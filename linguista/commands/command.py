#
#
#   Command Classifier
#
#

import os
from typing import Sequence, List, Dict

import jinja2

from ..flow import Flow, FlowSlot
from ..types import Categorical

current_dir = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(current_dir, "command_prompt_template.jinja2")) as fp:
    COMMAND_PROMPT_TEMPLATE = fp.read()


def render_prompt(available_flows: Sequence[Flow], current_flow: Flow, current_slot: FlowSlot,
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

    current_flow_slots = current_flow.get_slots()
    current_flow_slots = [flow_slot_to_dict(slot) for slot in current_flow_slots]

    command_prompt = jinja2.Template(COMMAND_PROMPT_TEMPLATE).render({
        "available_flows": available_flows,
        "current_flow": current_flow.name,
        "current_slot": current_slot.name,
        "current_slot_description": current_slot.description,
        "current_flow_slots": current_flow_slots,
        "current_conversation": current_conversation_str,
        "user_message": latest_user_message
    })

    return command_prompt


def parse_command_prompt_response(response: str):
    response = response.strip().splitlines()

    ...
