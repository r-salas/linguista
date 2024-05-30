#
#
#   Bot
#
#

import uuid
import warnings
from typing import Optional, List, Type

from . import Flow
from .session import Session
from .tracker import Tracker, RedisTracker

from .commands import render_prompt, parse_command_prompt_response
from .llm import LLM, OpenAI


class Bot:

    def __init__(self, session_id: Optional[str] = None, tracker: Optional[Tracker] = None, model: Optional[LLM] = None, flows: Optional[List[Flow]] = None):
        if session_id is None:
            session_id = str(uuid.uuid4())

        if flows is None:
            flows = []

        if tracker is None:
            tracker = RedisTracker()

        if model is None:
            model = OpenAI()

        self.tracker = tracker
        self.model = model
        self.session = Session(session_id, tracker)
        self.flows = flows

    def add_flow(self, flow: Flow):
        self.flows.append(flow)

    def message(self, message, stream=False):
        """
        Listen to the user.

        Args:
            message: The message from the user.
            stream: Whether to stream the responses.

        Returns:
            The responses.
        """
        if not self.flows:
            warnings.warn("No flows available. Please add flows to the bot.")
            return

        current_flow_meta = self.tracker.get_current_flow(self.session.id) or {}
        conversation = self.tracker.get_conversation(self.session.id)

        current_flow = next((flow for flow in self.flows if flow.name == current_flow_meta.get("name")), None)
        current_slot = None
        if current_flow is not None:
            current_slot = current_flow.get_slot(current_flow_meta.get("slot_name"))

        command_prompt = render_prompt(
            available_flows=self.flows,
            current_flow=current_flow,
            current_slot=current_slot,
            current_conversation=conversation,
            latest_user_message=message
        )

        command_prompt_response = self.model(command_prompt)
        action_list = parse_command_prompt_response(command_prompt_response)



        if stream:
            return response_stream
        else:
            return [response for response in response_stream]

    def reply(self, message: str):
        """
        Reply to the user.

        Args:
            message: The message to send.
        """
        print(f"Bot: {message}")  # FIXME: Implement this
        # self.tracker.add_message_to_conversation(self.session_id, Role.ASSISTANT, message)
