#
#
#   Completed
#
#

from ..actions import Reply, action
from ..flow import Flow


class Completed(Flow):

    @property
    def name(self):
        return "INTERNAL_COMPLETED"

    @property
    def description(self):
        return "Completed flow"

    @action
    def start(self):
        return Reply("Is there anything else I can help you with?")
