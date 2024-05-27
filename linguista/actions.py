#
#
#   Actions
#
#
from functools import wraps
from typing import Optional

from .flow import FlowSlot


def action(id: Optional[str] = None):
    def wrapper(func):
        action_id = id or func.__name__
        return ActionFunction(func, id=action_id)
    return wrapper


class Action:

    def __init__(self, id: Optional[str] = None):
        self.id = id

    def __rshift__(self, other):
        return Chain([self, other])


class Chain:

    def __init__(self, actions):
        self.actions = actions

    def __rshift__(self, other):
        return Chain(self.actions + [other])

    def __repr__(self):
        return f"Chain({self.actions})"


class ActionFunction(Action):

    def __init__(self, func, id: Optional[str] = None):
        super().__init__(id)

        self.func = func

    def __repr__(self):
        return f"ActionFunction(func={self.func}, id='{self.id}')"


class Ask(Action):

    def __init__(self, slot: FlowSlot, prompt: Optional[str] = None, id: Optional[str] = None):
        super().__init__(id)

        self.slot = slot
        self.prompt = prompt

    def __repr__(self):
        return f"Ask({self.slot}, prompt='{self.prompt}', id='{self.id}')"


class Next(Action):

    def __init__(self, next_action_id: str, id: Optional[str] = None):
        super().__init__(id)

        self.next_action_id = next_action_id

    def __repr__(self):
        return f"Next(next_action_id='{self.next_action_id}', id='{self.id}')"
