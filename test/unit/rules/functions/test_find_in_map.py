"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from unittest.mock import MagicMock

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.context.context import Resource, Transforms
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.FindInMap import FindInMap
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = FindInMap()
    yield rule


@pytest.fixture(scope="module")
def cfn():
    return Template(
        "",
        {
            "Parameters": {
                "MyParameter": {
                    "Type": "String",
                    "AllowedValues": ["A", "B", "C"],
                }
            },
            "Resources": {"MyResource": Resource({"Type": "AWS::SSM::Parameter"})},
            "Mappings": {"A": {"B": {"C": "Value"}}},
        },
        regions=["us-east-1"],
    )


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


@pytest.mark.parametrize(
    "name,instance,schema,context_evolve,ref_mock_values,expected",
    [
        (
            "Valid Fn::FindInMap",
            {"Fn::FindInMap": ["A", "B", "C"]},
            {"type": "string"},
            {},
            None,
            [],
        ),
        (
            "Valid Fn::FindInMap with DefaultValue",
            {"Fn::FindInMap": ["A", "B", "C", {"DefaultValue": "D"}]},
            {"type": "string"},
            {},
            None,
            [],
        ),
        (
            "Invalid Fn::FindInMap 4th item not a DefaultValue object"
            " without transform",
            {"Fn::FindInMap": ["A", "B", "C", "notanobject"]},
            {"type": "string"},
            {},
            None,
            [
                ValidationError(
                    "'notanobject' is not of type 'object'",
                    path=deque(["Fn::FindInMap", 3]),
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            3,
                            "cfnContext",
                            "schema",
                            "type",
                        ]
                    ),
                    validator="fn_findinmap",
                ),
            ],
        ),
        (
            "Invalid Fn::FindInMap too long",
            {"Fn::FindInMap": ["foo", "bar", "key", {"DefaultValue": "D"}, "key2"]},
            {"type": "string"},
            {},
            None,
            [
                ValidationError(
                    "expected maximum item count: 4, found: 5",
                    path=deque(["Fn::FindInMap"]),
                    schema_path=deque(["cfnContext", "schema", "maxItems"]),
                    validator="fn_findinmap",
                ),
            ],
        ),
        (
            "Invalid Fn::FindInMap with wrong type",
            {"Fn::FindInMap": {"foo": "bar"}},
            {"type": "string"},
            {},
            None,
            [
                ValidationError(
                    "{'foo': 'bar'} is not of type 'array'",
                    path=deque(["Fn::FindInMap"]),
                    schema_path=deque(["cfnContext", "schema", "type"]),
                    validator="fn_findinmap",
                ),
            ],
        ),
        (
            "Invalid Fn::FindInMap with wrong function",
            {"Fn::FindInMap": [{"Fn::GetAtt": "MyResource.Arn"}, "foo", "bar"]},
            {"type": "string"},
            {},
            None,
            [
                ValidationError(
                    "{'Fn::GetAtt': 'MyResource.Arn'} is not of type 'string'",
                    path=deque(["Fn::FindInMap", 0]),
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            0,
                            "else",
                            "cfnContext",
                            "schema",
                            "type",
                        ]
                    ),
                    validator="fn_findinmap",
                ),
            ],
        ),
        (
            "Valid Fn::FindInMap",
            {"Fn::FindInMap": ["A", "B", "C", {"DefaultValue": "D"}]},
            {"type": "string"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            None,
            [],
        ),
        (
            "Invalid Fn::FindInMap options not of type object",
            {"Fn::FindInMap": ["A", "B", "C", []]},
            {"type": "string"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            None,
            [
                ValidationError(
                    "[] is not of type 'object'",
                    path=deque(["Fn::FindInMap", 3]),
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            3,
                            "cfnContext",
                            "schema",
                            "type",
                        ]
                    ),
                    validator="fn_findinmap",
                ),
            ],
        ),
        (
            "Invalid Fn::FindInMap default keyword doesn't exist",
            {"Fn::FindInMap": ["A", "B", "C", {}]},
            {"type": "string"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            None,
            [
                ValidationError(
                    "'DefaultValue' is a required property",
                    path=deque(["Fn::FindInMap", 3]),
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            3,
                            "cfnContext",
                            "schema",
                            "required",
                        ]
                    ),
                    validator="fn_findinmap",
                ),
            ],
        ),
        (
            "Invalid Fn::FindInMap with a Ref to a resource",
            {"Fn::FindInMap": ["A", {"Ref": "MyResource"}, "C"]},
            {"type": "string"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [ValidationError("Foo")],
            [
                ValidationError(
                    "Foo",
                    path=deque(["Fn::FindInMap", 1]),
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            1,
                            "then",
                            "cfnContext",
                            "schema",
                            "ref",
                        ]
                    ),
                    validator="ref",
                ),
            ],
        ),
        (
            "Invalid Fn::FindInMap with a bad map key",
            {"Fn::FindInMap": ["A", "C", "B"]},
            {"type": "string", "enum": ["Foo"]},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [ValidationError("Foo")],
            [
                ValidationError(
                    "'C' is not one of ['B'] for mapping 'A'",
                    path=deque(["Fn::FindInMap", 1]),
                    schema_path=deque([]),
                    validator="fn_findinmap",
                ),
            ],
        ),
        (
            "Valid Fn::FindInMap as the Ref could work",
            {"Fn::FindInMap": ["A", {"Ref": "MyParameter"}, "C"]},
            {"type": "string"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [],
            [],
        ),
        (
            "Valid Fn::FindInMap with a Ref to AWS::NoValue",
            {
                "Fn::FindInMap": [
                    "A",
                    "B",
                    "C",
                    {"DefaultValue": {"Ref": "AWS::NoValue"}},
                ]
            },
            {"type": "string"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [],
            [],
        ),
    ],
)
def test_validate(
    name,
    instance,
    schema,
    ref_mock_values,
    context_evolve,
    expected,
    rule,
    context,
    cfn,
):
    context = context.evolve(**context_evolve)
    ref_mock = MagicMock()
    ref_mock.return_value = iter(ref_mock_values or [])

    validator = CfnTemplateValidator({}).extend(validators={"ref": ref_mock})(
        context=context, cfn=cfn
    )

    errs = list(rule.fn_findinmap(validator, schema, instance, {}))

    if ref_mock_values is None:
        ref_mock.assert_not_called()
    else:
        assert ref_mock.call_count == len(ref_mock_values) or 1

    assert errs == expected, f"Test {name!r} got {errs!r}"


