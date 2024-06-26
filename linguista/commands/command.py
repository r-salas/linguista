#
#
#   Command Classifier
#
#

import os
import re
from typing import Sequence, List, Dict, Optional

import jinja2

from .cancel_flow import CancelFlowCommand
from .chitchat import ChitChatCommand
from .clarify import ClarifyCommand
from .human_handoff import HumanHandoffCommand
from .set_slot import SetSlotCommand
from .skip_question import SkipQuestionCommand
from .start_flow import StartFlowCommand
from .repeat import RepeatCommand
from ..enums import Role
from ..flow import Flow
from ..flow_slot import FlowSlot
from ..types import Categorical

current_dir = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(current_dir, "command_prompt_template.jinja2")) as fp:
    COMMAND_PROMPT_TEMPLATE = fp.read()


def render_prompt(available_flows: Sequence[Flow], current_flow: Optional[Flow], current_slot: Optional[FlowSlot],
                  current_flow_slot_values: Optional[Dict[str, str]], current_conversation: List[Dict[str, str]],
                  latest_user_message: str) -> str:
    if current_flow_slot_values is None:
        current_flow_slot_values = {}

    latest_user_message = latest_user_message.replace("\n", " ")

    def flow_slot_to_dict(flow_slot: FlowSlot, in_current_flow: bool = False):
        allowed_values = None
        if flow_slot.type == bool:
            slot_type = "boolean"
        elif isinstance(flow_slot.type, Categorical):
            slot_type = "categorical"
            allowed_values = ", ".join(flow_slot.type.categories)
        else:
            slot_type = {
                int: "number",
                str: "text",
                float: "number",
            }[flow_slot.type]

        return {
            "name": flow_slot.name,
            "description": flow_slot.description,
            "type": slot_type,
            "allowed_values": allowed_values,
            "value": current_flow_slot_values.get(flow_slot.name, "") if in_current_flow else None
        }

    def flow_to_dict(flow: Flow):
        return {
            "name": flow.name,
            "description": flow.description,
            "slots": [flow_slot_to_dict(slot) for slot in flow.get_slots()]
        }

    available_flows = [flow_to_dict(flow) for flow in available_flows]

    role_to_str = {
        Role.USER: "USER",
        Role.ASSISTANT: "AI"
    }

    last_n_messages = 20  # FIXME: make it configurable

    user_str = f"USER: {latest_user_message}"
    current_conversation_str = "\n".join([f"{role_to_str[message['role']]}: {message['message']}"
                                          for message in current_conversation[-last_n_messages:]] + [user_str])

    if current_flow is None:
        current_flow_name = None
        current_flow_slots = []
    else:
        current_flow_name = current_flow.name
        current_flow_slots = current_flow.get_slots()
        current_flow_slots = [flow_slot_to_dict(slot, in_current_flow=True) for slot in current_flow_slots]

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
    repeat_re = re.compile(r"Repeat\(\)")

    for action in response:
        if match := slot_set_re.search(action):
            slot_name = match.group(1).strip()
            slot_value = match.group(2).strip("'\" ")

            # FIXME: sometimes the model predicts a slot set command with the flow name

            # error case where the llm tries to start a flow using a slot set
            if slot_name == "flow_name":
                commands.append(StartFlowCommand(slot_value))
            else:
                commands.append(
                    SetSlotCommand(name=slot_name, value=slot_value)
                )
        elif match := start_flow_re.search(action):
            flow_name = match.group(1).strip()
            if flow_name == "HumanHandoff":
                # Sometimes the model predicts HumanHandoff as a flow name
                commands.append(HumanHandoffCommand())
            else:
                commands.append(StartFlowCommand(flow_name))
        elif cancel_flow_re.search(action):
            commands.append(CancelFlowCommand())
        elif chitchat_re.search(action):
            commands.append(ChitChatCommand())
        elif skip_question_re.search(action):
            commands.append(SkipQuestionCommand())
        elif humand_handoff_re.search(action):
            commands.append(HumanHandoffCommand())
        elif repeat_re.search(action):
            commands.append(RepeatCommand())
        elif match := clarify_re.search(action):
            options = sorted([opt.strip() for opt in match.group(1).split(",")])
            if len(options) > 1:  # NOTE: if there is only one option, is it a clarification?
                commands.append(ClarifyCommand(options))

    return commands
