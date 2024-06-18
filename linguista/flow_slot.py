#
#
#   Flow Slot
#
#

from dataclasses import dataclass
from typing import Type, Union

from .types import Categorical
from .utils import strtobool


@dataclass(frozen=True)
class FlowSlot:
    name: str
    description: str
    type: Union[Type, Categorical]
    ask_before_filling: bool = True

    def __post_init__(self):
        valid_types = [int, float, bool, str]
        assert isinstance(self.type, Categorical) or self.type in valid_types, f"Invalid slot type: {self.type}"

    @staticmethod
    def from_dict(data: dict):
        if data["type"]["type"] == "categorical":
            slot_type = Categorical(data["type"]["categories"])
        else:
            slot_type_name_to_type = {
                "int": int,
                "float": float,
                "bool": bool,
                "str": str
            }
            assert data["type"]["type"] in slot_type_name_to_type, f"Invalid slot type: {data['type']['type']}"
            slot_type = slot_type_name_to_type[data["type"]["type"]]

        return FlowSlot(
            name=data["name"],
            description=data["description"],
            type=slot_type,
            ask_before_filling=data["ask_before_filling"]
        )

    def to_dict(self):
        if isinstance(self.type, Categorical):
            type_json = {
                "type": "categorical",
                "categories": self.type.categories
            }
        else:
            type_json = {
                "type": self.type.__name__
            }

        return {
            "name": self.name,
            "description": self.description,
            "type": type_json,
            "ask_before_filling": self.ask_before_filling
        }
