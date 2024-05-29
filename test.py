#
#
#
#
#

import linguista
from linguista import Bot
from linguista.command import render_prompt


class TransferMoneyFlow(linguista.Flow):

    amount = linguista.FlowSlot(
        description="Amount of money to transfer",
        type=int,
    )

    recipient = linguista.FlowSlot(
        description="Recipient name",
        type=linguista.types.Categorical(["Alice", "Bob", "Charlie"])
    )

    transfer_confirmation = linguista.FlowSlot(
        description="Confirm the transfer",
        type=bool
    )

    @property
    def name(self):
        return "transfer_money"

    @property
    def description(self):
        return "Transfer money to a recipient"

    def start(self, bot: Bot):
        bot.reply("Welcome to the money transfer service!")
        bot.reply("Please follow the instructions to complete the transfer.")

        ask_amount = linguista.actions.Ask(self.amount, prompt="How much money would you like to transfer?",
                                           id="ask-amount")

        return ask_amount >> self.validate_amount

    @linguista.action()
    def validate_amount(self, bot: linguista.Bot, amount: int):
        if amount < 0:
            bot.reply("Amount must be positive")
            return linguista.actions.Next("ask-amount")

        # TODO: ask recipient


bot = linguista.Bot(session_id="test-session")

flow = TransferMoneyFlow()

print(flow)

next_actions = flow.start(bot)
print(next_actions)

prompt = render_prompt(available_flows=[flow], current_flow=flow, current_slot=flow.amount,
                       current_conversation=[],
                       latest_user_message="50€")

print(prompt)

print(flow.get_slots())

print(flow.get_slot("amount"))

from linguista.llm.openai import OpenAI
openai_llm = OpenAI()
response = openai_llm(prompt)

print(response)

from linguista.tracker import RedisTracker
from linguista.enums import Role

"""
tracker = RedisTracker()
tracker.add_message_to_conversation("test-session", Role.USER, "Hello")
conversation = tracker.get_conversation("test-session")
print(conversation)
"""

session_id = "test-session"

bot = Bot(session_id=session_id)

response_stream = bot.message("i want to make a transfer", stream=True)

for response in response_stream:
    print(response)
