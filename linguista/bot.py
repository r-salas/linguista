#
#
#   Bot
#
#

import inspect
import uuid
import warnings
from collections import deque
from typing import Optional, List, Sequence, Any, Type, Dict

from .flow_slot import FlowSlot
from .actions import ActionFunction, Reply, Ask, ChainAction, Action, End, CallFlow
from .commands import render_prompt, parse_command_prompt_response, SetSlotCommand, StartFlowCommand, CancelFlowCommand, \
    ChitChatCommand, ClarifyCommand, HumanHandoffCommand, RepeatCommand, SkipQuestionCommand
from .enums import Role
from .event_flows import CancelFlow, CannotHandle, ChitChat, Clarify, Completed, ContinueInterrupted, Correction, \
    HumanHandoff, InternalError, SkipQuestion
from .event_flows.base import EventFlow
from .flow import Flow
from .models import LLM, OpenAI
from .session import Session
from .tracker import Tracker, RedisTracker, ProxyTracker
from .types import Categorical
from .utils import debug, extract_digits, strtobool


def assert_is_action(action: Any):
    """
    Asserts that the action is an instance of ActionFunction.
    """
    assert isinstance(action, ActionFunction), "Action must be an instance of ActionFunction."


def _find_flow_by_name(flows: Sequence[Flow], name: str):
    """
    Find a flow by its name.
    """
    return next((flow for flow in flows if flow.name == name), None)


def _find_internal_flow(flows: Sequence[Flow], internal_flow_cls: Type[Flow]):
    """
    Check if the user has overriden the default internal flow. If so, return the overriden flow. Otherwise, return the
    default internal flow.
    """
    overriden_flow = next((flow for flow in flows if isinstance(flow, internal_flow_cls)), None)

    if overriden_flow is not None:
        return overriden_flow

    return internal_flow_cls()


def _listify_actions(actions: ChainAction | Action):
    """
    Convert the actions to a list of actions. If the actions is a ChainAction, return the actions. Otherwise, return a
    list with the action.

    Parameters
    ----------
    actions: ChainAction | Action
        The actions to convert.
    Returns
    --------
    List[Action]
        A list of actions.
    """
    if isinstance(actions, ChainAction):
        return actions.actions
    else:
        return [actions]


def _parse_flow_slot_value(flow_slot: FlowSlot, value: str):
    """
    Parse the value of a flow slot based on its type.
    :param flow_slot: Flow slot to parse the value for.
    :param value: Value to parse.
    :return: Parsed value.
    """
    flow_slot_value = None

    if flow_slot.type == int:
        digits = extract_digits(value)
        flow_slot_value = int(digits)
    elif flow_slot.type == float:
        digits = extract_digits(value)
        flow_slot_value = float(digits)
    elif flow_slot.type == bool:
        flow_slot_value = str(strtobool(value))
    elif flow_slot.type == str:
        flow_slot_value = value
    elif isinstance(flow_slot.type, Categorical):
        matches = [category for category in flow_slot.type.categories
                   if category.lower() == value.lower()]

        if matches:
            if len(matches) > 1:
                warnings.warn(f"Multiple matches found for value '{value}' in slot '{flow_slot.name}'")

            flow_slot_value = matches[0]
        else:
            debug("No match found for value", value, "in slot", flow_slot.name)
    else:
        raise ValueError(f"Invalid slot type: {flow_slot.type}")

    return flow_slot_value


