#
#
#   Actions
#
#

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Optional, Sequence, List

import dacite

from .flow import FlowSlot


def action(func):
    """
    Decorator to create an action from a function
    """
    return ActionFunction(func)


@dataclass(frozen=True)
class Action:

    @staticmethod
    def from_dict(cls, data: dict):
        action_subclasses = cls.__subclasses__()
        action_cls = next((action_cls for action_cls in action_subclasses if action_cls.__name__ == data["type"]), None)

        if action_cls is None:
            raise ValueError(f"Invalid action type: {data['type']}")

        action = action_cls.from_dict(data["action"])

        return action

    def __rshift__(self, other):
        return ChainAction([self, other])


@dataclass(frozen=True)
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

        object.__setattr__(self, 'actions', new_actions)

    def __rshift__(self, other):
        return ChainAction(self.actions + [other])

    @staticmethod
    def from_dict(cls, data: dict):
        raise NotImplementedError()

    def to_dict(self):
        raise NotImplementedError()


@dataclass(frozen=True)
class ActionFunction(Action):

    func: callable

    @classmethod
    def from_dict(cls, data: dict):
        ...  # FIXME: Implement this

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "action": {
                "func": {
                    "name": self.func.__name__
                }
            }
        }


@dataclass(frozen=True)
class Ask(Action):

    slot: FlowSlot
    prompt: Optional[str] = None

    @staticmethod
    def from_dict(cls, data: dict):
        slot = FlowSlot.from_dict(data["slot"])
        prompt = data.get("prompt")

        return Ask(slot=slot, prompt=prompt)

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "action": {
                "slot": self.slot.to_dict(),
                "prompt": self.prompt
            }
        }


@dataclass(frozen=True)
class CallFlow(Action):

    flow_name: str

    @staticmethod
    def from_dict(cls, data: dict):
        return CallFlow(flow_name=data["flow_name"])

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "action": {
                "flow_name": self.flow_name
            }
        }


@dataclass(frozen=True)
class Reply(Action):

    message: str

    @staticmethod
    def from_dict(cls, data: dict):
        return Reply(message=data["message"])

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "action": {
                "message": self.message
            }
        }


@dataclass(frozen=True)
class End(Action):

    @staticmethod
    def from_dict(cls, data: dict):
        return End()

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "action": {}
        }
