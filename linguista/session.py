#
#
#   Session
#
#

class Session:

    def __init__(self, session_id: str, tracker):
        self.session_id = session_id
        self.tracker = tracker

    @property
    def id(self):
        return self.session_id

    def get_slot(self, slot_name: str):
        ...

    def set_slot(self, slot_name: str, value):
        ...

    def delete_slot(self, slot_name: str):
        ...
