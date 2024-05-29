#
#
#   Bot
#
#

from typing import Optional

from .tracker import Tracker, RedisTracker

from .enums import Role
from .commands import render_prompt, parse_command_prompt_response
from .llm import LLM, OpenAI


class Bot:

    def __init__(self, session_id: str, tracker: Optional[Tracker] = None, model: Optional[LLM] = None):
        if tracker is None:
            tracker = RedisTracker()

        if model is None:
            model = OpenAI()

        self.session_id = session_id
        self.tracker = tracker
        self.model = model

    def message(self, message, stream=False):
        """
        Listen to the user.

        Args:
            message: The message from the user.
            stream: Whether to stream the responses.

        Returns:
            The responses.
        """
        available_flows = []   # FIXME: How to get available flows?
        current_flow_meta = self.tracker.get_current_flow(self.session_id) or {}
        conversation = self.tracker.get_conversation(self.session_id)

        current_flow = ...
        current_slot = ...

        command_prompt = render_prompt(
            available_flows=available_flows,
            current_flow=current_flow,
            current_slot=current_slot,
            current_conversation=conversation,
            latest_user_message=message
        )

        command_prompt_response = self.model(command_prompt)
        action_list = parse_command_prompt_response(command_prompt_response)

        ...

    def reply(self, message: str):
        """
        Reply to the user.

        Args:
            message: The message to send.
        """
        print(f"Bot: {message}")  # FIXME: Implement this
        self.tracker.add_message_to_conversation(self.session_id, Role.ASSISTANT, message)
