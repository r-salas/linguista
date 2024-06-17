#
#
#   Correction flow
#
#

from ..actions import Reply, action
from .base import EventFlow


class Correction(EventFlow):

    name = "INTERNAL_CORRECTION"

    description = "Correction flow"

    @action
    def start(self):
        return Reply("Ok, I will update that.")
