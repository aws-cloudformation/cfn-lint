"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.context.context import Path
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.jsonschema._filter import FunctionFilter
from cfnlint.template import Template


@pytest.fixture(scope="module")
def filter():
    filter = FunctionFilter()
    yield filter


@pytest.fixture()
def template():
    template = Template(
        None,
        {
            "Parameters": {"MyParameter": {"Type": "String"}},
            "Conditions": {"Condition": {"Fn::Equals": [{"Ref": "MyParameter"}, ""]}},
        },
        ["us-east-1"],
    )
    yield template


@pytest.mark.parametrize(
    "name,instance,schema,path,functions,expected",
    [
        (
            "Don't validate dynamic references inside of function",
            "{{resolve:ssm:${AWS::AccountId}/${AWS::Region}/ac}}",
            {"enum": "Foo"},
            deque(["Foo", "Test", "Fn::Sub"]),
            [],
            [],
        ),
        (
            "Validate dynamic references",
            "{{resolve:ssm:secret}}",
            {"enum": "Foo"},
            deque(["Foo", "Test"]),
            [],
            [
                ("{{resolve:ssm:secret}}", {"dynamicReference": {"enum": "Foo"}}),
            ],
        ),
        (
            "Validate dynamic references with spaces",
            "{{ resolve:ssm:secret }}",
            {"enum": "Foo"},
            deque(["Foo", "Test"]),
            [],
            [
                (
                    "{{ resolve:ssm:secret }}",
                    {"dynamicReferenceSpaces": {"enum": "Foo"}},
                ),
            ],
        ),
        (
            "Detect raw pseudo-parameter string",
            "AWS::NoValue",
            {"type": "string"},
            deque(["Resources", "MyResource", "Properties", "Foo"]),
            [],
            [
                (
                    "AWS::NoValue",
                    {"rawPseudoParameter": {"type": "string"}},
                ),
            ],
        ),
        (
            "Skip pseudo-parameter when used inside Ref",
            "AWS::NoValue",
            {"type": "string"},
            deque(["Resources", "MyResource", "Properties", "Foo", "Ref"]),
            [],
            [
                (
                    "AWS::NoValue",
                    {"type": "string"},
                ),
            ],
        ),
        (
            "Skip non pseudo-parameter AWS:: string",
            "AWS::EC2::Instance",
            {"type": "string"},
            deque(["Resources", "MyResource", "Type"]),
            [],
            [
                (
                    "AWS::EC2::Instance",
                    {"type": "string"},
                ),
            ],
        ),
        (
            "Lack of functions returns the schema and instance",
            {
                "Foo": {"Ref": "AWS::NoValue"},
            },
            {"required": ["Foo"]},
            deque([]),
            [],
            [
                (
                    {
                        "Foo": {"Ref": "AWS::NoValue"},
                    },
                    {"required": ["Foo"]},
                ),
            ],
        ),
        (
            "Filtered schemas",
            {
                "Foo": {"Ref": "AWS::NoValue"},
            },
            {"required": ["Foo"]},
            deque([]),
            ["Ref", "Fn::If"],
            [
                (
                    {},
                    {"required": ["Foo"]},
                ),
                ({"Foo": {"Ref": "AWS::NoValue"}}, {"cfnLint": [""]}),
            ],
        ),
        (
            "Filtered schemas with list",
            [
                {
                    "Fn::If": [
                        "Condition",
                        {"Key": "1", "Value": "A"},
                        {"Ref": "AWS::NoValue"},
                    ]
                },
                {
                    "Key": "2",
                    "Value": "B",
                },
                {"Ref": "AWS::NoValue"},
            ],
            {"items": {"required": ["Key"]}},
            deque([]),
            ["Ref", "Fn::If"],
            [
                (
                    [
                        {
                            "Fn::If": [
                                "Condition",
                                {"Key": "1", "Value": "A"},
                                {"Ref": "AWS::NoValue"},
                            ]
                        },
                        {
                            "Key": "2",
                            "Value": "B",
                        },
                        {"Ref": "AWS::NoValue"},
                    ],
                    {"items": {"required": ["Key"]}, "cfnLint": [""]},
                ),
            ],
        ),
    ],
)
def test_filter(
    name,
    instance,
    schema,
    path,
    functions,
    expected,
    filter,
    template,
):
    context = create_context_for_template(template)
    validator = CfnTemplateValidator(
        context=context,
        cfn=template,
        schema=schema,
    )
    validator = validator.evolve(
        context=validator.context.evolve(
            path=Path(path),
            functions=functions,
        )
    )

    results = list(filter.filter(validator, instance, schema))

    assert len(results) == len(expected), f"For test {name} got {len(results)} results"

    for result, (exp_instance, exp_schema) in zip(results, expected):
        assert result[0] == exp_instance, f"For test {name} got {result[0]!r}"
        assert result[1] == exp_schema, f"For test {name} got {result[1]!r}"


def test_raw_pseudo_parameter_with_dynamic_references_disabled(template):
    """
    Pseudo-parameter detection must run even when the filter has
    validate_dynamic_references=False (e.g. CfnLintJsonSchema rules).
    """
    filter = FunctionFilter(validate_dynamic_references=False)

    context = create_context_for_template(template)
    schema = {"type": "string"}
    validator = CfnTemplateValidator(
        context=context,
        cfn=template,
        schema=schema,
    )
    validator = validator.evolve(
        context=validator.context.evolve(
            path=Path(deque(["Resources", "MyResource", "Properties", "Foo"])),
            functions=[],
        )
    )

    results = list(filter.filter(validator, "AWS::NoValue", schema))

    assert len(results) == 1
    assert results[0][0] == "AWS::NoValue"
    assert results[0][1] == {"rawPseudoParameter": schema}
