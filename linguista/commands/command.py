#
#
#   Command Classifier
#
#

import os
import re
from collections import deque
from typing import Sequence, List, Dict, Optional

import jinja2

from ..actions import ChainAction, Reply, Ask, ActionFunction
from ..flow import Flow, FlowSlot
from ..tracker import Tracker
from ..types import Categorical
from .chitchat import ChitChatCommand
from .set_slot import SetSlotCommand
from .start_flow import StartFlowCommand
from .cancel_flow import CancelFlowCommand
from .skip_question import SkipQuestionCommand
from .human_handoff import HumanHandoffCommand
from .clarify import ClarifyCommand


current_dir = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(current_dir, "command_prompt_template.jinja2")) as fp:
    COMMAND_PROMPT_TEMPLATE = fp.read()


def _find_flow_by_name(flows, name):
    return next((flow for flow in flows if flow.name == name), None)


def _listify_actions(actions):
    if isinstance(actions, ChainAction):
        return actions.actions
    else:
        return [actions]


def render_prompt(available_flows: Sequence[Flow], current_flow: Optional[Flow], current_slot: Optional[FlowSlot],
                  current_conversation: List[Dict[str, str]], latest_user_message: str):
    latest_user_message = latest_user_message.replace("\n", " ")

    def flow_slot_to_dict(flow_slot: FlowSlot):
        allowed_values = None
        if isinstance(flow_slot.type, Categorical):
            slot_type = "categorical"
            allowed_values = ", ".join(flow_slot.type.categories)
        else:
            slot_type = {
                int: "number",
                bool: "boolean",
                str: "text",
                float: "number",
            }[flow_slot.type]

        return {
            "name": flow_slot.name,
            "description": flow_slot.description,
            "type": slot_type,
            "allowed_values": allowed_values
        }

    def flow_to_dict(flow: Flow):
        return {
            "name": flow.name,
            "description": flow.description,
            "slots": [flow_slot_to_dict(slot) for slot in flow.get_slots()]
        }

    available_flows = [flow_to_dict(flow) for flow in available_flows]

    role_to_str = {
        "user": "USER",
        "assistant": "AI"
    }

    last_n_messages = 20  # FIXME: make it configurable

    user_str = f"USER: {latest_user_message}"
    current_conversation_str = "\n".join([f"{role_to_str[message['role']]}: {message['content']}"
                                          for message in current_conversation[-last_n_messages:]] + [user_str])

    if current_flow is None:
        current_flow_name = None
        current_flow_slots = []
    else:
        current_flow_name = current_flow.name
        current_flow_slots = current_flow.get_slots()
        current_flow_slots = [flow_slot_to_dict(slot) for slot in current_flow_slots]

    if current_slot is None:
        current_slot_name = None
        current_slot_description = None
    else:
        current_slot_name = current_slot.name
        current_slot_description = current_slot.description

    command_prompt = jinja2.Template(COMMAND_PROMPT_TEMPLATE).render({
        "available_flows": available_flows,
        "current_flow": current_flow_name,
        "current_slot": current_slot_name,
        "current_slot_description": current_slot_description,
        "current_flow_slots": current_flow_slots,
        "current_conversation": current_conversation_str,
        "user_message": latest_user_message
    })

    return command_prompt


def parse_command_prompt_response(response: str):
    response = response.strip().splitlines()

    commands = []

    slot_set_re = re.compile(r"""SetSlot\(([a-zA-Z_][a-zA-Z0-9_-]*?), ?(.*)\)""")
    start_flow_re = re.compile(r"StartFlow\(([a-zA-Z0-9_-]+?)\)")
    cancel_flow_re = re.compile(r"CancelFlow\(\)")
    chitchat_re = re.compile(r"ChitChat\(\)")
    skip_question_re = re.compile(r"SkipQuestion\(\)")
    humand_handoff_re = re.compile(r"HumanHandoff\(\)")
    clarify_re = re.compile(r"Clarify\(([a-zA-Z0-9_, ]+)\)")

    for action in response:
        if match := slot_set_re.search(action):
            slot_name = match.group(1).strip()
            slot_value = match.group(2).strip("'\" ")

            # error case where the llm tries to start a flow using a slot set
            if slot_name == "flow_name":
                commands.append(StartFlowCommand(slot_value))   # FIXME: check if flows are valid
            else:
                commands.append(
                    SetSlotCommand(name=slot_name, value=slot_value)
                )
        elif match := start_flow_re.search(action):
            flow_name = match.group(1).strip()
            commands.append(StartFlowCommand(flow_name))   # FIXME: check if flows are valid
        elif cancel_flow_re.search(action):
            commands.append(CancelFlowCommand())
        elif chitchat_re.search(action):
            commands.append(ChitChatCommand())
        elif skip_question_re.search(action):
            commands.append(SkipQuestionCommand())
        elif humand_handoff_re.search(action):
            commands.append(HumanHandoffCommand())
        elif match := clarify_re.search(action):
            options = sorted([opt.strip() for opt in match.group(1).split(",")])
            if len(options) >= 1:
                commands.append(ClarifyCommand(options))  # FIXME: check if flows are valid

    return commands


def run_commands(commands: List, flows: List[Flow], current_flow: Optional[Flow], tracker: Tracker, session_id: str):
    yield from ()  # HACK: Convert to iterator, even if there's nothing to yield, i.e. no replies / ask

    next_actions = deque()

    print(commands)

    for command in commands:
        if isinstance(command, SetSlotCommand):
            tracker.set_flow_slot(session_id, current_flow.name, command.name, command.value)
        elif isinstance(command, StartFlowCommand):
            current_flow = _find_flow_by_name(flows, command.name)

            if current_flow is None:
                raise ValueError(f"Flow '{command.name}' not found.")

            current_flow_next_actions = current_flow.start(current_flow)
            current_flow_next_actions = _listify_actions(current_flow_next_actions)
            next_actions.extendleft(reversed(current_flow_next_actions))
        else:
            raise ValueError(f"Invalid command: {command}")

        while next_actions:
            action = next_actions.popleft()

            if isinstance(action, Reply):
                yield action.message
            elif isinstance(action, Ask):
                flow_slot_value = tracker.get_flow_slot(session_id, current_flow.name, action.slot.name)

                if flow_slot_value is None:
                    next_actions.appendleft(action)
                    break  # We don't want to run the next actions until the user responds
            elif isinstance(action, ActionFunction):
                action_func_next_actions = action(current_flow)
                action_func_next_actions = _listify_actions(action_func_next_actions)
                next_actions.extendleft(reversed(action_func_next_actions))  # Prepend the actions to the queue
            else:
                raise ValueError(f"Invalid action: {action}")

    # If there are any pending asks, yield the prompt
    if next_actions and isinstance(next_actions[0], Ask):
        yield next_actions[0].prompt

    print(next_actions)   # TODO: save next_actions to tracker
