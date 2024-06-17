#
#
#   Cannot handle
#
#

from ..actions import Reply, action
from .base import EventFlow


class CannotHandle(EventFlow):

    name = "INTERNAL_CANNOT_HANDLE"

    description = "Cannot handle flow"

    @action
    def start(self):
        # FIXME: get reason and return according to that
        return Reply("I'm sorry, I cannot handle that request. Is there something else I can help you with?")
