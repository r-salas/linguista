#
#
#   Clarify
#
#

from ..flow import Flow
from ..actions import Reply, action


class Clarify(Flow):

    @property
    def name(self):
        return "INTERNAL_CLARIFY"

    @property
    def description(self):
        return "Clarify flow"

    @action
    def start(self):
        return Reply("I'm sorry, I'm not sure what you mean by that. Can you please rephrase your question?")
