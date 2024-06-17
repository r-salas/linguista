#
#
#   Completed
#
#

from ..actions import Reply, action
from .base import EventFlow


class Completed(EventFlow):

    name = "INTERNAL_COMPLETED"

    description = "Completed flow"

    @action
    def start(self):
        return Reply("Is there anything else I can help you with?")
