"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context.context import Map


@pytest.mark.parametrize(
    "name,get_key_1,get_key_2,expected",
    [
        ("Valid get", "A", "B", ["C"]),
        ("Invalid first key", "B", "B", KeyError()),
        ("Invalid second key", "A", "C", KeyError()),
    ],
)
def test_mapping_value(name, get_key_1, get_key_2, expected):
    mapping = Map({"A": {"B": "C"}})

    if isinstance(expected, Exception):
        with pytest.raises(type(expected)):
            list(mapping.find_in_map(get_key_1, get_key_2))
    else:
        assert list(mapping.find_in_map(get_key_1, get_key_2)) == expected
