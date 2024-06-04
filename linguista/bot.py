#
#
#   Bot
#
#

import uuid
import warnings
from typing import Optional, List, Type

from .actions import ChainAction, Ask, ActionFunction, Reply
from .flow import Flow
from .commands import render_prompt, parse_command_prompt_response, StartFlowCommand, ChitChatCommand, \
    CancelFlowCommand, ClarifyCommand, HumanHandoffCommand, RepeatCommand, SetSlotCommand, SkipQuestionCommand
from .llm import LLM, OpenAI
from .session import Session
from .tracker import Tracker, RedisTracker


class Bot:

    def __init__(self, session_id: Optional[str] = None, tracker: Optional[Tracker] = None, model: Optional[LLM] = None,
                 flows: Optional[List[Type[Flow]]] = None):
        if session_id is None:
            session_id = str(uuid.uuid4())

        if flows is None:
            flows = []

        assert [issubclass(flow, Flow) for flow in flows], "All flows must be subclasses of Flow."

        if tracker is None:
            tracker = RedisTracker()

        if model is None:
            model = OpenAI()

        self.tracker = tracker
        self.model = model
        self.session = Session(session_id, tracker)
        self.flows = [flow_cls(tracker, session_id) for flow_cls in flows]

    def add_flow(self, flow: Type[Flow]):
        flow = flow(self.tracker, self.session.id)
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
        yield from ()  # HACK: Convert to iterator, even if there's nothing to yield, i.e. no replies / ask

        if not self.flows:
            warnings.warn("No flows available. Please add flows to the bot.")
            return

        current_conversation = self.tracker.get_conversation(self.session.id)

        current_flow = None
        current_slot = None

        prompt = render_prompt(
            available_flows=self.flows,
            current_flow=current_flow,
            current_slot=current_slot,
            current_conversation=current_conversation,
            latest_user_message=message
        )

        response = self.model(prompt)

        command_list = parse_command_prompt_response(response)

        print(command_list)

        for command in command_list:
            if isinstance(command, ChitChatCommand):
                if current_flow is not None and hasattr(current_flow, "chitchat"):
                    next_actions = current_flow.chitchat(current_flow)
                else:
                    ...   # Default chitchat
            elif isinstance(command, CancelFlowCommand):
                ...
            elif isinstance(command, ClarifyCommand):
                ...
            elif isinstance(command, HumanHandoffCommand):
                ...
            elif isinstance(command, RepeatCommand):
                ...
            elif isinstance(command, SetSlotCommand):
                ...
            elif isinstance(command, SkipQuestionCommand):
                ...
            elif isinstance(command, StartFlowCommand):
                flow_to_start = next((flow for flow in self.flows if flow.name == command.name), None)

                if flow_to_start is None:
                    warnings.warn(f"Flow '{command.name}' not found.")
                    continue

                # TODO: set current flow to tracker
                # TODO: change current flow

                next_actions = flow_to_start.start(flow_to_start)

                if isinstance(next_actions, ChainAction):
                    next_actions_list = next_actions.actions
                else:
                    next_actions_list = [next_actions]

                print(next_actions_list)
