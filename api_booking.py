#
#
#   API Booking
#
#


import datetime
import linguista

from typing import Optional

def confirmation_prompt_for_create_booking(bot: linguista.Bot, )

@linguista.flow("create_booking", "Create a new booking")
def create_booking(bot: linguista.Bot, num_people: int, date_time: datetime.datetime, name: str, phone_number: str,
                   observations: Optional[str] = None,
                   confirmation: Annotated[bool, linguista.Slot(prompt="Do you confirm the booking?")]):
    ...
