"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.context.conditions._conditions import Conditions
from cfnlint.context.conditions.exceptions import Unsatisfiable
from cfnlint.template import Template


def template():
    return {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Parameters": {
            "Environment": {
                "Type": "String",
                "Default": "dev",
                "AllowedValues": ["dev", "prod"],
            },
            "Name": {
                "Type": "String",
                "Default": "bi",
                "AllowedValues": ["bi", "ai"],
            },
            "AmiId": {
                "Type": "String",
                "Default": "",
            },
        },
        "Conditions": {
            "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
            "IsNotUsEast1": {"Fn::Not": [{"Condition": "IsUsEast1"}]},
            "IsUsWest2": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-west-2"]},
            "IsProd": {"Fn::Equals": [{"Ref": "Environment"}, "prod"]},
            "IsDev": {"Fn::Equals": [{"Ref": "Environment"}, "dev"]},
            "IsAmiProvided": {"Fn::Not": [{"Fn::Equals": [{"Ref": "AmiId"}, ""]}]},
            "IsAi": {"Fn::Equals": [{"Ref": "Name"}, "ai"]},
            "IsBi": {"Fn::Equals": [{"Ref": "Name"}, "bi"]},
            "IsUsEast1OrUsWest2": {
                "Fn::Or": [
                    {"Condition": "IsUsEast1"},
                    {"Condition": "IsUsWest2"},
                ]
            },
            "IsUsEast1AndProd": {
                "Fn::And": [
                    {"Condition": "IsUsEast1"},
                    {"Condition": "IsProd"},
                ]
            },
            "IsStaticTrue": {"Fn::Equals": [1, "1"]},
            "IsStaticFalse": {"Fn::Equals": [1, "2"]},
            "TwoObjects": {
                "Fn::Equals": [
                    {"Ref": "Environment"},
                    {"Ref": "AWS::Region"},
                ]
            },
            "TwoObjectsSameHash": {
                "Fn::Equals": [
                    {"Ref": "AWS::Region"},
                    {"Ref": "Environment"},
                ]
            },
            "BadAwsFn": {"Ref": "Foo"},
            "BadFn": {"Key": "Foo"},
            "BadNotList": {"Fn::And": "Foo"},
            "UseBadFn": {"Condition": "BadFn"},
            "UseBadCondition": {"Condition": []},
            "EqualsTooLong": {"Fn::Equals": ["a", "b", "c"]},
            "EqualsWrongTypes": {"Fn::Equals": ["a", []]},
            "NotWithTwoItems": {
                "Fn::Not": [
                    {"Condition": "IsAi"},
                    {"Condition": "IsBi"},
                ]
            },
        },
    }


def test_conditions():
    cfn = Template(None, template(), regions=["us-east-1"])
    context = create_context_for_template(cfn)

    assert len(context.conditions.conditions) == 22
    assert context.conditions.conditions["IsStaticTrue"].fn_equals.is_static is True
    assert context.conditions.conditions["IsStaticFalse"].fn_equals.is_static is False
    assert (
        context.conditions.conditions["TwoObjects"].fn_equals.hash
        == context.conditions.conditions["TwoObjectsSameHash"].fn_equals.hash
    )
    assert context.conditions.conditions["TwoObjects"].fn_equals.is_static is None

    for k in [
        "IsUsEast1",
        "IsNotUsEast1",
        "IsUsWest2",
        "IsUsEast1OrUsWest2",
        "IsUsEast1AndProd",
    ]:
        assert context.conditions.conditions[k].is_region is True

    for k in ["IsAmiProvided", "IsProd", "IsDev", "IsAi", "IsBi"]:
        assert context.conditions.conditions[k].is_region is False

    for k in [
        "BadAwsFn",
        "BadFn",
        "BadNotList",
        "UseBadCondition",
        "EqualsTooLong",
        "EqualsWrongTypes",
        "NotWithTwoItems",
    ]:
        assert context.conditions.conditions[k].fn_equals.left.instance is None
        assert context.conditions.conditions[k].fn_equals.right.instance is None
        assert context.conditions.conditions[k].fn_equals.is_static is None
        assert context.conditions.conditions[k].is_region is False

    assert (
        context.conditions.conditions["UseBadFn"].condition.fn_equals.left.instance
        is None
    )
    assert (
        context.conditions.conditions["UseBadFn"].condition.fn_equals.right.instance
        is None
    )
    assert (
        context.conditions.conditions["UseBadFn"].condition.fn_equals.is_static is None
    )


