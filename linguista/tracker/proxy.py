#
#
#   Proxy
#
#

from typing import Any

from ..flow import Flow
from ..flow_slot import FlowSlot
from ..utils import strtobool, extract_digits


class ProxyTracker:

    def __init__(self, tracker, session_id: str, current_flow: Flow):
        self.tracker = tracker
        self.session_id = session_id
        self.current_flow = current_flow

        self.session = SessionProxyTracker(tracker, session_id)

    def get_slot(self, slot: FlowSlot):
        value_str = self.tracker.get_flow_slot(self.session_id, self.current_flow.name, slot.name)

        if value_str is None:
            return None

        # Convert the value to the correct type
        if slot.type == int:
            value_str_digits = extract_digits(value_str)
            return int(value_str_digits)
        elif slot.type == float:
            value_str_digits = extract_digits(value_str)
            return float(value_str_digits)
        elif slot.type == bool:
            return strtobool(value_str)
        else:
            return value_str

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
