from __future__ import annotations

"""Deploy JSON5 source assets into JSON data files for each SpaceTrucker mod.

Run this script from the ``src`` directory. Each valid JSON5 file must declare an
``Asset`` name and may include one or more supported Ostranauts data-folder keys.
The script writes each supported section as ``<Asset>.json`` under every sibling
mod's ``data/<folder>`` directory.

NOTE: JSON5 is used for the master records but will be converted to strict JSON
for deployment for compatibility.
"""

import json
from pathlib import Path

import json5

# Sibling directories that contain source material rather than deployable mod data.
EXCLUDED_FOLDERS = {"src", "readme_assets"}

"""Valid top-level JSON5 keys that correspond to Ostranauts data directories.

Note that the ``Asset`` key is used to name the output file and is not a 
mod data folder itself."""
DATAFOLDERS = [
    "Asset",
    "gasrespires",
    "guipropmaps",
    "headlines",
    "homeworlds",
    "info",
    "installables",
    "interaction_overrides",
    "interactions",
    "items",
    "jobitems",
    "jobs",
    "ledgerdefs",
    "lifeevents",
    "lights",
    "loot",
    "manpages",
    "market",
    "music",
    "music_stations",
    "names_first",
    "names_full",
    "names_last",
    "names_robots",
    "names_ship",
    "names_ship_adjectives",
    "names_ship_nouns",
    "parallax",
    "pda_apps",
    "personspecs",
    "pledges",
    "plot_beat_overrides",
    "plot_beats",
    "plot_manager",
    "plots",
    "powerinfos",
    "racing",
    "rooms",
    "schemas",
    "ships",
    "shipspecs",
    "slot_effects",
    "slots",
    "star_systems",
    "strings",
    "tickers",
    "tips",
    "tokens",
    "traitscores",
    "transit",
    "tsv",
    "wounds",
    "zone_triggers",
    "ads",
    "ai_training",
    "archived_content",
    "attackmodes",
    "audioemitters",
    "blueprints",
    "careers",
    "chargeprofiles",
    "colors",
    "conditions",
    "conditions_simple",
    "condowners",
    "condrules",
    "condtrigs",
    "context",
    "cooverlays",
    "crewskins",
    "crime",
    "explosions",
]


def find_json5_files(directory: Path) -> list[Path]:
    """Return recursively discovered JSON5 source files that pass validation.

    Invalid files are reported to the console and intentionally omitted from the
    deployment set, allowing the remaining assets to deploy.
    """
    result: list[Path] = []

    for file in directory.iterdir():
        if file.is_file() and file.suffix == ".json5":
            if validate_json5_file(file, report=True):
                result.append(file)
        elif file.is_dir():
            result.extend(find_json5_files(file))

    return result


def find_mod_folders(directory: Path) -> list[Path]:
    """Return immediate child directories that receive generated mod data."""
    result: list[Path] = []

    for folder in directory.iterdir():
        if folder.is_dir() and folder.name not in EXCLUDED_FOLDERS:
            result.append(folder)

    return result


def validate_json5_file(file_path: Path, report: bool = True) -> bool:
    """Validate the required asset identifier and optionally report data sections."""
    with open(file_path, "r", encoding="utf-8") as file:
        data = json5.load(file)
        asset_name = data.get("Asset")
        if not asset_name or not isinstance(asset_name, str):
            print(
                f"File {file_path.stem} is missing the 'Asset' key or it is not a string (found {asset_name})."
            )
            return False

    if report:
        # Report which of the DATAFOLDERS keys are present in the file
        present_keys = [key for key in DATAFOLDERS if key in data]
        print(
            f"File {file_path.stem} contains the following DATAFOLDERS keys:"
        )
        for key in present_keys:
            print(f" - {key}")

    return True


def get_json5_data(file_path: Path) -> dict:
    """Load only the supported data-folder sections from a JSON5 source asset."""
    with open(file_path, "r", encoding="utf-8") as file:
        data = json5.load(file)

    return {key: value for key, value in data.items() if key in DATAFOLDERS}


def deploy_to_data_folders(
    json5_files: list[Path],
    mod_folders: list[Path],
    asset_names: str | list[str] | None = None,
) -> None:
    """Write selected source asset sections as indented JSON to every target mod.

    Optionally pass asset name or list of asset names to restrict deployment.
    Output stays strict JSON rather than JSON5 for compatibility.
    """
    selected_asset_names = (
        {asset_names} if isinstance(asset_names, str) else set(asset_names or [])
    )

    for file in json5_files:
        data = get_json5_data(file)
        asset_name = data.get("Asset")
        if selected_asset_names and asset_name not in selected_asset_names:
            continue

        for key, value in data.items():
            if key == "Asset":
                continue

            for mod_folder in mod_folders:
                output_folder = mod_folder / "data" / key
                output_folder.mkdir(parents=True, exist_ok=True)
                output_file = output_folder / f"{asset_name}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(value, f, indent=4)
                print(f"Wrote {output_file}")


def main() -> None:
    """Discover source assets and sibling mods, then deploy all valid sections."""
    print("\n")

    current_directory = Path.cwd()
    mod_folders = find_mod_folders(current_directory.parent)
    print(f"\nFound {len(mod_folders)} mod folders:")
    for folder in mod_folders:
        print(f" - {folder}")
    print("\n")

    json5_files = find_json5_files(current_directory)

    assets_to_deploy = None
    # assets_to_deploy = ["Boots"]
    deploy_to_data_folders(json5_files, mod_folders, assets_to_deploy)

    print("\n")


if __name__ == "__main__":
    main()
