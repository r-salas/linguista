#
#
#   Clarify
#
#

from dataclasses import dataclass
from typing import Sequence


@dataclass(init=False)
class ClarifyCommand:
    flows: Sequence[str]

    def __init__(self, *flows: Sequence[str]):
        self.flows = flows
