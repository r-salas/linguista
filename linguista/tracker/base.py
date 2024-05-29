#
#
#   Base class for trackers
#
#

from abc import ABC, abstractmethod

from ..enums import Role


class Tracker(ABC):

    @abstractmethod
    def get_conversation(self, session_id: str):
        """
        Get the conversation for a session.

        Args:
            session_id: The session ID.

        Returns:
            The conversation.
        """
        raise NotImplementedError()

    @abstractmethod
    def add_message_to_conversation(self, session_id: str, role: Role, message: str):
        """
        Add a message to a conversation.

        Args:
            session_id: The session ID.
            role: The role of the speaker.
            message: The message.
        """
        raise NotImplementedError()
