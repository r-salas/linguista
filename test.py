#
#
#
#
#

import linguista

from linguista import Bot, FlowSlot
from linguista.actions import Ask, Reply


class TransferMoneyFlow(linguista.Flow):

    amount = linguista.FlowSlot(
        name="amount",
        description="Amount of money to transfer",
        type=float,
        # TODO: add default value
    )

    recipient = linguista.FlowSlot(
        name="recipient-name",
        description="Recipient name",
        type=linguista.types.Categorical(["Alice", "Bob", "Charlie"])
    )

    transfer_confirmation = linguista.FlowSlot(
        name="transfer-confirmation",
        description="Confirm the transfer",
        type=bool
    )

    @property
    def name(self):
        return "transfer_money"

    @property
    def description(self):
        return "Transfer money to a recipient"

    @linguista.action
    def start(self):
        return Reply("Welcome to the money transfer service!") >> Reply("Please follow the instructions to complete the transfer.") >> self.ask_amount

    @linguista.action
    def ask_amount(self):
        ask_amount = Ask(self.amount, prompt="How much money would you like to transfer?")

        return ask_amount >> self.validate_amount

    @linguista.action
    def validate_amount(self):
        amount = self.get_slot_value(self.amount)

        if amount < 0:
            return Reply("Amount must be positive") >> self.ask_amount

        return self.ask_recipient

    @linguista.action
    def ask_recipient(self):
        ask_recipient = linguista.actions.Ask(self.recipient, prompt="Who would you like to transfer to?")

        return ask_recipient >> self.ask_confirmation

    @linguista.action
    def ask_confirmation(self):
        amount = self.get_slot_value(self.amount)
        recipient = self.get_slot_value(self.recipient)

        ask_confirmation = linguista.actions.Ask(self.transfer_confirmation, prompt=f"Are you sure you want to transfer {recipient} to {amount}?")

        return ask_confirmation >> self.validate_confirmation

    @linguista.action
    def validate_confirmation(self):
        transfer_confirmation = self.get_slot_value(self.transfer_confirmation)

        if transfer_confirmation:
            return Reply("Transfer completed")
        else:
            return Reply("Transfer cancelled")


bot = linguista.Bot(
    session_id="test-session",
    flows=[
        TransferMoneyFlow
    ]
)

response_stream = bot.message("I want to transfer money", stream=True)

for response in response_stream:
    print(response)
