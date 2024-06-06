#
#
#   Chitchat flow
#
#

from ..actions import Reply, action
from ..flow import Flow


class Chitchat(Flow):

    @property
    def name(self):
        return "INTERNAL_CHITCHAT"

    @property
    def description(self):
        return "Chitchat flow"

    @action
    def start(self):
        return Reply("I'm sorry, I'm not sure what you mean by that. Can you please rephrase your question?")
