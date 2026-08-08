from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any

import json5  # type: ignore # FOR JSON with comments and trailing commas
from character_data import CharacterData

CHARACTER_SCHEMA = Path(__file__).parent / "character-schema.json"

local_low = Path.home() / "AppData" / "LocalLow"
SAVE_DIRECTORY = local_low / "Blue Bottle Games" / "Ostranauts" / "Saves"
SAVE_NAME = "klarke_start" # For testing


def extract_save_info(save_info_file: Path) -> tuple[str, str]:
    """Return the player name and registered ship ID recorded in a save."""
    with save_info_file.open("r", encoding="utf-8") as save_file:
        save_info = json5.load(save_file)

    if not isinstance(save_info, list) or not save_info:
        raise ValueError(f"{save_info_file} must contain a non-empty array.")

    first_entry = save_info[0]
    if not isinstance(first_entry, dict):
        raise TypeError(f"The first entry in {save_info_file} must be an object.")

    player_name = first_entry.get("playerName")
    ship_reg_id = first_entry.get("shipRegID")
    if not isinstance(player_name, str) or not isinstance(ship_reg_id, str):
        raise TypeError(f"{save_info_file} is missing playerName or shipRegID.")

    return player_name, ship_reg_id


def extract_ship_file_from_zip(save_zip_file: Path, ship_reg_id: str) -> dict[str, Any]:
    """Read the registered ship's JSON object from a save archive."""
    ship_file_name = f"{ship_reg_id}.json"
    with zipfile.ZipFile(save_zip_file) as save_archive:
        for archive_entry in save_archive.infolist():
            entry_path = Path(archive_entry.filename)
            if entry_path.parent.name == "ships" and entry_path.name == ship_file_name:
                with save_archive.open(archive_entry) as ship_file:
                    ship_data = json5.loads(ship_file.read().decode("utf-8"))
                if isinstance(ship_data, list) and len(ship_data) == 1:
                    ship_data = ship_data[0]
                if not isinstance(ship_data, dict):
                    raise ValueError(
                        f"Ship file {archive_entry.filename} must contain a ship object."
                    )
                return ship_data

    raise FileNotFoundError(f"Could not find ships/{ship_file_name} in {save_zip_file}.")


def _required_character_fields(character_schema: Path) -> set[str]:
    with character_schema.open("r", encoding="utf-8") as schema_file:
        schema = json.load(schema_file)

    required_fields = schema.get("items", {}).get("required")
    if not isinstance(required_fields, list) or not all(
        isinstance(field, str) for field in required_fields
    ):
        raise ValueError(f"{character_schema} does not define items.required as a string array.")

    return set(required_fields)


def extract_character_from_ship_data(
    ship_data: dict[str, Any], player_name: str, character_schema: Path | None = None
) -> CharacterData:
    """Return the full player character, optionally checking schema-required fields."""
    characters = ship_data.get("aCOs", ship_data.get("characters"))
    if not isinstance(characters, list):
        raise TypeError("The ship data does not contain an aCOs or characters array.")

    required_fields = (
        _required_character_fields(character_schema) if character_schema is not None else set()
    )
    for character in characters:
        if not isinstance(character, dict) or character.get("strID") != player_name:
            continue

        missing_fields = required_fields - character.keys()
        if missing_fields:
            field_list = ", ".join(sorted(missing_fields))
            raise ValueError(f"Character {player_name!r} is missing required fields: {field_list}.")
        return CharacterData.from_dict(character)

    raise LookupError(f"Could not find character {player_name!r} in the registered ship.")


def extract_character_from_save(
    save_directory: Path, character_schema: Path | None = None
) -> CharacterData:
    """Extract the player character from an Ostranauts save directory."""
    save_directory = Path(save_directory)
    player_name, ship_reg_id = extract_save_info(save_directory / "saveInfo.json")
    ship_data = extract_ship_file_from_zip(
        save_directory / f"{save_directory.name}.zip", ship_reg_id
    )
    return extract_character_from_ship_data(ship_data, player_name, character_schema)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract the player character from an Ostranauts save directory."
    )
    parser.add_argument(
        "save_directory",
        nargs="?",
        type=Path,
        default=SAVE_DIRECTORY / SAVE_NAME,
        help="Save directory to extract; defaults to the configured test save.",
    )
    parser.add_argument("--schema", type=Path, help="Validate against this character schema.")
    arguments = parser.parse_args()

    character = extract_character_from_save(arguments.save_directory, arguments.schema)

    print(json.dumps(character.aFaceParts, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()