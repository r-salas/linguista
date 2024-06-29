#
#
#
#
#

import os
import uuid

import linguista

from linguista.actions import Ask, Reply, CallFlow, End


class CheckExpenseCurrentMonthFlow(linguista.Flow):

    @property
    def name(self):
        return "check_expense_current_month"

    @property
    def description(self):
        return "Check the expense of the current month"

    @linguista.action
    def start(self):
        return Reply("Welcome to the expense checking service!") >> Reply("Please wait while we retrieve your expense...") >> self.check_expense_current_month

    @linguista.action
    def check_expense_current_month(self):
        return Reply("Your expense for the current month is 500€")


class GetAccountInfoFlow(linguista.Flow):

    @property
    def name(self):
        return "get_account_info"

    @property
    def description(self):
        return "Get account information"

    @linguista.action
    def start(self):
        return Reply("Welcome to the account information service!") >> Reply("Please wait while we retrieve your account information...") >> CallFlow("check_balance") >> self.get_account_info

    @linguista.action
    def get_account_info(self):
        return Reply("Your account number is 1234567890")


class CheckBalanceFlow(linguista.Flow):

    @property
    def name(self):
        return "check_balance"

    @property
    def description(self):
        return "Check the balance of the account"

    @linguista.action
    def start(self):
        return Reply("Welcome to the balance checking service!") >> Reply("Please wait while we retrieve your balance...") >> self.check_balance

    @linguista.action
    def check_balance(self):
        return Reply("Your balance is 1000€")


class TransferMoneyFlow(linguista.Flow):

    amount = linguista.FlowSlot(
        name="amount",
        description="Amount of money to transfer",
        type=float,
    )

    recipient = linguista.FlowSlot(
        name="recipient-name",
        description="Recipient name",
        type=linguista.types.Categorical(["Alice", "Bob", "Charlie"]),
    )

    notes = linguista.FlowSlot(
        name="notes",
        description="Notes for the transfer",
        type=str,
        required=False
    )

    email_invoice = linguista.FlowSlot(
        name="email-invoice",
        description="Whether or not send an invoice to the recipient",
        type=bool,
    )

    transfer_confirmation = linguista.FlowSlot(
        name="transfer-confirmation",
        description="Confirm the transfer",
        type=bool,
        ask_before_filling=True,
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
    def validate_amount(self, tracker: linguista.Tracker):
        amount = tracker.get_slot(self.amount)

        if amount < 0:
            return Reply("Amount must be positive") >> self.ask_amount

        return self.ask_recipient

    @linguista.action
    def ask_recipient(self):
        ask_recipient = linguista.actions.Ask(self.recipient, prompt="Who would you like to transfer to?")

        return ask_recipient >> self.ask_notes

    @linguista.action
    def ask_notes(self):
        ask_notes = Ask(self.notes, prompt="Any notes for the transfer?")

        return ask_notes >> self.ask_email_invoice

    @linguista.action
    def ask_email_invoice(self):
        ask_email_invoice = Ask(self.email_invoice, prompt="Would you like to send an invoice to the recipient?")

        return ask_email_invoice >> self.ask_confirmation

    @linguista.action
    def ask_confirmation(self, tracker: linguista.Tracker):
        amount = tracker.get_slot(self.amount)
        recipient = tracker.get_slot(self.recipient)

        ask_confirmation = linguista.actions.Ask(self.transfer_confirmation, prompt=f"Are you sure you want to transfer {amount}€ to {recipient}?")

        return ask_confirmation >> self.validate_confirmation

    @linguista.action
    def validate_confirmation(self, tracker: linguista.Tracker):
        transfer_confirmation = tracker.get_slot(self.transfer_confirmation)

        if transfer_confirmation:
            amount = tracker.get_slot(self.amount)
            recipient = tracker.get_slot(self.recipient)
            notes = tracker.get_slot(self.notes)
            email_invoice = tracker.get_slot(self.email_invoice)

            return Reply(f"Transferring {amount}€ to {recipient} with notes: {notes} and email invoice: {email_invoice}") >> self.complete_transfer
        else:
            return Reply("Transfer cancelled")

    @linguista.action
    def complete_transfer(self):
        return Reply("Transfer completed")


session_id = str(uuid.uuid4())

gpt_3_5 = linguista.OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    model="gpt-3.5-turbo",
)

gpt_4o = linguista.OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    model="gpt-4o",
)

claude_haiku = linguista.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

claude_sonnet = linguista.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    model="claude-3-5-sonnet-20240620"
)

claude_opus = linguista.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    model="claude-3-opus-20240229"
)

bot = linguista.Bot(
    session_id=session_id,
    flows=[
        TransferMoneyFlow(),
        CheckBalanceFlow(),
        GetAccountInfoFlow(),
        CheckExpenseCurrentMonthFlow()
    ],
    model=claude_haiku
)

try:
    while True:
        user_message = input(">>> ")
        response_stream = bot.message(user_message, stream=True)

        for response in response_stream:
            print(response)
except KeyboardInterrupt:
    pass