def _run_commands(commands: List, flows: List[Flow], event_flows: Dict[str, Flow], tracker: RedisTracker,
                  session_id: str, current_flow: Optional[Flow] = None):
    """
    This function processes a list of commands, updates the tracker and yields responses.

    Parameters
    ----------
    commands: List
        A list of commands to be processed.
    flows: List[Flow]
        A list of available flows.
    event_flows: Dict[str, Flow]
        A dictionnary of flows by event name.
    tracker RedisTracker:
        The tracker object to keep track of the state.
    session_id str:
        The session ID.
    current_flow: Optional[Flow]
        The current flow, defaults to None.

    Yields
    ------
    str
        The bot's response to the user.
    """
    yield from ()  # HACK: Convert to iterator, even if there's nothing to yield, i.e. no replies / ask

    all_flows = flows + list(event_flows.values())

    # Load previous actions
    next_actions_with_flows = tracker.get_current_actions(session_id)
    next_actions_with_flows = deque(next_actions_with_flows)  # Convert to deque for efficient popping

    debug("Initial actions", next_actions_with_flows)
    debug("Commands", commands)

    # Check if the next action is an ask, we save the slot requested to be able to check if the user has answered
    # to the ask. This is used for the functionality `ask_before_filling`. We need to know if the user has answered
    # from the ask.
    flow_slot_requested = None
    if next_actions_with_flows:
        following_next_action, following_flow_name = next_actions_with_flows[0]

        if isinstance(following_next_action, Ask):
            flow_slot_requested = (following_next_action.slot, following_flow_name)

    # If there are no commands predicted, start the CannotHandle flow
    if not commands:
        current_flow = event_flows["cannot_handle"]
        next_actions_with_flows.appendleft((current_flow.start, current_flow.name))

        commands.append(None)  # Add a dummy command so the actions loop runs at least once

    for command in commands:
        if isinstance(command, SetSlotCommand):
            flow_slot_value = None

            if current_flow:
                # Parse flow slot value based on slot type
                flow_slot: FlowSlot = current_flow.get_slot(command.name)

                if flow_slot:
                    flow_slot_value = _parse_flow_slot_value(flow_slot, command.value)
            else:
                debug(f"No current flow to set slot {command.name} with value {command.value}.")

            if flow_slot_value is None:
                current_flow = event_flows["cannot_handle"]
                next_actions_with_flows.appendleft((current_flow.start, current_flow.name))
            else:
                tracker.set_flow_slot(session_id, current_flow.name, command.name, flow_slot_value)
        elif isinstance(command, StartFlowCommand):
            if current_flow is None:
                completed = event_flows["completed"]
                next_actions_with_flows.appendleft((completed.start, completed.name))
            else:
                continue_interrupted = event_flows["continue_interrupted"]
                next_actions_with_flows.appendleft((continue_interrupted.start, continue_interrupted.name))

            current_flow = _find_flow_by_name(all_flows, command.name)

            if current_flow is None:
                warnings.warn(f"Flow '{command.name}' not found.")
                current_flow = event_flows["cannot_handle"]

            next_actions_with_flows.appendleft((current_flow.start, current_flow.name))
        elif isinstance(command, CancelFlowCommand):
            # TODO: how to handle the END? Should I handle here or in the event flow?
            next_actions_with_flows.appendleft((End(), current_flow.name))

            current_flow = event_flows["cancel"]
            next_actions_with_flows.appendleft((current_flow.start, current_flow.name))
        elif isinstance(command, ChitChatCommand):
            current_flow = event_flows["chit_chat"]
            next_actions_with_flows.appendleft((current_flow.start, current_flow.name))
        elif isinstance(command, ClarifyCommand):
            current_flow = event_flows["clarify"]
            next_actions_with_flows.appendleft((current_flow.start, current_flow.name))
        elif isinstance(command, HumanHandoffCommand):
            current_flow = event_flows["human_handoff"]
            next_actions_with_flows.appendleft((current_flow.start, current_flow.name))
        elif isinstance(command, RepeatCommand):
            pass  # Get current conversation and repeat the last message of the bot
        elif isinstance(command, SkipQuestionCommand):
            current_flow = event_flows["skip_question"]
            next_actions_with_flows.appendleft((current_flow.start, current_flow.name))
        elif command is None:
            pass  # Do nothing, dummy command
        else:
            raise ValueError(f"Invalid command: {command}")

        while next_actions_with_flows:
            action, action_flow_name = next_actions_with_flows.popleft()

            if isinstance(action, Reply):
                yield action.message
            elif isinstance(action, Ask):
                action_flow = _find_flow_by_name(all_flows, action_flow_name)

                flow_slot = action_flow.get_slot(action.slot.name)
                flow_slot_value = tracker.get_flow_slot(session_id, action_flow_name, action.slot.name)

                # We need to check if we must ask the user for the slot value. If the slot is already set, we skip the
                # ask. If the slot is not set, we ask the user. If the slot is set, but the ask_before_filling is True,
                # we ask the user again.
                is_from_ask = False
                if flow_slot_requested:
                    flow_slot_requested_name, flow_slot_requested_flow_name = flow_slot_requested

                    if (flow_slot_requested_name.name == action.slot.name) and \
                            (flow_slot_requested_flow_name == action_flow.name):
                        is_from_ask = True

                must_ask_slot = flow_slot.ask_before_filling and not is_from_ask

                # If the slot value is not set, ask the user. Otherwise, skip the ask
                if flow_slot_value is None or must_ask_slot:
                    next_actions_with_flows.appendleft((action, action_flow_name))  # Re-add the ask task to the queue
                    break  # We don't want to run the next actions until the user responds
            elif isinstance(action, ActionFunction):
                action_flow = _find_flow_by_name(all_flows, action_flow_name)

                # The function may be a string, usually because it's from tracker
                if isinstance(action.function, str):
                    # If the function is a string, replace the action with the actual function
                    action = getattr(action_flow, action.function, None)

                # Dynamically inject the available parameters to the action function.
                # If the action function doesn't need any of the parameters, they will be ignored.
                available_params = {
                    "tracker": ProxyTracker(tracker, session_id, action_flow)
                }

                # Parse the parameters of the action function
                action_func_signature = inspect.signature(action.function)
                action_func_args_to_pass = {}
                for param_name, param_value in action_func_signature.parameters.items():
                    if param_name in available_params:
                        action_func_args_to_pass[param_name] = available_params[param_name]

                action_func_next_actions = action.function(action_flow, **action_func_args_to_pass)
                # The action may return a single action or a list of actions
                action_func_next_actions = _listify_actions(action_func_next_actions)
                action_func_next_actions = [(action, action_flow.name) for action in action_func_next_actions]
                next_actions_with_flows.extendleft(reversed(action_func_next_actions))  # Prepend actions to queue
            elif isinstance(action, CallFlow):
                flow_to_call = _find_flow_by_name(all_flows, action.flow_name)
                next_actions_with_flows.appendleft((flow_to_call.start, flow_to_call.name))
            elif isinstance(action, End):
                # Remove all following actions for the current flow
                next_actions_with_flows = deque(filter(lambda x: x[1] != action_flow_name, next_actions_with_flows))
            else:
                raise ValueError(f"Invalid action: {action}")

    following = next_actions_with_flows[0] if next_actions_with_flows else None

    if following is None:  # no more actions to run
        tracker.delete_current_actions(session_id)
        tracker.delete_flow_slots(session_id)  # Delete all flow slots
    else:
        following_next_action, following_flow_name = following

        # If there are any pending asks, yield the prompt for the first one
        if isinstance(following_next_action, Ask):
            yield following_next_action.prompt

        tracker.save_current_actions(session_id, next_actions_with_flows)


