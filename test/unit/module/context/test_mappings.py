"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context._mappings import Map, Mappings, _MappingSecondaryKey


@pytest.mark.parametrize(
    "name,get_key_1,get_key_2,expected",
    [
        ("Valid get", "A", "B", ["C"]),
        ("Invalid first key", "B", "B", KeyError()),
        ("Invalid second key", "A", "C", KeyError()),
    ],
)
def test_mapping_value(name, get_key_1, get_key_2, expected):
    mapping = Map.create_from_dict({"A": {"B": "C"}})

    if isinstance(expected, Exception):
        with pytest.raises(type(expected)):
            list(mapping.find_in_map(get_key_1, get_key_2))
    else:
        assert list(mapping.find_in_map(get_key_1, get_key_2)) == expected


def test_transforms():
    mapping = Map.create_from_dict({"A": {"Fn::Transform": "C"}})

    assert mapping.keys.get("A").is_transform is True

    mapping = Map.create_from_dict({"Fn::Transform": {"B": "C"}})

    assert mapping.is_transform is True

    mapping = Mappings.create_from_dict({"Fn::Transform": {"B": {"C": "D"}}})

    assert mapping.is_transform is True


@pytest.mark.parametrize(
    "name,mappings,expected",
    [
        (
            "Valid mappings",
            {
                "A": {"B": {"C": "D"}},
                "1": {"2": {"3": "4"}},
                "Z": [],
                "9": {"8": []},
                "M": {"N": {"O": {"P": "Q"}}},
            },
            Mappings(
                {
                    "A": Map({"B": _MappingSecondaryKey({"C": "D"})}),
                    "1": Map({"2": _MappingSecondaryKey({"3": "4"})}),
                    "Z": Map({}),
                    "9": Map({"8": _MappingSecondaryKey({})}),
                    "M": Map({"N": _MappingSecondaryKey({})}),
                }
            ),
        ),
        (
            "Valid mappings with transforms",
            {
                "A": {"Fn::Transform": "MyTransform"},
                "1": {"2": {"Fn::Transform": "MyTransform"}},
            },
            Mappings(
                {
                    "A": Map({}, True),
                    "1": Map({"2": _MappingSecondaryKey({}, True)}),
                }
            ),
        ),
        (
            "Valid mappings with transforms for mappings",
            {
                "Fn::Transform": "MyTransform",
            },
            Mappings({}, True),
        ),
        (
            "Invalid mappings with wrong types",
            {
                "A": {True: {"C": "foo"}},
                "1": {"2": {False: "foo"}},
            },
            Mappings(
                {
                    "A": Map({}, False),
                    "1": Map({"2": _MappingSecondaryKey({}, False)}),
                }
            ),
        ),
    ],
)
def test_mapping_creation(name, mappings, expected):
    results = Mappings.create_from_dict(mappings)

    assert results == expected, f"{name!r} failed got {results!r}"
