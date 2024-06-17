#
#
#   Skip question flow
#
#

from ..actions import Reply, action
from .base import EventFlow


class SkipQuestion(EventFlow):

    name = "INTERNAL_SKIP_QUESTION"

    description = "Skip question flow"

    @action
    def start(self):
        return Reply("I'm here to provide you with the best assistance, and in order to do so, I kindly request that "
                     "we complete this step together. Your input is essential for a seamless experience!")
