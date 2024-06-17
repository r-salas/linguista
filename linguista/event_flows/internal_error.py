#
#
#   Internal error
#
#

from ..actions import Reply, action
from .base import EventFlow


class InternalError(EventFlow):

    name = "INTERNAL_ERROR"

    description = "Internal error flow"

    @action
    def start(self):
        return Reply("I'm sorry, I'm experiencing some technical difficulties. Please try again later.")
