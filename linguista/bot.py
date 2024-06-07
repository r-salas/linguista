#
#
#   Bot
#
#

import uuid
import warnings
from collections import deque
from dataclasses import asdict
from typing import Optional, List, Type

from . import default_flows
from .actions import ActionFunction, Reply, Ask, ChainAction
from .commands import render_prompt, parse_command_prompt_response, SetSlotCommand, StartFlowCommand
from .enums import Role
from .flow import Flow
from .llm import LLM, OpenAI
from .session import Session
from .tracker import Tracker, RedisTracker


def assert_is_action(action):
    assert isinstance(action, ActionFunction), "Action must be an instance of ActionFunction."


def _find_internal_flow(flows, internal_flow_type):
    return next((flow for flow in flows if isinstance(flow, internal_flow_type)), None)


def _find_flow_by_name(flows, name):
    return next((flow for flow in flows if flow.name == name), None)


def _listify_actions(actions):
    if isinstance(actions, ChainAction):
        return actions.actions
    else:
        return [actions]


def _run_commands(commands: List, flows: List[Flow], tracker: RedisTracker, session_id: str, current_flow: Optional[Flow] = None):
    yield from ()  # HACK: Convert to iterator, even if there's nothing to yield, i.e. no replies / ask

    next_actions = tracker.get_current_actions(session_id)
    next_actions = deque(next_actions)  # Convert to deque for efficient popping

    print("Initial actions", next_actions)
    print("Commands", commands)

    for command in commands:
        if isinstance(command, SetSlotCommand):
            tracker.set_flow_slot(session_id, current_flow.name, command.name, command.value)
        elif isinstance(command, StartFlowCommand):
            current_flow = _find_flow_by_name(flows, command.name)

            if current_flow is None:
                raise ValueError(f"Flow '{command.name}' not found.")

            next_actions.appendleft((current_flow.start, current_flow))
        else:
            raise ValueError(f"Invalid command: {command}")

        while next_actions:
            action, action_flow = next_actions.popleft()

            if isinstance(action, Reply):
                yield action.message
            elif isinstance(action, Ask):
                flow_slot_value = tracker.get_flow_slot(session_id, action_flow.name, action.slot.name)

                # If the slot value is not set, ask the user. Otherwise, skip the ask
                if flow_slot_value is None:
                    next_actions.appendleft((action, action_flow))
                    break  # We don't want to run the next actions until the user responds
                else:
                    print("Skipping ask for slot", action.slot.name, "with value", flow_slot_value)
            elif isinstance(action, ActionFunction):
                action_func_next_actions = action(action_flow)
                action_func_next_actions = _listify_actions(action_func_next_actions)
                action_func_next_actions = [(action, action_flow) for action in action_func_next_actions]
                next_actions.extendleft(reversed(action_func_next_actions))  # Prepend the actions to the queue
            else:
                raise ValueError(f"Invalid action: {action}")

    # If there are any pending asks, yield the prompt for the first one
    following = next_actions[0] if next_actions else None

    if following is None:
        tracker.delete_current_flow(session_id)
        tracker.delete_current_slot(session_id)
        tracker.delete_current_actions(session_id)
    else:
        following_next_action, following_flow = following

        if isinstance(following_next_action, Ask):
            yield following_next_action.prompt
            tracker.set_current_slot(session_id, following_next_action.slot.name)
        else:
            tracker.delete_current_slot(session_id)

        tracker.set_current_flow(session_id, following_flow.name)
        tracker.save_current_actions(session_id, next_actions)

    print("Next actions", next_actions)

    for action, flow in next_actions:
        print(asdict(action))


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
        flow_instance = flow(self.tracker, self.session.id)
        self.flows.append(flow_instance)

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
            return iter(())   # Return an empty iterator

        current_conversation = self.tracker.get_conversation(self.session.id)

        # self.tracker.add_message_to_conversation(self.session.id, Role.USER, message)

        print("Current conversation", current_conversation)

        current_flow_name = self.tracker.get_current_flow(self.session.id)
        current_slot_name = self.tracker.get_current_slot(self.session.id)

        current_flow = _find_flow_by_name(self.flows, current_flow_name)
        current_slot = None if current_flow is None else current_flow.get_slot(current_slot_name)

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

        def response_generator():
            for bot_response in _run_commands(commands=command_list, flows=self.flows, tracker=self.tracker,
                                              session_id=self.session.id, current_flow=current_flow):
                yield bot_response
                # self.tracker.add_message_to_conversation(self.session.id, Role.ASSISTANT, response)

        if stream:
            return response_generator()
        else:
            return list(response_generator())