@pytest.fixture(scope="module")
def cfn_with_default():
    return Template(
        "",
        {
            "Parameters": {"Stage": {"Type": "String", "Default": ""}},
            "Resources": {"Dummy": Resource({"Type": "AWS::SNS::Topic"})},
            "Mappings": {"StageMap": {"gamma": {"TCS": "1"}, "prod": {"TCS": "2"}}},
        },
        regions=["us-east-1"],
    )


@pytest.fixture(scope="module")
def cfn_with_map_name_default():
    return Template(
        "",
        {
            "Parameters": {"MapStage": {"Type": "String", "Default": "beta"}},
            "Resources": {"Dummy": Resource({"Type": "AWS::SNS::Topic"})},
            "Mappings": {
                "beta": {"us-east-1": {"Other": "x"}},
                "gamma": {"us-east-1": {"TopicSuffix": "y", "Other": "z"}},
            },
        },
        regions=["us-east-1"],
    )


@pytest.mark.parametrize(
    "name,instance,expected_messages",
    [
        (
            # A Ref to a parameter's Default resolves to a value that a
            # deployer can override, so a missing mapping key isn't a
            # definite failure and must not be reported (was E1011).
            "Top level key from a parameter Default is not reported",
            {"Fn::FindInMap": ["StageMap", {"Ref": "Stage"}, "TCS"]},
            [],
        ),
        (
            "Second level key from a parameter Default is not reported",
            {"Fn::FindInMap": ["StageMap", "gamma", {"Ref": "Stage"}]},
            [],
        ),
        (
            # Hardcoded keys aren't overridable, so they are still validated.
            "Hardcoded top level key is still reported",
            {"Fn::FindInMap": ["StageMap", "typo", "TCS"]},
            ["'typo' is not one of ['gamma', 'prod'] for mapping 'StageMap'"],
        ),
        (
            "Hardcoded second level key is still reported",
            {"Fn::FindInMap": ["StageMap", "gamma", "typo"]},
            ["'typo' is not one of ['TCS'] for mapping 'StageMap' and key 'gamma'"],
        ),
    ],
)
def test_resolve_from_parameter_default(
    name, instance, expected_messages, rule, cfn_with_default
):
    """Values resolved from an overridable parameter Default shouldn't
    surface resolution errors, while hardcoded values still do."""
    context = create_context_for_template(cfn_with_default)
    validator = CfnTemplateValidator({}).extend(validators={})(
        context=context, cfn=cfn_with_default
    )

    # A constraining schema is required for resolution to run
    schema = {"type": "string", "pattern": "^[0-9]+$"}
    errs = list(rule.resolve(validator, schema, instance, {}))

    assert [err.message for err in errs] == expected_messages, (
        f"{name!r} failed and got errors {[e.message for e in errs]!r}"
    )


