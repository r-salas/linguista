#
#
#   Set slot command
#
#

from dataclasses import dataclass
from typing import Optional


@dataclass
class SetSlotCommand:
    name: str
    value: Optional[str]

    def __post_init__(self):
        if self.value in {
            "[missing information]",
            "[missing]",
            "None",
            "undefined",
            "null",
        }:
            self.value = None
