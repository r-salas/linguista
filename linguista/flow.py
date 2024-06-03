#
#
#   Flow
#
#

import inspect
from abc import ABC, abstractmethod

from .tracker import Tracker
from .types import Categorical


class FlowSlot:

    def __init__(self, name: str, description: str, type=str):
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

    def __init__(self, tracker: Tracker, session_id: str):
        self.tracker = tracker
        self.session_id = session_id

        self._slots = _get_slots_from_flow(self)
        self._slot_values = {slot.name: None for slot in self._slots}

        initial_values = tracker.get_flow_slots(session_id, self.name)

        for slot_name, slot_value in initial_values.items():
            self._slot_values[slot_name] = slot_value

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
        return self._slots

    def set_slot_value(self, slot: FlowSlot, value):
        self._slot_values[slot.name] = value
        self.tracker.update_flow_slot(self.session_id, self.name, slot.name, value)

    def get_slot_value(self, slot: FlowSlot):
        return self._slot_values.get(slot.name)

    def next(self, *actions):
        ...

    def __repr__(self):
        return f"Flow(name='{self.name}', description='{self.description}', slots={self._slots})"


def _get_slots_from_flow(flow: Flow):
    return_slots = set()
    slots_members = inspect.getmembers(flow, lambda attr: isinstance(attr, FlowSlot))

    for slot_var_name, flow_slot in slots_members:
        return_slots.add(flow_slot)

    return return_slots
