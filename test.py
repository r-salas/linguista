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

    def start(self, bot: Bot):
        ...


flow = TransferMoneyFlow()

print(flow)
