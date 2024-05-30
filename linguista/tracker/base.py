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

    @abstractmethod
    def get_current_flow(self, session_id: str):
        """
        Get the current flow for a session.

        Args:
            session_id: The session ID.

        Returns:
            The current flow.
        """
        raise NotImplementedError()

    @abstractmethod
    def update_current_flow(self, session_id: str, flow_name: str):
        """
        Update the current flow for a session.

        Args:
            session_id: The session ID.
            flow_name: The name of the flow.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_slots(self, session_id: str):
        """
        Get the slots for a session.

        Args:
            session_id: The session ID.

        Returns:
            The slots.
        """
        raise NotImplementedError()

    @abstractmethod
    def update_slot(self, session_id: str, slot_name: str, value):
        """
        Update a slot for a session.

        Args:
            session_id: The session ID.
            slot_name: The name of the slot.
            value: The value of the slot.
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_slot(self, session_id: str, slot_name: str):
        """
        Delete a slot for a session.

        Args:
            session_id: The session ID.
            slot_name: The name of the slot.
        """
        raise NotImplementedError()
