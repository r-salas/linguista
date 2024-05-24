#
#
#   Command Classifier
#
#

import os
import jinja2
import inspect

from pprint import pprint
from typing import Optional
from openai import OpenAI

current_dir = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(current_dir, "command_prompt_template.jinja2")) as fp:
    COMMAND_PROMPT_TEMPLATE = fp.read()


def classify_command(text: str):
    text = text.replace("\n", " ")

    available_flows = [
        {
            "name": "transfer_money",
            "description": "Transfer money to another account",
            "slots": [
                {
                    "name": "transfer_money_amount",
                    "description": "Amount to transfer",
                },
                {
                    "name": "transfer_money_recipient",
                    "description": "Recipient name of the transfer",
                    "type": "categorical",
                    "allowed_values": [
                        "Rubén",
                        "Alicia",
                        "Enrique"
                    ]
                },
            ]
        },
        {
            "name": "get_current_money",
            "description": "Get how much money you have in your account",
            "slots": []
        },
        {
            "name": "get_last_transactions",
            "description": "Get the last transactions in your account",
            "slots": [
                {
                    "name": "get_last_transactions_limit",
                    "description": "Number of transactions to get",
                    "type": "number",
                }
            ]
        }
    ]

    # current_conversation: keep only last n turns
    command_prompt = jinja2.Template(COMMAND_PROMPT_TEMPLATE).render({
        "available_flows": available_flows,
        "current_conversation": inspect.cleandoc(f"""
            USER: Hi, I want to transfer some money
            AI: Sure, how much do you want to transfer?
            USER: 20 euros
            AI: Who do you want to transfer the money to?
            USER: {text}
        """),
        "current_flow": "transfer_money",
        "current_slot": "transfer_money_recipient",
        "current_slot_description": "Recipient of the transfer",
        "current_flow_slots": [
            {
                "name": "transfer_money_amount",
                "description": "Amount to transfer",
                "type": "number",
                "value": 20
            },
        ],
        "user_message": text
    })

    print(command_prompt)

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": command_prompt
            }
        ],
        temperature=0,
        model="gpt-3.5-turbo",
    )

    action_list = chat_completion.choices[0].message.content.split("\n")
    pprint(action_list)
