#
#
#   Actions
#
#

from dataclasses import dataclass
from typing import Optional, List, Union

from .flow_slot import FlowSlot


def action(func):
    """
    Decorator to create an action from a function
    """
    return ActionFunction(func)


@dataclass(frozen=True)
class Action:

    @classmethod
    def from_dict(cls, data: dict):
        action_subclasses = cls.__subclasses__()
        action_cls = next((action_cls for action_cls in action_subclasses if action_cls.__name__ == data["type"]), None)

        if action_cls is None:
            raise ValueError(f"Invalid action type: {data['type']}")

        action = action_cls.from_dict(data["action"])

        return action

    def __rshift__(self, other):
        return ChainAction([self, other])

    def to_dict(self):
        raise NotImplementedError()


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

    @classmethod
    def from_dict(cls, data: dict):
        raise NotImplementedError()

    def to_dict(self):
        raise NotImplementedError()


@dataclass(frozen=True)
class ActionFunction(Action):
    function: Union[str, callable]  # it may be a string with the function name

    @classmethod
    def from_dict(cls, data: dict):
        return ActionFunction(function=data["function"])

    def to_dict(self):
        if isinstance(self.function, str):
            function_name = self.function
        else:
            function_name = self.function.__name__

        return {
            "type": self.__class__.__name__,
            "action": {
                "function": function_name
            }
        }


@dataclass(frozen=True)
class Ask(Action):
    slot: FlowSlot
    prompt: Optional[str] = None

    @classmethod
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

    @classmethod
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

    @classmethod
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

    @classmethod
    def from_dict(cls, data: dict):
        return End()

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "action": {}
        }
