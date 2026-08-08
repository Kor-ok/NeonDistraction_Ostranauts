from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field, fields
from typing import Any, TypeAlias

CharacterJsonObj: TypeAlias = dict[str, Any]
ConditionValue: TypeAlias = int | float # Accounting for Ostranauts values e.g. 1.0x0.3995 or 1.0x3 or 1x0.2 etc, being permutations of int and float, but always two values separated by 'x'
CharacterCondition: TypeAlias = tuple[str, tuple[ConditionValue, ConditionValue]]


@dataclass
class CharacterData:
	"""Schema-shaped representation of a character object from a ship's ``aCOs`` array."""

	strID: str
	strCODef: str
	bAlive: bool
	aConds: list[str]
	aCondRules: list[str]
	strCondID: str
	inventoryX: float
	inventoryY: float
	aMessages2: list[CharacterJsonObj]
	fDGasTemp: float
	fLastICOUpdate: float
	aAttackIAs: list[str]
	nDestTile: float
	strDestCO: str
	strDestShip: str
	strIdleAnim: str
	strBodyType: str
	aFaceParts: list[str]
	dictRecentlyTried: CharacterJsonObj
	aRememberIAs: list[str]
	cgs: CharacterJsonObj
	social: CharacterJsonObj
	aTickers: list[CharacterJsonObj]
	aPledges: list[CharacterJsonObj]
	aFactions: list[str]
	strComp: str
	strFriendlyName: str
	strRegIDLast: str
	fMSRedamageAmount: float
	mapIAHist2: list[CharacterJsonObj]
	aMyShips: list[str] = field(default_factory=list)
	extra: CharacterJsonObj = field(default_factory=dict, repr=False)

	@staticmethod
	def parse_condition(condition: str) -> CharacterCondition | None:
		"""Parse an ``aConds`` entry such as ``StatAge=1.0x18``."""
		if "=" not in condition:
			return None

		name, raw_values = condition.split("=", 1)
		values = raw_values.split("x")
		if not name or len(values) != 2:
			return None

		try:
			parsed_values = tuple(
				float(value) if any(marker in value for marker in ".eE") else int(value)
				for value in values
			)
		except ValueError:
			return None

		return name, (parsed_values[0], parsed_values[1])

	@staticmethod
	def format_condition(condition: CharacterCondition) -> str:
		"""Format a parsed condition back to the JSON representation used by ``aConds``."""
		name, values = condition
		return f"{name}={values[0]}x{values[1]}"

	@property
	def conditions(self) -> list[CharacterCondition]:
		"""Return the valid parsed entries from the raw ``aConds`` JSON field."""
		return [
			condition
			for raw_condition in self.aConds
			if (condition := self.parse_condition(raw_condition)) is not None
		]

	@classmethod
	def from_dict(cls, character: Mapping[str, Any]) -> CharacterData:
		"""Create character data from one object in a ship's ``aCOs`` array."""
		if not isinstance(character, Mapping):
			raise TypeError("Character data must be a mapping.")

		known_fields = {field_info.name for field_info in fields(cls)} - {"extra"}
		missing_fields = sorted(
			field_name
			for field_name in known_fields - {"aMyShips"}
			if field_name not in character
		)
		if missing_fields:
			raise ValueError(
				f"Character data is missing required fields: {', '.join(missing_fields)}."
			)

		values = {
			field_name: character[field_name]
			for field_name in known_fields
			if field_name in character
		}
		values["extra"] = {
			field_name: value
			for field_name, value in character.items()
			if field_name not in known_fields
		}
		return cls(**values)

	def to_dict(self) -> CharacterJsonObj:
		"""Return a JSON-serializable character object, including unknown source fields."""
		character = asdict(self)
		extra = character.pop("extra")
		return {**extra, **character}

	def get_appearance(self) -> CharacterJsonObj:
		"""Return the character's appearance-related fields."""
		return {"strBodyType": self.strBodyType, "aFaceParts": self.aFaceParts}