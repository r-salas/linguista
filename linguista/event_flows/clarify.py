#
#
#   Clarify
#
#

from .base import EventFlow
from ..actions import Reply, action


class Clarify(EventFlow):

    name = "INTERNAL_CLARIFY"

    description = "Clarify flow"

    @action
    def start(self):
        return Reply("I'm sorry, I'm not sure what you mean by that. Can you please rephrase your question?")
