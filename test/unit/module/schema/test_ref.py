"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging

import pytest

from cfnlint.schema._schema import Schema

LOGGER = logging.getLogger("cfnlint.schema.manager")
LOGGER.disabled = True


@pytest.mark.parametrize(
    "name,resource_schema,expected",
    [
        (
            "Standard ref",
            {
                "additionalProperties": False,
                "createOnlyProperties": [],
                "primaryIdentifier": ["/properties/One"],
                "properties": {"One": {"type": "string"}, "Two": {"type": "boolean"}},
                "readOnlyProperties": [],
                "typeName": "Foo::Foo::Foo",
                "writeOnlyProperties": [],
            },
            {"type": "string"},
        ),
        (
            "Standard with multiple identifiers",
            {
                "additionalProperties": False,
                "createOnlyProperties": [],
                "primaryIdentifier": ["/properties/One", "/properties/Two"],
                "properties": {"One": {"type": "integer"}, "Two": {"type": "boolean"}},
                "readOnlyProperties": [],
                "typeName": "Foo::Foo::Foo",
                "writeOnlyProperties": [],
            },
            {"type": "string"},
        ),
    ],
)
def test_schema(name, resource_schema, expected):

    schema = Schema(resource_schema)

    assert schema.ref == expected, f"{name!r} test got {schema.ref!r}"
