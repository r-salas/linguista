#
#
#   Actions
#
#

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence, List

from .flow import FlowSlot


def action(func):
    """
    Decorator to create an action from a function
    """
    return ActionFunction(func)


@dataclass
class Action(ABC):

    def __rshift__(self, other):
        return ChainAction([self, other])


@dataclass
class ChainAction(Action):

    actions: List[Action]

    def __post_init__(self):
        # Flatten the actions
        new_actions = []
        for action_instance in self.actions:
            if isinstance(action_instance, ChainAction):
                new_actions.extend(action_instance.actions)
            else:
                new_actions.append(action_instance)

        self.actions = new_actions

    def __rshift__(self, other):
        return ChainAction(self.actions + [other])


@dataclass
class ActionFunction(Action):

    func: callable

    def __call__(self, *args, **kwargs):
        flow = self.func.__self__
        return self.func(flow, *args, **kwargs)


@dataclass
class Ask(Action):

    slot: FlowSlot
    prompt: Optional[str] = None


@dataclass
class CallFlow(Action):

    flow_name: str


@dataclass
class Reply(Action):

    message: str


@dataclass
class End(Action):
    pass
