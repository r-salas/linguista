import enum
from typing import Annotated

import linguista


class MoneyTransferRecipient(enum.Enum):
    Ruben = "Rubén"
    Alicia = "Alicia"
    Enrique = "Enrique"


def validate_amount_to_transfer(amount: float, bot: linguista.Bot):
    if amount < 0:
        raise linguista.BadSlotValue("Amount to transfer must be positive")
    return amount


@linguista.event("session_start")
def session_start(bot: linguista.Bot, meta):
    bot.session["customer_id"] = meta["customer_id"]
    bot.session["money"] = 1000


@linguista.flow("transfer_money", "Transfer money to someone")
def transfer_money_to_someone(bot: linguista.Bot,
                              amount: Annotated[float, linguista.Slot(callback=validate_amount_to_transfer)],
                              recipient: MoneyTransferRecipient):
    print(f"Transfering {amount} to {recipient}")
    bot.reply("Money transfered. Thank you!")
    bot.session["money"] -= amount


@linguista.flow("get_current_money", "Get how much money you have")
def get_current_money(bot: linguista.Bot):
    print("Getting current money")
    bot.reply(f"You have {bot.session['money']} euros")
    bot.flows.call("get_last_transactions", limit=5)


@linguista.flow("get_last_transactions", "Get the last transactions")
def get_last_transactions(limit: int = 10):
    print(f"Getting last {limit} transactions")
