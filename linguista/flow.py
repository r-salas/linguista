#
#
#   Flow
#
#

import copy
import inspect

from abc import ABC, abstractmethod
from typing import Optional

from .bot import Bot
from .types import Categorical


class FlowSlot:

    def __init__(self, description: str, type=str, name: Optional[str] = None):
        self.name = name
        self.description = description
        self.type = type

        assert type in {int, bool, str, float} or isinstance(type, Categorical), f"Invalid type: {type}"

    def __repr__(self):
        return f"FlowSlot(name='{self.name}', description='{self.description}', type={self.type})"


class Flow(ABC):
    """
    Base class for conversational flows.
    """

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
    def start(self, bot: Bot):
        """
        Start the flow.

        Args:
            bot: The bot instance.

        Returns:
            The first action of the flow.
        """
        pass

    def get_slot(self, slot_name: str):
        slot = getattr(self, slot_name, None)

        if slot is None:
            return None

        if not isinstance(slot, FlowSlot):
            raise ValueError(f"Invalid slot name: {slot_name}")

        if slot.name is None:
            slot = copy.deepcopy(slot)
            slot.name = slot_name

        return slot

    def get_slots(self):
        slots = _get_slots_from_flow(self)
        return slots

    def __repr__(self):
        slots = _get_slots_from_flow(self)
        return f"Flow(name='{self.name}', description='{self.description}', slots={slots})"


def _get_slots_from_flow(flow: Flow):
    return_slots = []
    slots_members = inspect.getmembers(flow, lambda attr: isinstance(attr, FlowSlot))

    for slot_name, flow_slot in slots_members:

        if flow_slot.name is None:
            flow_slot = copy.deepcopy(flow_slot)
            flow_slot.name = slot_name

        return_slots.append(flow_slot)

    return return_slots
