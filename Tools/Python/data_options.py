from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any

import json5

MOD_DIRECTORY = Path(r"D:\Apps\Steam\steamapps\common\Ostranauts\Ostranauts_Data\StreamingAssets\data")
ENUM_DIRECTORY = Path(r"D:\Projects\Ostranauts\Github\NeonDistraction_Ostranauts\schemas\enums")


class SUB_DIRECTORIES(Enum):
    GASRESPIRES = "gasrespires"
    GUIPROPMAPS = "guipropmaps"
    HEADLINES = "headlines"
    HOMEWORLDS = "homeworlds"
    INFO = "info"
    INSTALLABLES = "installables"
    INTERACTION_OVERRIDES = "interaction_overrides"
    INTERACTIONS = "interactions"
    ITEMS = "items"
    JOBITEMS = "jobitems"
    JOBS = "jobs"
    LEDGERDEFS = "ledgerdefs"
    LIFEEVENTS = "lifeevents"
    LIGHTS = "lights"
    LOOT = "loot"
    MANPAGES = "manpages"
    MARKET = "market"
    MUSIC = "music"
    MUSIC_STATIONS = "music_stations"
    NAMES_FIRST = "names_first"
    NAMES_FULL = "names_full"
    NAMES_LAST = "names_last"
    NAMES_ROBOTS = "names_robots"
    NAMES_SHIP = "names_ship"
    NAMES_SHIP_ADJECTIVES = "names_ship_adjectives"
    NAMES_SHIP_NOUNS = "names_ship_nouns"
    PARALLAX = "parallax"
    PDA_APPS = "pda_apps"
    PERSONSPECS = "personspecs"
    PLEDGES = "pledges"
    PLOT_BEAT_OVERRIDES = "plot_beat_overrides"
    PLOT_BEATS = "plot_beats"
    PLOT_MANAGER = "plot_manager"
    PLOTS = "plots"
    POWERINFOS = "powerinfos"
    RACING = "racing"
    ROOMS = "rooms"
    SCHEMAS = "schemas"
    SHIPS = "ships"
    SHIPSPECS = "shipspecs"
    SLOT_EFFECTS = "slot_effects"
    SLOTS = "slots"
    STAR_SYSTEMS = "star_systems"
    STRINGS = "strings"
    TICKERS = "tickers"
    TIPS = "tips"
    TOKENS = "tokens"
    TRAITSCORES = "traitscores"
    TRANSIT = "transit"
    TSV = "tsv"
    WOUNDS = "wounds"
    ZONE_TRIGGERS = "zone_triggers"
    ADS = "ads"
    AI_TRAINING = "ai_training"
    ARCHIVED_CONTENT = "archived_content"
    ATTACKMODES = "attackmodes"
    AUDIOEMITTERS = "audioemitters"
    BLUEPRINTS = "blueprints"
    CAREERS = "careers"
    CHARGEPROFILES = "chargeprofiles"
    COLORS = "colors"
    CONDITIONS = "conditions"
    CONDITIONS_SIMPLE = "conditions_simple"
    CONDOWNERS = "condowners"
    CONDRULES = "condrules"
    CONDTRIGS = "condtrigs"
    CONTEXT = "context"
    COOVERLAYS = "cooverlays"
    CREWSKINS = "crewskins"
    CRIME = "crime"
    EXPLOSIONS = "explosions"

OPTIONAL_SPECIFIC_FILE = Path(r"D:\Apps\Steam\steamapps\common\Ostranauts\Ostranauts_Data\StreamingAssets\data\condowners\condowners_plots.json")

def get_path(subdir: SUB_DIRECTORIES) -> Path:
    """Return the path to a subdirectory of the Ostranauts data directory."""
    return MOD_DIRECTORY / subdir.value

def extract_unique_keys_from_json_files(directory: Path) -> set[str]:
    """Extract unique keys from all JSON files in the specified directory."""
    unique_keys = set()
    for json_file in directory.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            try:
                data = json5.load(f)
                if isinstance(data, dict):
                    unique_keys.update(data.keys())
                elif isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, dict):
                            unique_keys.update(entry.keys())
            except (OSError, ValueError) as e:
                print(f"Error reading {json_file}: {e}")
    return unique_keys

def get_json_schema_type(value: object) -> str | None:
    """Return the JSON Schema type name for a JSON-compatible value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return None


def get_json_value_key(value: Any) -> str:
    """Return a stable key for comparing and ordering JSON-compatible values."""
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def extract_unique_values_from_specified_key(
    directory: Path, key: str, flatten_arrays: bool = False
) -> tuple[list[Any], set[str]]:
    """Extract unique JSON-compatible values and their JSON Schema types.

    Set ``flatten_arrays`` to collect each array element as an option instead of
    treating each complete array as an enum value.
    """
    unique_values: dict[str, Any] = {}
    unique_types: set[str] = set()

    def collect_value(value: object) -> None:
        if flatten_arrays and isinstance(value, list):
            for item in value:
                collect_value(item)
        else:
            schema_type = get_json_schema_type(value)
            if schema_type is None:
                print(f"Skipping unsupported value for '{key}': {value!r}")
                return
            unique_values[get_json_value_key(value)] = value
            unique_types.add(schema_type)

    for json_file in directory.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            try:
                data = json5.load(f)
                if isinstance(data, dict) and key in data:
                    collect_value(data[key])
                elif isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, dict) and key in entry:
                            collect_value(entry[key])
            except (OSError, ValueError) as e:
                print(f"Error reading {json_file}: {e}")
    return list(unique_values.values()), unique_types


def write_json_schema_enum(
    file_path: Path, enum_values: list[Any], type_values: set[str], title: str, search_key: str
) -> None:
    """Write a JSON Schema enum for scalar, array, and object values."""
    schema_simple = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": title,
        "type": sorted(type_values),
        "enum": sorted(enum_values, key=get_json_value_key),
    }
    schema_array = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": title,
        "type": "array",
        "items": {
            "type": sorted(type_values),
            "enum": sorted(enum_values, key=get_json_value_key),
        }
    }
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        # If the search-key starts with "a" or "map" then use schema_array
        if search_key.startswith(("a", "map")):
            json.dump(schema_array, f, indent=2)
        else:
            json.dump(schema_simple, f, indent=2)

def main() -> None:
    """Main function to extract unique keys from JSON files in the specified subdirectory."""

    subdir = SUB_DIRECTORIES.CONDOWNERS  
    directory_path = get_path(subdir)

    # print(f"Extracting unique keys from JSON files in {directory_path}...")
    # unique_keys = extract_unique_keys_from_json_files(directory_path)
    # print(f"Unique keys in {subdir.value}:")
    # for key in sorted(unique_keys):
    #     print(key)

    search_key = "mapGUIPropMaps"
    unique_values, unique_types = extract_unique_values_from_specified_key(
        directory_path, search_key, flatten_arrays=True
    )

    # print(f"Unique values for '{search_key}' in {subdir.value}:")
    # for value in sorted(unique_values, key=lambda x: str(x)):
    #     print(value)
    # print(f"Unique types for '{search_key}' in {subdir.value}:")
    # for t in sorted(unique_types, key=lambda x: str(x)):
    #     print(t)

    schema_filename = f"{subdir.value}-{search_key}-options.json"
    schema_path = Path(ENUM_DIRECTORY, schema_filename)
    schema_title = f"Values for {subdir.value}[].{search_key}"
    write_json_schema_enum(schema_path, unique_values, unique_types, schema_title, search_key=search_key)



if __name__ == "__main__":
    main()