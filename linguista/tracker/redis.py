#
#
#   Redis tracker
#
#

import json
from typing import Optional, Sequence, Tuple

from .base import Tracker
from ..enums import Role
from ..actions import Action

try:
    import redis
except ImportError:
    redis = None


def _get_redis_conversation_key(session_id: str) -> str:
    return f"linguista:conversation:{session_id}"


def _get_redis_current_flow_key(session_id: str) -> str:
    return f"linguista:current:{session_id}"


def _get_redis_current_slot_key(session_id: str) -> str:
    return f"linguista:current_slot:{session_id}"


def _get_redis_current_actions_key(session_id: str) -> str:
    return f"linguista:current_actions:{session_id}"


def _get_redis_slots_key(session_id: str) -> str:
    return f"linguista:slots:{session_id}"


def _get_redis_flow_slots_key(session_id: str, flow_name: str) -> str:
    return f"linguista:flow_slots:{session_id}:{flow_name}"


class RedisTracker(Tracker):

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        if redis is None:
            raise ImportError("Please install the 'linguista[redis]' package to use the Redis tracker.")

        self.host = host
        self.port = port
        self.db = db

        self._client = redis.Redis(host=host, port=port, db=db)

    def get_conversation(self, session_id: str):
        conversation_key = _get_redis_conversation_key(session_id)
        conversation = self._client.lrange(conversation_key, 0, -1)

        if conversation is None:
            return []

        conversation_json = [json.loads(message) for message in conversation]
        return [{"role": Role(message["role"]), "message": message["message"]} for message in conversation_json]

    def add_message_to_conversation(self, session_id: str, role: Role, message: str):
        conversation_key = _get_redis_conversation_key(session_id)
        self._client.rpush(conversation_key, json.dumps({"role": role.value, "message": message}))
        self._client.expire(conversation_key, 60 * 60 * 24)  # FIXME: Make this configurable

    def get_slot(self, session_id: str, slot_name: str):
        slots_key = _get_redis_slots_key(session_id)
        slot = self._client.hget(slots_key, slot_name)

        if slot is None:
            return None

        return slot.decode()

    def get_flow_slot(self, session_id: str, flow_name: str, slot_name: str):
        slots_key = _get_redis_flow_slots_key(session_id, flow_name)
        slot = self._client.hget(slots_key, slot_name)

        if slot is None:
            return None

        return slot.decode()

    def get_flow_slots(self, session_id: str, flow_name: str):
        slots_key = _get_redis_flow_slots_key(session_id, flow_name)
        slots = self._client.hgetall(slots_key)

        if slots is None:
            return {}

        return {key.decode(): value.decode() for key, value in slots.items()}

    def set_flow_slot(self, session_id: str, flow_name: str, slot_name: str, slot_value: str):
        slots_key = _get_redis_flow_slots_key(session_id, flow_name)
        self._client.hset(slots_key, slot_name, slot_value)

    def set_slot(self, session_id: str, slot_name: str, slot_value: str):
        slots_key = _get_redis_slots_key(session_id)
        self._client.hset(slots_key, slot_name, slot_value)

    def delete_slot(self, session_id: str, slot_name: str):
        slots_key = _get_redis_slots_key(session_id)
        self._client.hdel(slots_key, slot_name)

    def delete_flow_slot(self, session_id: str, flow_name: str, slot_name: str):
        slots_key = _get_redis_flow_slots_key(session_id, flow_name)
        self._client.hdel(slots_key, slot_name)

    def delete_flow_slots(self, session_id: str):
        slots_key = _get_redis_flow_slots_key(session_id, "*")

        pipe = self._client.pipeline()
        for key in self._client.scan_iter(slots_key):
            pipe.delete(key)
        pipe.execute()

    def save_current_actions(self, session_id: str, actions_with_flows: Sequence[Tuple["Action", str]]):
        current_actions_key = _get_redis_current_actions_key(session_id)

        to_save = [(action.to_dict(), flow) for action, flow in actions_with_flows]
        self._client.set(current_actions_key, json.dumps(to_save))

    def get_current_actions(self, session_id: str) -> Sequence[Tuple["Action", str]]:
        current_actions_key = _get_redis_current_actions_key(session_id)
        current_actions_json_str = self._client.get(current_actions_key)

        if current_actions_json_str is None:
            return []

        return [(Action.from_dict(action_dict), flow) for action_dict, flow in json.loads(current_actions_json_str)]

    def delete_current_actions(self, session_id: str):
        current_actions_key = _get_redis_current_actions_key(session_id)
        self._client.delete(current_actions_key)