class Bot:

    def __init__(self, session_id: Optional[str] = None, tracker: Optional[Tracker] = None,
                 model: Optional[LLM] = None, flows: Optional[List[Flow]] = None):
        if session_id is None:
            session_id = str(uuid.uuid4())

        if flows is None:
            flows = []

        assert [isinstance(flow, Flow) for flow in flows], "All flows must be subclasses of Flow."

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

            if stream:
                return iter(())  # Return an empty iterator
            else:
                return []

        current_conversation = self.tracker.get_conversation(self.session.id)

        self.tracker.add_message_to_conversation(self.session.id, Role.USER, message)

        debug("Current conversation", current_conversation)

        event_flows = {
            "cancel": _find_internal_flow(self.flows, CancelFlow),
            "cannot_handle": _find_internal_flow(self.flows, CannotHandle),
            "chit_chat": _find_internal_flow(self.flows, ChitChat),
            "clarify": _find_internal_flow(self.flows, Clarify),
            "completed": _find_internal_flow(self.flows, Completed),
            "continue_interrupted": _find_internal_flow(self.flows, ContinueInterrupted),
            "correction": _find_internal_flow(self.flows, Correction),
            "human_handoff": _find_internal_flow(self.flows, HumanHandoff),
            "internal_error": _find_internal_flow(self.flows, InternalError),
            "skip_question": _find_internal_flow(self.flows, SkipQuestion)
        }

        user_flows = [flow for flow in self.flows if not isinstance(flow, EventFlow)]

        all_flows = user_flows + list(event_flows.values())

        current_actions = self.tracker.get_current_actions(self.session.id)

        current_flow = None
        current_slot = None
        current_flow_slot_values = None

        if len(current_actions) > 0:
            following_action, following_flow_name = current_actions[0]

            current_flow = _find_flow_by_name(all_flows, following_flow_name)
            current_flow_slot_values = self.tracker.get_flow_slots(self.session.id, current_flow.name)

            if isinstance(following_action, Ask):
                current_slot = current_flow.get_slot(following_action.slot.name)

        debug("Current flow", current_flow.name if current_flow else None)
        debug("Current slot", current_slot.name if current_slot else None)

        prompt = render_prompt(
            available_flows=user_flows,
            current_flow=current_flow,
            current_slot=current_slot,
            current_conversation=current_conversation,
            latest_user_message=message,
            current_flow_slot_values=current_flow_slot_values
        )

        response = self.model(prompt)

        command_list = parse_command_prompt_response(response)

        def response_generator():
            for bot_response in _run_commands(commands=command_list, flows=user_flows, event_flows=event_flows,
                                              tracker=self.tracker, session_id=self.session.id,
                                              current_flow=current_flow):
                yield bot_response
                self.tracker.add_message_to_conversation(self.session.id, Role.ASSISTANT, bot_response)

        if stream:
            return response_generator()
        else:
            return list(response_generator())
