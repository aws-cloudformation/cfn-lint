"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.mappings.Configuration import Configuration
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = Configuration()
    yield rule


@pytest.fixture(scope="module")
def cfn():
    return Template(
        "",
        {},
        regions=["us-east-1"],
    )


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Empty is okay",
            {"MyMapping": {"Key": {"Value": "Foo"}}},
            [],
        ),
        (
            "Good key name",
            {"MyMapping": {"Foo-Bar": {"Value": "Foo"}}},
            [],
        ),
        (
            "Wrong type",
            [],
            [
                ValidationError(
                    "[] is not of type 'object'",
                    validator="type",
                    schema_path=deque(["type"]),
                    rule=Configuration(),
                )
            ],
        ),
        (
            "Bad mapping type",
            {"MyMapping": []},
            [
                ValidationError(
                    "[] is not of type 'object'",
                    validator="type",
                    schema_path=deque(["patternProperties", "^[a-zA-Z0-9]+$", "type"]),
                    rule=Configuration(),
                    path=deque(["MyMapping"]),
                )
            ],
        ),
        (
            "Bad key type",
            {"MyMapping": {"Key": []}},
            [
                ValidationError(
                    "[] is not of type 'object'",
                    validator="type",
                    schema_path=deque(
                        [
                            "patternProperties",
                            "^[a-zA-Z0-9]+$",
                            "patternProperties",
                            "^[a-zA-Z0-9.-]+$",
                            "type",
                        ]
                    ),
                    rule=Configuration(),
                    path=deque(
                        [
                            "MyMapping",
                            "Key",
                        ]
                    ),
                )
            ],
        ),
        (
            "Bad value type",
            {"MyMapping": {"Key": {"Value": {}}}},
            [
                ValidationError(
                    (
                        "{} is not of type 'string', 'boolean', "
                        "'integer', 'number', 'array'"
                    ),
                    validator="type",
                    schema_path=deque(
                        [
                            "patternProperties",
                            "^[a-zA-Z0-9]+$",
                            "patternProperties",
                            "^[a-zA-Z0-9.-]+$",
                            "patternProperties",
                            "^[a-zA-Z0-9]+$",
                            "type",
                        ]
                    ),
                    rule=Configuration(),
                    path=deque(["MyMapping", "Key", "Value"]),
                )
            ],
        ),
        (
            "Bad Name",
            {"MyMapping-1": {"Key": {"Value": "Foo"}}},
            [
                ValidationError(
                    "'MyMapping-1' does not match any of the regexes: '^[a-zA-Z0-9]+$'",
                    validator="additionalProperties",
                    schema_path=deque(["additionalProperties"]),
                    rule=Configuration(),
                    path=deque(["MyMapping-1"]),
                )
            ],
        ),
        (
            "Long key name",
            {"a" * 256: {"Key": {"Value": "Foo"}}},
            [
                ValidationError(
                    f"{'a'*256!r} is longer than 255",
                    validator="maxLength",
                    schema_path=deque(["propertyNames", "maxLength"]),
                    rule=None,  # empty because we didn't load child rules
                    path=deque(["a" * 256]),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, context, cfn):
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(rule.validate(validator, {}, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"
