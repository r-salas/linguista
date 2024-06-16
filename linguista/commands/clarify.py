#
#
#   Clarify
#
#

from dataclasses import dataclass
from typing import Tuple


@dataclass(init=False)
class ClarifyCommand:
    flows: Tuple[str]

    def __init__(self, *flows: Tuple[str]):
        self.flows = flows
