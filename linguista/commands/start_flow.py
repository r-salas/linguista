#
#
#   Start Flow
#
#

from dataclasses import dataclass


@dataclass
class StartFlowCommand:
    name: str