@pytest.mark.parametrize(
    "name,instance,expected_messages",
    [
        (
            # The map name resolves from a parameter Default that a deployer
            # can override, so missing keys under it aren't definite failures
            # and must not be reported (was E1011, issue #4802).
            "Literal keys with map name from a parameter Default are not reported",
            {"Fn::FindInMap": [{"Ref": "MapStage"}, "us-east-1", "TopicSuffix"]},
            [],
        ),
        (
            "Ref AWS::Region top key with map name from a parameter Default "
            "is not reported",
            {
                "Fn::FindInMap": [
                    {"Ref": "MapStage"},
                    {"Ref": "AWS::Region"},
                    "TopicSuffix",
                ]
            },
            [],
        ),
        (
            "Literal top key with map name from a parameter Default is not reported",
            {"Fn::FindInMap": [{"Ref": "MapStage"}, "us-east-1", "Missing"]},
            [],
        ),
        (
            # Hardcoded map names aren't overridable, so they are still
            # validated even when the keys are hardcoded too.
            "Hardcoded map name with missing second level key is still reported",
            {"Fn::FindInMap": ["beta", "us-east-1", "TopicSuffix"]},
            [
                "'TopicSuffix' is not one of ['Other'] "
                "for mapping 'beta' and key 'us-east-1'"
            ],
        ),
        (
            "Hardcoded map name with Ref AWS::Region top key is still reported",
            {
                "Fn::FindInMap": [
                    "beta",
                    {"Ref": "AWS::Region"},
                    "TopicSuffix",
                ]
            },
            [
                "'TopicSuffix' is not a second level key when "
                "{'Ref': 'AWS::Region'} is resolved for mapping 'beta'"
            ],
        ),
        (
            "Hardcoded unknown map name is still reported",
            {"Fn::FindInMap": ["typo", "us-east-1", "TopicSuffix"]},
            ["'typo' is not one of ['beta', 'gamma']"],
        ),
        (
            "Valid lookup against a hardcoded map name stays silent",
            {"Fn::FindInMap": ["beta", "us-east-1", "Other"]},
            [],
        ),
    ],
)
def test_resolve_map_name_from_parameter_default(
    name, instance, expected_messages, rule, cfn_with_map_name_default
):
    """A map name resolved from an overridable parameter Default shouldn't
    surface key resolution errors, while hardcoded map names still do."""
    context = create_context_for_template(cfn_with_map_name_default)
    validator = CfnTemplateValidator({}).extend(validators={})(
        context=context, cfn=cfn_with_map_name_default
    )

    # A constraining schema is required for resolution to run; the mapped
    # values are single lowercase letters, so constrain to those.
    schema = {"type": "string", "pattern": "^[a-z]$"}
    errs = list(rule.resolve(validator, schema, instance, {}))

    assert [err.message for err in errs] == expected_messages, (
        f"{name!r} failed and got errors {[e.message for e in errs]!r}"
    )
