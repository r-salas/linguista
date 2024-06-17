#
#
#   Continue interrupted flow
#
#

from ..actions import Reply, action
from .base import EventFlow


class ContinueInterrupted(EventFlow):

    name = "INTERNAL_CONTINUE_INTERRUPTED"

    description = "Continue interrupted flow"

    @action
    def start(self):
        return Reply("Let's continue from where we left off.")
