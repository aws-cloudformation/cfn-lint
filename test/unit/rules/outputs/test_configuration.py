"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.outputs.Configuration import Configuration
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
            {},
            [],
        ),
        (
            "Proper output",
            {"MyOutput": {"Value": "Foo"}},
            [],
        ),
        (
            "Proper output with export",
            {
                "MyOutput": {
                    "Value": "Foo",
                    "Export": {"Name": "Foo"},
                }
            },
            [],
        ),
        (
            "wrong type",
            [],
            [
                ValidationError(
                    "[] is not of type 'object'",
                    validator="type",
                    schema_path=deque(["type"]),
                    rule=None,  # we didn't load child rules for testing
                )
            ],
        ),
        (
            "String type with MinValue",
            {
                "MyOutput": {
                    "Value": "Foo",
                    "Name": "String",
                }
            },
            [
                ValidationError(
                    "Additional properties are not allowed ('Name' was unexpected)",
                    validator="additionalProperties",
                    schema_path=deque(
                        [
                            "patternProperties",
                            "^[a-zA-Z0-9]+$",
                            "additionalProperties",
                        ]
                    ),
                    rule=Configuration(),
                    path=deque(["MyOutput", "Name"]),
                )
            ],
        ),
        (
            "Bad Name",
            {
                "Ref&3": {
                    "Value": "Foo",
                }
            },
            [
                ValidationError(
                    "'Ref&3' does not match any of the regexes: '^[a-zA-Z0-9]+$'",
                    validator="additionalProperties",
                    schema_path=deque(["additionalProperties"]),
                    rule=Configuration(),
                    path=deque(["Ref&3"]),
                )
            ],
        ),
        (
            "Long key name",
            {
                "a" * 256: {
                    "Value": "Foo",
                }
            },
            [
                ValidationError(
                    "expected maximum length: 255, found: 256",
                    validator="maxLength",
                    schema_path=deque(["propertyNames", "maxLength"]),
                    rule=None,  # none becuase we don't load child rule
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


def test_validate_bad_name_uses_e6004(context, cfn):
    # A non-alphanumeric output name fails as additionalProperties at
    # the section level; with child rules loaded it must map to E6004.
    from cfnlint.rules.outputs.Pattern import Pattern

    rule = Configuration()
    rule.child_rules["E6004"] = Pattern()
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(
        rule.validate(
            validator,
            {},
            {"Ref&3": {"Value": "Foo"}},
            {},
        )
    )

    assert len(errs) == 1
    assert errs[0].rule.id == "E6004"


def test_validate_nested_property_stays_e6001(context, cfn):
    # An unknown property inside an output is also an
    # additionalProperties failure, but nested under patternProperties;
    # it must stay E6001 even with child rules loaded.
    from cfnlint.rules.outputs.Pattern import Pattern

    rule = Configuration()
    rule.child_rules["E6004"] = Pattern()
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(
        rule.validate(
            validator,
            {},
            {"MyOutput": {"Value": "Foo", "Name": "String"}},
            {},
        )
    )

    assert len(errs) == 1
    assert errs[0].rule.id == "E6001"
