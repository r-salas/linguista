#
#
#   Internal error
#
#

from ..actions import Reply, action
from ..flow import Flow


class InternalError(Flow):

    @property
    def name(self):
        return "INTERNAL_ERROR"

    @property
    def description(self):
        return "Internal error flow"

    @action
    def start(self):
        return Reply("I'm sorry, I'm experiencing some technical difficulties. Please try again later.")
