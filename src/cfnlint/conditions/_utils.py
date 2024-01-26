"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import hashlib
import json


class ObjectEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, "_value"):
            # pylint: disable=protected-access
            return o._value
        return o


def get_hash(o):
    """Return a hash of an object"""
    return hashlib.sha1(
        json.dumps(o, sort_keys=True, cls=ObjectEncoder).encode("utf-8")
    ).hexdigest()
