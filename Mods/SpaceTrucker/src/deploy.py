from __future__ import annotations

import json  # ensure old JSON for compatibility
from pathlib import Path

import json5  # using json5 for master source data

EXCLUDED_FOLDERS = {"src", "readme_assets"}

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

# General Helpers


def find_json5_files(directory: Path) -> list[Path]:
    result: list[Path] = []

    # Include validate_json5_file function here so that only valid JSON5 files are returned
    for file in directory.iterdir():
        if file.is_file() and file.suffix == ".json5":
            if validate_json5_file(file, report=True):
                result.append(file)
        elif file.is_dir():
            result.extend(find_json5_files(file))

    return result


def find_mod_folders(directory: Path) -> list[Path]:
    result: list[Path] = []

    for folder in directory.iterdir():
        if folder.is_dir() and folder.name not in EXCLUDED_FOLDERS:
            result.append(folder)

    return result


# Source JSON5 File Helpers
def validate_json5_file(file_path: Path, report: bool = True) -> bool:
    # First check for the "Asset" key and that the value is a simple string. Return false early
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
        print(f"File {file_path.stem} contains the following DATAFOLDERS keys:")
        for key in present_keys:
            print(f" - {key}")

    return True

def get_json5_data(file_path: Path) -> dict:
    # Read the JSON5 file and return data who's keys match the DataFolders enum values
    with open(file_path, "r", encoding="utf-8") as file:
        data = json5.load(file)

    return {key: value for key, value in data.items() if key in DATAFOLDERS}


# Target JSON (OLD for compatibility) File Helpers
def deploy_to_data_folders(
    json5_files: list[Path], mod_folders: list[Path]
) -> None:
    # For each key in the data except for "Asset" write a JSON(OLD for compatibility) file
    # with the name that is the value of "Asset" and the extension ".json" in each of the mod
    # folders +/data/<key>/
    for file in json5_files:
        data = get_json5_data(file)
        asset_name = data.get("Asset")

        for key, value in data.items():
            if key == "Asset":
                continue

            for mod_folder in mod_folders:
                output_folder = mod_folder / "data" / key
                output_folder.mkdir(parents=True, exist_ok=True)
                output_file = output_folder / f"{asset_name}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(
                        value, f, indent=4
                    )  # ensure old JSON for compatibility
                print(f"Wrote {output_file}")


def main() -> None:
    print("\n")

    current_directory = Path.cwd()
    mod_folders = find_mod_folders(current_directory.parent)
    # TEST Mod Folders
    print(f"\nFound {len(mod_folders)} mod folders:")
    for folder in mod_folders:
        print(f" - {folder}")
    print("\n")

    json5_files = find_json5_files(current_directory)

    deploy_to_data_folders(json5_files, mod_folders)

    print("\n")


if __name__ == "__main__":
    main()
