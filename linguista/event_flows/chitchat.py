#
#
#   Chitchat flow
#
#

from ..actions import Reply, action
from .base import EventFlow


class ChitChat(EventFlow):

    name = "INTERNAL_CHITCHAT"

    description = "Chitchat flow"

    @action
    def start(self):
        return Reply("I'm sorry, I'm not sure what you mean by that. Can you please rephrase your question?")
