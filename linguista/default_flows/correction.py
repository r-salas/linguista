#
#
#   Correction flow
#
#

from ..actions import Reply, action
from ..flow import Flow


class Correction(Flow):

    @property
    def name(self):
        return "INTERNAL_CORRECTION"

    @property
    def description(self):
        return "Correction flow"

    @action
    def start(self):
        return Reply("Ok, I will update that.")
