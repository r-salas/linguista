#
#
#   Flow
#
#

import inspect
from abc import ABC, abstractmethod

from .flow_slot import FlowSlot


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
