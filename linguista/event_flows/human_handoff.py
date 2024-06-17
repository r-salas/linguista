#
#
#   Human Handoff
#
#

from .base import EventFlow
from ..actions import action, Reply


class HumanHandoff(EventFlow):

    name = "INTERNAL_HUMAN_HANDOFF"

    description = "Human handoff flow"

    @action
    def start(self):
        return Reply("I understand you want to be connected to a human agent, "
                     "but that's something I cannot help you with at the moment. "
                     "Is there something else I can help you with?")
