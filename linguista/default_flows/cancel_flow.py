#
#
#   Cancel Flow
#
#

from ..actions import Reply, action
from ..flow import Flow


class CancelFlow(Flow):

    @property
    def name(self):
        return "INTERNAL_CANCEL_FLOW"

    @property
    def description(self):
        return "Cancel flow"

    @action
    def start(self):
        flow_name = ...   # TODO: get the name of the flow to cancel
        return Reply(f"Okay, stopping {flow_name}.")
