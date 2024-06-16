#
#
#   Bot
#
#
import inspect
import uuid
import warnings
from collections import deque
from typing import Optional, List, Sequence, Any

from .actions import ActionFunction, Reply, Ask, ChainAction, Action, End, CallFlow
from .commands import render_prompt, parse_command_prompt_response, SetSlotCommand, StartFlowCommand, CancelFlowCommand, \
    ChitChatCommand, ClarifyCommand, HumanHandoffCommand, RepeatCommand, SkipQuestionCommand
from .enums import Role
from .flow import Flow
from .llm import LLM, OpenAI
from .session import Session
from .tracker import Tracker, RedisTracker, ProxyTracker
from .utils import debug


def assert_is_action(action: Any):
    """
    Asserts that the action is an instance of ActionFunction.

    """
    assert isinstance(action, ActionFunction), "Action must be an instance of ActionFunction."


def _find_flow_by_name(flows: Sequence[Flow], name: str):
    return next((flow for flow in flows if flow.name == name), None)


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


def _run_commands(commands: List, flows: List[Flow], tracker: RedisTracker, session_id: str,
                  current_flow: Optional[Flow] = None):
    """
    This function processes a list of commands, updates the tracker and yields responses.

    Parameters
    ----------
    commands: List
        A list of commands to be processed.
    flows: List[Flow]
        A list of available flows.
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

    # Load previous actions
    next_actions_with_flows = tracker.get_current_actions(session_id)
    next_actions_with_flows = deque(next_actions_with_flows)  # Convert to deque for efficient popping

    debug("Initial actions", next_actions_with_flows)
    debug("Commands", commands)

    for command in commands:
        if isinstance(command, SetSlotCommand):
            tracker.set_flow_slot(session_id, current_flow.name, command.name, command.value)
        elif isinstance(command, StartFlowCommand):
            current_flow = _find_flow_by_name(flows, command.name)

            if current_flow is None:
                raise ValueError(f"Flow '{command.name}' not found.")

            next_actions_with_flows.appendleft((current_flow.start, current_flow.name))
        elif isinstance(command, CancelFlowCommand):
            next_actions_with_flows.appendleft((End(), current_flow.name))
            next_actions_with_flows.appendleft((Reply("Ok, I will stop."), current_flow.name))  # FIXME: This is a hack
        elif isinstance(command, ChitChatCommand):
            next_actions_with_flows.appendleft((Reply("I'm a virtual assistant designed to help you with multiple tasks. How can I help you?"), current_flow.name))  # FIXME: This is a hack
        elif isinstance(command, ClarifyCommand):
            next_actions_with_flows.appendleft((Reply("I'm sorry, I didn't understand that. Can you please clarify what do you mean?"), current_flow.name))   # FIXME: This is a hack
        elif isinstance(command, HumanHandoffCommand):
            next_actions_with_flows.appendleft((Reply("Before transferring you to an agent, let's try to solve it together. What can I help you with?"), current_flow.name))   # FIXME: This is a hack
        elif isinstance(command, RepeatCommand):
            pass  # How can I do it? I must have a history of the conversation to repeat it
        elif isinstance(command, SkipQuestionCommand):
            next_actions_with_flows.appendleft((Reply("To assist you effectively, I need you to provide the information I requested."), current_flow.name))   # FIXME: This is a hack
        else:
            raise ValueError(f"Invalid command: {command}")

        while next_actions_with_flows:
            action, action_flow_name = next_actions_with_flows.popleft()

            if isinstance(action, Reply):
                yield action.message
            elif isinstance(action, Ask):
                flow_slot_value = tracker.get_flow_slot(session_id, action_flow_name, action.slot.name)

                # If the slot value is not set, ask the user. Otherwise, skip the ask
                if flow_slot_value is None:
                    next_actions_with_flows.appendleft((action, action_flow_name))  # Re-add the ask task to the queue
                    break  # We don't want to run the next actions until the user responds
            elif isinstance(action, ActionFunction):
                action_flow = _find_flow_by_name(flows, action_flow_name)

                # The function may be a string, usually because it's from tracker
                if isinstance(action.function, str):
                    # If the function is a string, replace the action with the actual function
                    action = getattr(action_flow, action.function, None)

                # Dynamically inject the available parameters to the action function.
                # If the action function doesn't need any of the parameters, they will be ignored.
                available_params = {
                    "tracker": ProxyTracker(tracker, session_id, action_flow)
                }

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
                flow = _find_flow_by_name(flows, action.flow_name)
                next_actions_with_flows.appendleft((flow.start, flow.name))
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

        current_actions = self.tracker.get_current_actions(self.session.id)

        current_flow = None
        current_slot = None

        if len(current_actions) > 0:
            following_action, following_flow_name = current_actions[0]

            current_flow = _find_flow_by_name(self.flows, following_flow_name)
            if isinstance(following_action, Ask):
                current_slot = current_flow.get_slot(following_action.slot.name)

        debug("Current flow", current_flow.name if current_flow else None)
        debug("Current slot", current_slot.name if current_slot else None)

        prompt = render_prompt(
            available_flows=self.flows,
            current_flow=current_flow,
            current_slot=current_slot,
            current_conversation=current_conversation,
            latest_user_message=message
        )

        response = self.model(prompt)

        command_list = parse_command_prompt_response(response)

        def response_generator():
            for bot_response in _run_commands(commands=command_list, flows=self.flows, tracker=self.tracker,
                                              session_id=self.session.id, current_flow=current_flow):
                yield bot_response
                self.tracker.add_message_to_conversation(self.session.id, Role.ASSISTANT, bot_response)

        if stream:
            return response_generator()
        else:
            return list(response_generator())
