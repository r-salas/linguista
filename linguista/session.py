#
#
#   Session
#
#

class Session:

    def __init__(self, session_id: str, tracker):
        self.session_id = session_id
        self.tracker = tracker

        self._slots = tracker.get_slots(session_id)

    @property
    def id(self):
        return self.session_id

    def get_slot(self, slot_name: str):
        return self._slots.get(slot_name)

    def set_slot(self, slot_name: str, value):
        self._slots[slot_name] = value
        self.tracker.update_slot(self.session_id, slot_name, value)

    def delete_slot(self, slot_name: str):
        self._slots.pop(slot_name, None)
        self.tracker.delete_slot(self.session_id, slot_name)
