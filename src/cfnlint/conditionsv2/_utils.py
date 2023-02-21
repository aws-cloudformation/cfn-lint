import hashlib
import json


class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "_value"):
            return obj._value


def get_hash(obj):
    """Return a hash of an object"""
    return hashlib.sha1(
        json.dumps(obj, sort_keys=True, cls=ObjectEncoder).encode("utf-8")
    ).hexdigest()
