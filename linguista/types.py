#
#
#   Types
#
#
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Categorical:
    categories: Tuple[str]

    def __post_init__(self):
        object.__setattr__(self, 'categories', tuple(self.categories))
