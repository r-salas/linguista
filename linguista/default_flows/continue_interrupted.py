#
#
#   Continue interrupted flow
#
#

from ..actions import Reply, action
from ..flow import Flow


class ContinueInterrupted(Flow):

    @property
    def name(self):
        return "INTERNAL_CONTINUE_INTERRUPTED"

    @property
    def description(self):
        return "Continue interrupted flow"

    @action
    def start(self):
        return Reply("Let's continue from where we left off.")
