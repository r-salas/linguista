#
#
#   Flow
#
#

import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, Union

from .tracker import Tracker
from .types import Categorical


@dataclass
class FlowSlot:

    name: str
    description: str
    type: Union[Type, Categorical]
    ask_before_filling: bool = True


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

    def __repr__(self):
        return f"Flow(name='{self.name}', description='{self.description}', slots={self.get_slots()})"


def _get_slots_from_flow(flow: Flow):
    return_slots = set()
    slots_members = inspect.getmembers(flow, lambda attr: isinstance(attr, FlowSlot))

    for slot_var_name, flow_slot in slots_members:
        return_slots.add(flow_slot)

    return return_slots
