#
#
#   Cancel Flow
#
#

from ..actions import Reply, action
from .base import EventFlow


class CancelFlow(EventFlow):

    name = "INTERNAL_CANCEL_FLOW"

    description = "Cancel flow"

    @action
    def start(self):
        flow_name = ...   # TODO: get the name of the flow to cancel
        return Reply(f"Okay, I will cancel the process.")
