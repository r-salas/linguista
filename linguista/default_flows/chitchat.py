#
#
#   Chitchat flow
#
#
from .. import action
from ..actions import Reply
from ..flow import InternalFlow


class Chitchat(InternalFlow):

    @property
    def name(self):
        return "INTERNAL_CHITCHAT"

    @property
    def description(self):
        return "Chitchat flow"

    @action
    def start(self):
        return Reply("I'm sorry, I'm not sure what you mean by that. Can you please rephrase your question?")
