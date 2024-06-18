#
#
#   Proxy
#
#

from typing import Any

from ..flow import Flow
from ..flow_slot import FlowSlot
from ..utils import strtobool


class ProxyTracker:

    def __init__(self, tracker, session_id: str, current_flow: Flow):
        self.tracker = tracker
        self.session_id = session_id
        self.current_flow = current_flow

        self.session = SessionProxyTracker(tracker, session_id)

    def get_slot(self, slot: FlowSlot):
        value = self.tracker.get_flow_slot(self.session_id, self.current_flow.name, slot.name)

        if value is None:
            return None

        if slot.type == bool:
            return strtobool(value)
        elif slot.type == int:
            return int(value)
        elif slot.type == float:
            return float(value)
        else:
            return value

    def set_slot(self, slot: FlowSlot, value: Any):
        self.tracker.set_flow_slot(self.session_id, self.current_flow.name, slot.name, value)


class SessionProxyTracker:

    def __init__(self, tracker, session_id: str):
        self.tracker = tracker
        self.session_id = session_id

    def get_slot(self, name: str):
        ...  # I don't really like that you need a FlowSlot object for a flow alot but here you need a string

    def set_slot(self, name: str, value):
        ...
