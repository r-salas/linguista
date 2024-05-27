#
#
#   Flow
#
#

import inspect
from abc import ABC, abstractmethod
from typing import Optional

from .bot import Bot

from .types import Categorical


class FlowSlot:

    def __init__(self, description: str, type=str, name: Optional[str] = None):
        self.name = name
        self.description = description
        self.type = type

        assert type in {int, bool, str, float} or isinstance(type, Categorical), f"Invalid type: {type}"

    def __repr__(self):
        return f"FlowSlot(description='{self.description}', type={self.type})"


class Flow(ABC):
    """
    Base class for conversational flows.
    """

    @abstractmethod
    def start(self, bot: Bot):
        """
        Start the flow.

        Args:
            bot: The bot instance.

        Returns:
            The first action of the flow.
        """
        pass

    def __repr__(self):
        slots = inspect.getmembers(self, lambda attr: isinstance(attr, FlowSlot))
        print(slots)
        return "Flow()"
