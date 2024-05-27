#
#
#
#
#

import linguista
from linguista import Bot


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

    @linguista.action("validate-amount")
    def validate_amount(self, bot: linguista.Bot, amount: int):
        if amount < 0:
            bot.reply("Amount must be positive")
            return linguista.actions.Next("ask-amount")

        # TODO: ask recipient


bot = linguista.Bot()

flow = TransferMoneyFlow()

print(flow)

next_actions = flow.start(bot)
print(next_actions)
