#
#
#   API Booking
#
#


import datetime
import linguista

from typing import Optional


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

    def start(self, bot: linguista.Bot):
        bot.reply("Welcome to the money transfer service!")
        bot.reply("Please follow the instructions to complete the transfer.")

        ask_amount = linguista.actions.Ask(self.amount, prompt="How much money would you like to transfer?",
                                           id="ask-amount")

        return ask_amount >> self.validate_amount

    @linguista.action
    def validate_amount(self, bot: linguista.Bot, amount: int):
        if amount < 0:
            bot.reply("Amount must be positive")
            return linguista.actions.Next("ask-amount")

        return self.ask_recipient

    @linguista.action
    def ask_recipient(self, bot: linguista.Bot, amount: int):
        return linguista.actions.Ask(self.recipient, prompt=f"Who would you like to transfer {amount}€ to?") >> self.ask_confirmation

    @linguista.action
    def ask_confirmation(self, bot: linguista.Bot, amount: int, recipient: str):
        ask_action = linguista.actions.Ask(self.transfer_confirmation,
                                           prompt=f"Are you sure you want to transfer {amount}€ to {recipient}?")
        return ask_action >> self.validate_confirmation

    @linguista.action
    def validate_confirmation(self, bot: linguista.Bot, transfer_confirmation: bool, amount: int, recipient: str):
        if transfer_confirmation:
            bot.reply("Transfer of ${} to {} completed".format(amount, recipient))
        else:
            bot.reply("Ok, I won't transfer the money")
