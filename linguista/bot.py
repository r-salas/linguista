#
#
#   Bot
#
#

import uuid
import warnings
from collections import deque
from typing import Optional, List, Type

from . import default_flows
from .actions import ChainAction, ActionFunction
from .commands import render_prompt, parse_command_prompt_response
from .commands.command import run_commands
from .flow import Flow
from .llm import LLM, OpenAI
from .session import Session
from .tracker import Tracker, RedisTracker


def assert_is_action(action):
    assert isinstance(action, ActionFunction), "Action must be an instance of ActionFunction."


def _find_internal_flow(flows, internal_flow_type):
    return next((flow for flow in flows if isinstance(flow, internal_flow_type)), None)


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

        chitchat_flow = _find_internal_flow(self.flows, default_flows.Chitchat)
        cancel_flow = _find_internal_flow(self.flows, default_flows.CancelFlow)
        clarify_flow = _find_internal_flow(self.flows, default_flows.Clarify)
        human_handoff_flow = _find_internal_flow(self.flows, default_flows.HumanHandoff)
        cannot_handle_flow = _find_internal_flow(self.flows, default_flows.CannotHandle)
        completed_flow = _find_internal_flow(self.flows, default_flows.Completed)
        continue_interrupted_flow = _find_internal_flow(self.flows, default_flows.ContinueInterrupted)
        internal_error_flow = _find_internal_flow(self.flows, default_flows.InternalError)
        correction_flow = _find_internal_flow(self.flows, default_flows.Correction)
        skip_question_flow = _find_internal_flow(self.flows, default_flows.SkipQuestion)

        current_flow = None

        yield from run_commands(commands=command_list, flows=self.flows, current_flow=current_flow,
                                tracker=self.tracker, session_id=self.session.id)
