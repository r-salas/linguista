#
#
#   Human Handoff
#
#

from ..flow import Flow
from ..actions import action, Reply


class HumanHandoff(Flow):

    @property
    def name(self):
        return "INTERNAL_HUMAN_HANDOFF"

    @property
    def description(self):
        return "Human handoff flow"

    @action
    def start(self):
        return Reply("I understand you want to be connected to a human agent, "
                     "but that's something I cannot help you with at the moment. "
                     "Is there something else I can help you with?")
