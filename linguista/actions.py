#
#
#   Actions
#
#
from functools import wraps
from typing import Optional

from .flow import FlowSlot


def action(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


class Action:

    ...


class Ask(Action):

    def __init__(self, slot: FlowSlot, prompt: Optional[str] = None, id: Optional[str] = None):
        self.slot = slot
        self.prompt = prompt
        self.id = id

    def __rshift__(self, other):
        ...

    def __repr__(self):
        return f"Ask({self.slot}, prompt='{self.prompt}', id='{self.id}')"
