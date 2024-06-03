#
#
#   Bot
#
#

import uuid
import warnings
from typing import Optional, List, Type

from .actions import ChainAction, Ask, ActionFunction
from .flow import Flow
from .commands import render_prompt, parse_command_prompt_response, StartFlowCommand, ChitChatCommand
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

        action_list = parse_command_prompt_response(response)

        print(action_list)

        next_actions = []

        for action in action_list:
            if isinstance(action, ChitChatCommand):

            elif isinstance(action, StartFlowCommand):
                flow_to_start = next((flow for flow in self.flows if flow.name == action.name), None)

                if flow_to_start is None:
                    warnings.warn(f"Flow '{action.name}' not found.")
                    continue

                # TODO: set current flow to tracker
                # TODO: change current flow

                next_actions = flow_to_start.start()

                if isinstance(next_actions, ChainAction):
                    next_actions_list = next_actions.actions
                else:
                    next_actions_list = [next_actions]

                for next_action in next_actions_list:
                    print(next_action)
                    if isinstance(next_action, Ask):
                        yield next_action.prompt
                    elif isinstance(next_action, ActionFunction):
