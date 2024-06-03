#
#
#   Actions
#
#

from typing import Optional, Sequence

from .flow import FlowSlot


def action(func):
    return ActionFunction(func)


class Action:

    def __rshift__(self, other):
        return ChainAction([self, other])


class ChainAction(Action):

    def __init__(self, actions):
        self.actions = []
        for action_or_chain in actions:
            if isinstance(action_or_chain, ChainAction):
                self.actions.extend(action_or_chain.actions)
            else:
                self.actions.append(action_or_chain)

    def __rshift__(self, other):
        return ChainAction(self.actions + [other])

    def __repr__(self):
        return f"Chain({self.actions})"


class ActionFunction(Action):

    def __init__(self, func):
        self.func = func

    def __repr__(self):
        return f"ActionFunction(func={self.func})"


class Ask(Action):

    def __init__(self, slot: FlowSlot, prompt: Optional[str] = None, next: Optional[Action | Sequence[Action]] = None):
        self.slot = slot
        self.prompt = prompt
        self.next = next

    def __repr__(self):
        return f"Ask({self.slot}, prompt='{self.prompt}')"


class CallFlow(Action):

    def __init__(self, flow_name: str):
        self.flow_name = flow_name

    def __repr__(self):
        return f"CallFlow({self.flow_name})"
