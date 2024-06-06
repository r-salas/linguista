#
#
#   Cannot handle
#
#

from ..actions import Reply, action
from ..flow import Flow


class CannotHandle(Flow):

    @property
    def name(self):
        return "INTERNAL_CANNOT_HANDLE"

    @property
    def description(self):
        return "Cannot handle flow"

    @action
    def start(self):
        # FIXME: get reason and return according to that
        return Reply("I'm sorry, I cannot handle that request. Is there something else I can help you with?")