@pytest.mark.parametrize(
    "current_status,new_status,expected",
    [
        ({}, {}, {}),
        ({"IsUsEast1": True}, {}, {"IsUsEast1": True}),
        (
            {"IsUsEast1": True},
            {"IsUsEast1": False},
            Unsatisfiable(
                new_status={"IsUsEast1": False}, current_status={"IsUsEast1": True}
            ),
        ),
        (
            {"IsUsEast1": True},
            {"IsNotUsEast1": True},
            Unsatisfiable(
                new_status={"IsNotUsEast1": True},
                current_status={"IsUsEast1": True},
            ),
        ),
        (
            {"IsUsEast1": False, "IsUsWest2": False},
            {"IsUsEast1OrUsWest2": True},
            Unsatisfiable(
                new_status={"IsUsEast1OrUsWest2": True},
                current_status={"IsUsEast1": True},
            ),
        ),
        (
            {"IsDev": False},
            {"IsProd": False},
            Unsatisfiable(new_status={"IsProd": False}, current_status={"IsDev": True}),
        ),
        ({}, {"BadFn": True}, {"BadFn": True}),
        ({}, {"BadFn": False}, {"BadFn": False}),
    ],
)
def test_condition_status(current_status, new_status, expected):
    cfn = Template(None, template(), regions=["us-east-1"])
    context = create_context_for_template(cfn)

    context = context.evolve(conditions=context.conditions.evolve(current_status))

    if isinstance(expected, Exception):
        with pytest.raises(ValueError):
            context.conditions.evolve(new_status)
    else:
        context = context.evolve(conditions=context.conditions.evolve(new_status))
        assert context.conditions.status == expected


@pytest.mark.parametrize(
    "current_status,instance,expected",
    [
        ({}, {"Foo": "Bar"}, [({"Foo": "Bar"}, {})]),
        (
            {},
            {"Fn::If": ["IsUsEast1", {"Foo": "Foo"}, {"Bar": "Bar"}]},
            [
                ({"Foo": "Foo"}, {"IsUsEast1": True}),
                ({"Bar": "Bar"}, {"IsUsEast1": False}),
            ],
        ),
        (
            {
                "IsUsEast1": True,
            },
            {"Fn::If": ["IsUsEast1", {"Foo": "Foo"}, {"Bar": "Bar"}]},
            [
                ({"Foo": "Foo"}, {"IsUsEast1": True}),
            ],
        ),
        (
            {
                "IsUsEast1": False,
            },
            {"Fn::If": ["IsUsEast1", {"Foo": "Foo"}, {"Bar": "Bar"}]},
            [
                ({"Bar": "Bar"}, {"IsUsEast1": False}),
            ],
        ),
        (
            {},
            {"Ref": "AWS::NoValue"},
            [
                (None, {}),
            ],
        ),
        (
            {},
            [{"Foo": {"Fn::If": ["IsUsEast1", "Foo", "Bar"]}}],
            [
                ([{"Foo": {"Fn::If": ["IsUsEast1", "Foo", "Bar"]}}], {}),
            ],
        ),
        (
            {},
            [{"Fn::If": ["IsUsEast1", {"Foo": "Bar"}, {"Ref": "AWS::NoValue"}]}],
            [
                ([{"Foo": "Bar"}], {"IsUsEast1": True}),
                ([], {"IsUsEast1": False}),
            ],
        ),
        (
            {"IsUsEast1": True, "IsProd": True},
            {
                "A": {"Fn::If": ["IsUsEast1AndProd", 1, 2]},
                "B": {"Fn::If": ["IsAi", 10, 11]},
            },
            [
                (
                    {"A": 1, "B": 10},
                    {
                        "IsUsEast1": True,
                        "IsProd": True,
                        "IsUsEast1AndProd": True,
                        "IsAi": True,
                    },
                ),
                (
                    {"A": 1, "B": 11},
                    {
                        "IsUsEast1": True,
                        "IsProd": True,
                        "IsUsEast1AndProd": True,
                        "IsAi": False,
                    },
                ),
            ],
        ),
        (
            {},
            {
                "A": {"Fn::If": ["IsUsEast1AndProd", 1]},
            },
            [
                (
                    {"A": {"Fn::If": ["IsUsEast1AndProd", 1]}},
                    {},
                ),
            ],
        ),
    ],
)
def test_evolve_from_instance(current_status, instance, expected):
    cfn = Template(None, template(), regions=["us-east-1"])
    context = create_context_for_template(cfn)

    context = context.evolve(
        conditions=context.conditions.evolve(current_status),
        functions=["Fn::If", "Ref"],
    )

    results = list(context.conditions.evolve_from_instance(instance, context))
    assert len(results) == len(expected)
    for result, expected_result in zip(results, expected):
        assert result[0] == expected_result[0]
        assert result[1].status == expected_result[1]


def test_condition_failures():
    with pytest.raises(ValueError):
        Conditions.create_from_instance([], {}, {})
