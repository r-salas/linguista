#
#
#   Types
#
#
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Categorical:
    categories: Sequence[str]

    def __post_init__(self):
        object.__setattr__(self, 'categories', tuple(self.categories))
