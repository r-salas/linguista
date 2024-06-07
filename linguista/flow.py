#
#
#   Flow
#
#

import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Type, Union

from .tracker import Tracker
from .types import Categorical


@dataclass(frozen=True)
class FlowSlot:

    name: str
    description: str
    type: Union[Type, Categorical]
    ask_before_filling: bool = True

    @staticmethod
    def from_dict(data: dict):
        if data["type"]["type"] == "categorical":
            slot_type = Categorical(data["type"]["categories"])
        else:
            slot_type_name_to_type = {
                "number": int,
                "boolean": bool,
                "str": str
            }
            slot_type = slot_type_name_to_type[data["type"]]

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


class Flow(ABC):
    """
    Base class for conversational flows.
    """

    def __init__(self, tracker: Tracker, session_id: str):
        self.tracker = tracker
        self.session_id = session_id

    @property
    @abstractmethod
    def name(self):
        """
        The name of the flow.
        """
        pass

    @property
    @abstractmethod
    def description(self):
        """
        A description of the flow.
        """
        pass

    @abstractmethod
    def start(self):
        """
        Start the flow.

        Returns:
            The first action of the flow.
        """
        pass

    def get_slots(self):
        return _get_slots_from_flow(self)

    def get_slot(self, slot_name):
        for slot in self.get_slots():
            if slot.name == slot_name:
                return slot

        return None

    def __repr__(self):
        return f"Flow(name='{self.name}', description='{self.description}', slots={self.get_slots()})"


def _get_slots_from_flow(flow: Flow):
    return_slots = set()
    slots_members = inspect.getmembers(flow, lambda attr: isinstance(attr, FlowSlot))

    for slot_var_name, flow_slot in slots_members:
        return_slots.add(flow_slot)

    return return_slots
