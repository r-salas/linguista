#
#
#   Bot
#
#
import uuid
from typing import Optional, List, Type

from . import Flow
from .session import Session
from .tracker import Tracker, RedisTracker

from .commands import render_prompt, parse_command_prompt_response
from .llm import LLM, OpenAI


class Bot:

    def __init__(self, session_id: Optional[str] = None, tracker: Optional[Tracker] = None, model: Optional[LLM] = None, flows: Optional[List[Type[Flow]]] = None):
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

    def add_flow(self, flow: Type[Flow]):
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
        available_flows = []   # FIXME: Instantiate the available flows
        current_flow_meta = self.tracker.get_current_flow(self.session.id) or {}
        conversation = self.tracker.get_conversation(self.session.id)

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

        command_runner = CommandRunner()
        response_stream = command_runner.run(action_list, current_flow, current_slot)

        for response in response_stream:

    def reply(self, message: str):
        """
        Reply to the user.

        Args:
            message: The message to send.
        """
        print(f"Bot: {message}")  # FIXME: Implement this
        # self.tracker.add_message_to_conversation(self.session_id, Role.ASSISTANT, message)
