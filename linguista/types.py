#
#
#   Types
#
#
from dataclasses import dataclass
from typing import List


@dataclass
class Categorical:

    categories: List[str]
