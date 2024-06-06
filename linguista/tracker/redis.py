#
#
#   Redis tracker
#
#

import json
from typing import Optional

from ..enums import Role
from .base import Tracker

try:
    import redis
except ImportError:
    redis = None


def _get_redis_conversation_key(session_id: str) -> str:
    return f"linguista:conversation:{session_id}"


def _get_redis_current_flow_key(session_id: str) -> str:
    return f"linguista:current:{session_id}"


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

        return [json.loads(message) for message in conversation]

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
