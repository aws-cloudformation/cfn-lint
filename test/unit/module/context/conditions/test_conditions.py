"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
from unittest.mock import patch

import pytest
from sympy import Not, Symbol
from sympy.logic.inference import satisfiable

from cfnlint.api import ManualArgs, lint
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
        (
            {},
            [
                "a",
                "b",
                {"Fn::If": ["IsDev", "c", {"Ref": "AWS::NoValue"}]},
                {"Fn::If": ["IsProd", "d", {"Ref": "AWS::NoValue"}]},
            ],
            [
                (["a", "b", "c"], {"IsDev": True, "IsProd": False}),
                (["a", "b", "d"], {"IsDev": False, "IsProd": True}),
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
    result_set = {(str(r[0]), tuple(sorted(r[1].status.items()))) for r in results}
    expected_set = {(str(e[0]), tuple(sorted(e[1].items()))) for e in expected}
    assert result_set == expected_set


def test_mutually_exclusive_equals_without_allowed_values():
    """Two Fn::Equals comparing the same Ref to different literals can never
    both be true, even when the parameter has no AllowedValues or is a
    pseudo-parameter (issue #4799)."""
    cfn = Template(
        None,
        {
            "Parameters": {
                "Source": {"Type": "String", "Default": "ipv4"},
            },
            "Conditions": {
                "UseIpv4": {"Fn::Equals": [{"Ref": "Source"}, "ipv4"]},
                "UseIpv6": {"Fn::Equals": [{"Ref": "Source"}, "ipv6"]},
                "UseAcct1": {"Fn::Equals": [{"Ref": "AWS::AccountId"}, "111111111111"]},
                "UseAcct2": {"Fn::Equals": [{"Ref": "AWS::AccountId"}, "222222222222"]},
            },
        },
        regions=["us-east-1"],
    )
    conditions = create_context_for_template(cfn).conditions

    # each condition is still individually reachable
    assert conditions.is_reachable("UseIpv4", True) is True
    assert conditions.is_reachable("UseIpv6", True) is True
    assert conditions.is_reachable("UseAcct1", True) is True

    # ...but the mutually exclusive pairs can never both be true
    with pytest.raises(Unsatisfiable):
        conditions.evolve({"UseIpv4": True, "UseIpv6": True})
    with pytest.raises(Unsatisfiable):
        conditions.evolve({"UseAcct1": True, "UseAcct2": True})


_REGION_FLAGS = {
    "us-east-1": {"A": "true", "B": "false"},
    "us-west-2": {"A": "false", "B": "true"},
}


def _find_in_map_equals(*keys, value="true"):
    return {"Fn::Equals": [{"Fn::FindInMap": ["Flags", *keys]}, value]}


@pytest.mark.parametrize(
    "name,mappings,condition_a,condition_b,exclusive",
    [
        (
            "Mapping keyed by AWS::Region",
            {"Flags": _REGION_FLAGS},
            _find_in_map_equals({"Ref": "AWS::Region"}, "A"),
            _find_in_map_equals({"Ref": "AWS::Region"}, "B"),
            True,
        ),
        (
            "Mapping keyed by a parameter at the second level",
            {"Flags": {"A": {"dev": "true", "prod": "false"}, "B": {"prod": "true"}}},
            _find_in_map_equals("A", {"Ref": "Env"}),
            _find_in_map_equals("B", {"Ref": "Env"}),
            True,
        ),
        (
            "A Ref value with no entry is not a value that makes it true",
            {
                "Flags": {
                    "us-east-1": {"A": "true"},
                    "us-west-2": {"A": "false", "B": "true"},
                }
            },
            _find_in_map_equals({"Ref": "AWS::Region"}, "A"),
            _find_in_map_equals({"Ref": "AWS::Region"}, "B"),
            True,
        ),
        (
            "Fn::Equals on the Ref and a mapping keyed by it",
            {"Flags": _REGION_FLAGS},
            {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
            _find_in_map_equals({"Ref": "AWS::Region"}, "B"),
            True,
        ),
        (
            "Fn::Equals on the Ref with a value the mapping makes true",
            {"Flags": _REGION_FLAGS},
            {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-west-2"]},
            _find_in_map_equals({"Ref": "AWS::Region"}, "B"),
            False,
        ),
        (
            "A key where both are true",
            {
                "Flags": {
                    **_REGION_FLAGS,
                    "eu-west-1": {"A": "true", "B": "true"},
                }
            },
            _find_in_map_equals({"Ref": "AWS::Region"}, "A"),
            _find_in_map_equals({"Ref": "AWS::Region"}, "B"),
            False,
        ),
        (
            "Mapping values that are not strings",
            {
                "Flags": {
                    "us-east-1": {"A": True, "B": False},
                    "us-west-2": {"A": False, "B": True},
                }
            },
            _find_in_map_equals({"Ref": "AWS::Region"}, "A"),
            _find_in_map_equals({"Ref": "AWS::Region"}, "B"),
            False,
        ),
        (
            "Compared to a value that is not a string",
            {"Flags": _REGION_FLAGS},
            _find_in_map_equals({"Ref": "AWS::Region"}, "A", value=True),
            _find_in_map_equals({"Ref": "AWS::Region"}, "B", value=True),
            False,
        ),
        (
            "Top-level key that is not a string",
            {
                "Flags": {
                    "111111111111": {"A": "true", "B": "false"},
                    222222222222: {"A": "true", "B": "true"},
                }
            },
            _find_in_map_equals({"Ref": "AWS::AccountId"}, "A"),
            _find_in_map_equals({"Ref": "AWS::AccountId"}, "B"),
            False,
        ),
        (
            "Fn::FindInMap with a DefaultValue",
            {"Flags": _REGION_FLAGS},
            _find_in_map_equals({"Ref": "AWS::Region"}, "A", {"DefaultValue": "true"}),
            _find_in_map_equals({"Ref": "AWS::Region"}, "B", {"DefaultValue": "true"}),
            False,
        ),
        (
            "Mapping built by Fn::Transform",
            {"Flags": {**_REGION_FLAGS, "Fn::Transform": {"Name": "AWS::Include"}}},
            _find_in_map_equals({"Ref": "AWS::Region"}, "A"),
            _find_in_map_equals({"Ref": "AWS::Region"}, "B"),
            False,
        ),
        (
            "Both keys are Refs",
            {"Flags": _REGION_FLAGS},
            _find_in_map_equals({"Ref": "AWS::Region"}, {"Ref": "Env"}),
            _find_in_map_equals({"Ref": "AWS::Region"}, "B"),
            False,
        ),
        (
            "Mapping that does not exist",
            {},
            _find_in_map_equals({"Ref": "AWS::Region"}, "A"),
            _find_in_map_equals({"Ref": "AWS::Region"}, "B"),
            False,
        ),
        (
            "Mappings that are not an object",
            [],
            _find_in_map_equals({"Ref": "AWS::Region"}, "A"),
            _find_in_map_equals({"Ref": "AWS::Region"}, "B"),
            False,
        ),
        (
            "Mappings section built by Fn::Transform",
            {"Flags": _REGION_FLAGS, "Fn::Transform": {"Name": "AWS::Include"}},
            _find_in_map_equals({"Ref": "AWS::Region"}, "A"),
            _find_in_map_equals({"Ref": "AWS::Region"}, "B"),
            False,
        ),
        (
            "Mapping name that is not a string",
            {"Flags": _REGION_FLAGS},
            {
                "Fn::Equals": [
                    {"Fn::FindInMap": [{"Ref": "Env"}, {"Ref": "AWS::Region"}, "A"]},
                    "true",
                ]
            },
            {
                "Fn::Equals": [
                    {"Fn::FindInMap": [{"Ref": "Env"}, {"Ref": "AWS::Region"}, "B"]},
                    "true",
                ]
            },
            False,
        ),
        (
            "Top-level entry that is not an object",
            {"Flags": {**_REGION_FLAGS, "eu-west-1": "true"}},
            _find_in_map_equals({"Ref": "AWS::Region"}, "A"),
            _find_in_map_equals({"Ref": "AWS::Region"}, "B"),
            False,
        ),
        (
            "Static top-level key with no entry",
            {"Flags": {"A": {"dev": "true", "prod": "false"}}},
            _find_in_map_equals("A", {"Ref": "Env"}),
            _find_in_map_equals("B", {"Ref": "Env"}),
            False,
        ),
    ],
)
def test_find_in_map_mutual_exclusion(
    name, mappings, condition_a, condition_b, exclusive
):
    """Two Fn::Equals that depend on the same Ref through Fn::FindInMap
    cannot both be true when no mapping key makes both true."""
    cfn = Template(
        None,
        {
            "Parameters": {"Env": {"Type": "String"}},
            "Mappings": mappings,
            "Conditions": {"A": condition_a, "B": condition_b},
            "Resources": {},
        },
        regions=["us-east-1"],
    )
    conditions = create_context_for_template(cfn).conditions

    assert conditions.is_reachable("A", True) is True, name
    assert conditions.is_reachable("B", True) is True, name
    if exclusive:
        with pytest.raises(Unsatisfiable):
            conditions.evolve({"A": True, "B": True})
    else:
        conditions.evolve({"A": True, "B": True})


def test_referenced_equals_paired_once():
    """A condition's equals includes those of every condition it references,
    so the same Fn::Equals is reachable many times over. Pairing it on each
    visit makes the clause count quadratic in the references rather than in
    the distinct Fn::Equals (issue #4984)."""
    regions = 30
    cfn = Template(
        None,
        {
            "Conditions": {
                **{
                    f"IsRegion{i}": {
                        "Fn::Equals": [{"Ref": "AWS::Region"}, f"region-{i}"]
                    }
                    for i in range(regions)
                },
                **{
                    f"InGroup{i}": {
                        "Fn::Or": [
                            {"Condition": f"IsRegion{(i + j) % regions}"}
                            for j in range(10)
                        ]
                    }
                    for i in range(regions)
                },
            },
            "Resources": {},
        },
        regions=["us-east-1"],
    )
    conditions = create_context_for_template(cfn).conditions

    assert len(conditions.cnf.data) < 2 * regions * regions

    # the mutual exclusion from #4799 still holds
    assert conditions.is_reachable("IsRegion0", True) is True
    assert conditions.is_reachable("IsRegion1", True) is True
    with pytest.raises(Unsatisfiable):
        conditions.evolve({"IsRegion0": True, "IsRegion1": True})

    # a group is satisfiable, and excludes a region none of its members allow
    in_group = conditions.evolve({"InGroup0": True})
    assert in_group.is_reachable("IsRegion0", True) is True
    assert in_group.is_reachable("IsRegion20", True) is False


def test_inline_equals_mutual_exclusion():
    """An Fn::Equals reached only by traversing another condition is still
    paired, so an enclosing Fn::Or stays mutually exclusive with a sibling
    condition on the same Ref (issue #4984)."""
    cfn = Template(
        None,
        {
            "Conditions": {
                "IsEast": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
                "IsElsewhere": {
                    "Fn::Or": [
                        {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-west-2"]},
                        {"Fn::Equals": [{"Ref": "AWS::Region"}, "eu-west-1"]},
                    ]
                },
            },
            "Resources": {},
        },
        regions=["us-east-1"],
    )
    conditions = create_context_for_template(cfn).conditions

    assert conditions.is_reachable("IsEast", True) is True
    assert conditions.is_reachable("IsElsewhere", True) is True

    with pytest.raises(Unsatisfiable):
        conditions.evolve({"IsEast": True, "IsElsewhere": True})


def test_allowed_values_covered_through_reference():
    """The Or that forces a fully covered AllowedValues parameter is still
    emitted when the covering Fn::Equals are only reachable by traversing
    another condition. Deduping on the Ref rather than on the Fn::Equals
    would leave a value uncovered and drop the Or (issue #4984)."""
    cfn = Template(
        None,
        {
            "Parameters": {
                "Stage": {"Type": "String", "AllowedValues": ["beta", "prod"]},
            },
            "Conditions": {
                "IsBetaOrProd": {
                    "Fn::Or": [
                        {"Fn::Equals": [{"Ref": "Stage"}, "beta"]},
                        {"Fn::Equals": [{"Ref": "Stage"}, "prod"]},
                    ]
                },
            },
            "Resources": {},
        },
        regions=["us-east-1"],
    )
    conditions = create_context_for_template(cfn).conditions

    # Stage can only be beta or prod, so a condition covering both is always true
    assert conditions.is_reachable("IsBetaOrProd", True) is True
    assert conditions.is_reachable("IsBetaOrProd", False) is False


def test_find_in_map_implication():
    """When every mapping key that makes one Fn::Equals true also makes the
    other true, the first implies the second."""
    cfn = Template(
        None,
        {
            "Mappings": {"Flags": {"us-east-1": {"A": "true", "B": "true"}}},
            "Conditions": {
                "A": _find_in_map_equals({"Ref": "AWS::Region"}, "A"),
                "B": _find_in_map_equals({"Ref": "AWS::Region"}, "B"),
                "IsEast": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
            },
            "Resources": {},
        },
        regions=["us-east-1"],
    )
    conditions = create_context_for_template(cfn).conditions

    assert conditions.evolve({"A": True}).is_reachable("B", False) is False
    assert conditions.evolve({"A": True}).is_reachable("IsEast", False) is False
    assert conditions.evolve({"IsEast": True}).is_reachable("A", False) is False
    assert conditions.is_reachable("A", False) is True


def test_allowed_values_with_duplicates():
    """A parameter whose AllowedValues repeat one value can only take it."""
    cfn = Template(
        None,
        {
            "Parameters": {
                "AppType": {"Type": "String", "AllowedValues": ["Public", "Public"]}
            },
            "Conditions": {"IsPublic": {"Fn::Equals": [{"Ref": "AppType"}, "Public"]}},
            "Resources": {},
        },
        regions=["us-east-1"],
    )
    conditions = create_context_for_template(cfn).conditions

    assert conditions.is_reachable("IsPublic", False) is False


@pytest.mark.parametrize(
    "conditions_section",
    [
        {"A": _find_in_map_equals({"Ref": "AWS::Region"}, "A")},
        {
            "A": _find_in_map_equals({"Ref": "AWS::Region"}, "A"),
            "B": _find_in_map_equals({"Ref": "AWS::Region"}, "B"),
        },
    ],
    ids=["alone", "with another Fn::Equals on the Ref"],
)
def test_find_in_map_never_true(conditions_section):
    """A Fn::Equals that no mapping key makes true is false, whether or not
    another Fn::Equals depends on the same Ref."""
    cfn = Template(
        None,
        {
            "Mappings": {"Flags": {"us-east-1": {"A": "false", "B": "true"}}},
            "Conditions": conditions_section,
            "Resources": {},
        },
        regions=["us-east-1"],
    )
    conditions = create_context_for_template(cfn).conditions

    assert conditions.is_reachable("A", True) is False


def test_allowed_values_with_other_literals():
    """A parameter with AllowedValues takes one of its AllowedValues, so a
    comparison against a value outside the list can never be true
    (issue #5075).  CloudFormation rejects such a value before creating
    anything, so the compared value is not part of the domain."""
    cfn = Template(
        None,
        {
            "Parameters": {"Env": {"Type": "String", "AllowedValues": ["dev", "prod"]}},
            "Conditions": {
                "IsDev": {"Fn::Equals": [{"Ref": "Env"}, "dev"]},
                "IsProd": {"Fn::Equals": [{"Ref": "Env"}, "prod"]},
                "IsTest": {"Fn::Equals": [{"Ref": "Env"}, "test"]},
            },
            "Resources": {},
        },
        regions=["us-east-1"],
    )
    conditions = create_context_for_template(cfn).conditions

    assert conditions.is_reachable("IsTest", True) is False
    assert conditions.is_reachable("IsTest", False) is True
    with pytest.raises(Unsatisfiable):
        conditions.evolve({"IsTest": True})
    with pytest.raises(Unsatisfiable):
        conditions.evolve({"IsDev": False, "IsProd": False, "IsTest": False})
    # Comparisons against allowed values stay reachable both ways.
    conditions.evolve({"IsDev": True})
    conditions.evolve({"IsProd": True})


def test_single_allowed_value():
    """With one AllowedValue, a comparison against it is always true and a
    comparison against any other value is always false (issue #5075)."""
    cfn = Template(
        None,
        {
            "Parameters": {"Env": {"Type": "String", "AllowedValues": ["prod"]}},
            "Conditions": {
                "IsProd": {"Fn::Equals": [{"Ref": "Env"}, "prod"]},
                "IsDev": {"Fn::Equals": [{"Ref": "Env"}, "dev"]},
            },
            "Resources": {},
        },
        regions=["us-east-1"],
    )
    conditions = create_context_for_template(cfn).conditions

    assert conditions.is_reachable("IsProd", False) is False
    assert conditions.is_reachable("IsDev", True) is False
    with pytest.raises(Unsatisfiable):
        conditions.evolve({"IsProd": False})
    with pytest.raises(Unsatisfiable):
        conditions.evolve({"IsDev": True})
    conditions.evolve({"IsProd": True, "IsDev": False})


def test_static_equals_condition():
    """A constant Fn::Equals folds to a constant in the solver, so pinning
    the condition to its impossible value is unsatisfiable (issue #5074).
    CloudFormation compares operands as strings, so [true, "true"] is
    always true while [false, "true"] is always false."""
    cfn = Template(
        None,
        {
            "Conditions": {
                "NeverTrue": {"Fn::Equals": [False, "true"]},
                "AlwaysTrue": {"Fn::Equals": [True, "true"]},
            },
            "Resources": {},
        },
        regions=["us-east-1"],
    )
    conditions = create_context_for_template(cfn).conditions

    assert conditions.is_reachable("NeverTrue", True) is False
    assert conditions.is_reachable("AlwaysTrue", False) is False
    with pytest.raises(Unsatisfiable):
        conditions.evolve({"NeverTrue": True})
    with pytest.raises(Unsatisfiable):
        conditions.evolve({"AlwaysTrue": False})
    conditions.evolve({"NeverTrue": False, "AlwaysTrue": True})


@pytest.mark.parametrize("allowed_values", [5, True, "dev,prod", {"dev": "prod"}])
def test_allowed_values_not_a_list(allowed_values):
    """AllowedValues that is not a list adds no constraint."""
    cfn = Template(
        None,
        {
            "Parameters": {"Env": {"Type": "String", "AllowedValues": allowed_values}},
            "Conditions": {
                "IsDev": {"Fn::Equals": [{"Ref": "Env"}, "dev"]},
                "IsProd": {"Fn::Equals": [{"Ref": "Env"}, "prod"]},
            },
            "Resources": {},
        },
        regions=["us-east-1"],
    )
    conditions = create_context_for_template(cfn).conditions

    assert set(conditions.conditions) == {"IsDev", "IsProd"}
    conditions.evolve({"IsDev": False, "IsProd": False})


def test_values_with_the_same_effect_share_a_variable():
    """Mapping keys that make the same Fn::Equals true share one variable,
    so the clause count follows the distinct lookups, not the keys."""
    keys = [f"key{i}" for i in range(200)]
    cfn = Template(
        None,
        {
            "Parameters": {"Env": {"Type": "String"}},
            "Mappings": {
                "Flags": {
                    k: {f"F{j}": "true" if i % 4 == j else "false" for j in range(4)}
                    for i, k in enumerate(keys)
                }
            },
            "Conditions": {
                f"C{j}": _find_in_map_equals({"Ref": "Env"}, f"F{j}") for j in range(4)
            },
            "Resources": {},
        },
        regions=["us-east-1"],
    )
    conditions = create_context_for_template(cfn).conditions

    assert len(conditions.cnf.data) < 50
    with pytest.raises(Unsatisfiable):
        conditions.evolve({"C0": True, "C1": True})
    conditions.evolve({"C0": False, "C1": False, "C2": False, "C3": False})


def test_condition_failures():
    with pytest.raises(ValueError):
        Conditions.create_from_instance([], {}, {})


def test_condition_non_string_names_skipped():
    # Regression test for https://github.com/aws-cloudformation/cfn-lint/issues/4813
    # A non-string condition logical ID must not crash create_from_instance
    # (sympy Symbol requires a string name).  The invalid name is skipped
    # here and reported by rule E8001.
    conditions = Conditions.create_from_instance(
        {123: {"Fn::Equals": ["a", "b"]}, "IsValid": {"Fn::Equals": ["a", "b"]}},
        {},
        {},
    )
    assert 123 not in conditions.conditions
    assert "IsValid" in conditions.conditions


def test_is_reachable_unknown_condition():
    cfn = Template(None, template(), regions=["us-east-1"])
    context = create_context_for_template(cfn)

    # An unknown condition is conservatively considered reachable.
    assert context.conditions.is_reachable("DoesNotExist", True) is True
    assert context.conditions.is_reachable("DoesNotExist", False) is True


def test_is_reachable_fact_vs_assumption():
    cfn = Template(None, template(), regions=["us-east-1"])
    base = create_context_for_template(cfn).conditions

    # A fact (e.g. a resource Condition or enclosing Fn::If) forces the value,
    # so the opposite is unreachable.
    fact = base.evolve({"IsUsEast1": True})
    assert fact.is_reachable("IsUsEast1", True) is True
    assert fact.is_reachable("IsUsEast1", False) is False

    # An assumption from scenario enumeration does not force anything, so both
    # values remain reachable.
    assumed = base.evolve({"IsUsEast1": True}, assumed=True)
    assert assumed.is_reachable("IsUsEast1", True) is True
    assert assumed.is_reachable("IsUsEast1", False) is True


def test_is_reachable_implication():
    cfn = Template(None, template(), regions=["us-east-1"])
    base = create_context_for_template(cfn).conditions

    # IsUsEast1AndProd = IsUsEast1 AND IsProd, so pinning it True as a fact
    # forces both operands True; their False values are unreachable.
    fact = base.evolve({"IsUsEast1AndProd": True})
    assert fact.is_reachable("IsUsEast1", True) is True
    assert fact.is_reachable("IsUsEast1", False) is False
    assert fact.is_reachable("IsProd", False) is False

    # As an assumption it forces nothing.
    assumed = base.evolve({"IsUsEast1AndProd": True}, assumed=True)
    assert assumed.is_reachable("IsUsEast1", False) is True


def test_or_of_and_pairs_does_not_explode():
    """An Fn::Or of Fn::And pairs is encoded with a linear number of
    clauses (issue #4737). Converting it to CNF by distribution would
    create 2^30 clauses."""
    pairs = 30
    cfn = Template(
        None,
        {
            "Parameters": {
                "Stage": {"Type": "String", "AllowedValues": ["beta", "prod"]},
            },
            "Conditions": {
                "IsDeployed": {
                    "Fn::Or": [
                        {
                            "Fn::And": [
                                {"Fn::Equals": [{"Ref": "AWS::Region"}, f"region-{i}"]},
                                {"Fn::Equals": [{"Ref": "Stage"}, "prod"]},
                            ]
                        }
                        for i in range(pairs)
                    ]
                },
                "IsProd": {"Fn::Equals": [{"Ref": "Stage"}, "prod"]},
            },
            "Resources": {},
        },
        regions=["us-east-1"],
    )
    conditions = create_context_for_template(cfn).conditions

    assert len(conditions.cnf.data) < 50 * pairs

    deployed = conditions.evolve({"IsDeployed": True})
    assert deployed.is_reachable("IsProd", True) is True
    assert deployed.is_reachable("IsProd", False) is False

    with pytest.raises(Unsatisfiable):
        conditions.evolve({"IsDeployed": True, "IsProd": False})

    not_prod = conditions.evolve({"IsProd": False})
    assert not_prod.is_reachable("IsDeployed", True) is False


def test_each_set_of_pins_is_solved_once():
    """Every Fn::If and condition scenario asks whether its pins are
    satisfiable, and most ask about the same pins. Solving each set once
    keeps the solver calls from growing with the number of Fn::If
    (issue #4991)."""
    cfn = Template(None, template(), regions=["us-east-1"])
    base = create_context_for_template(cfn).conditions

    with patch(
        "cfnlint.context.conditions._conditions.satisfiable", wraps=satisfiable
    ) as solver:
        first = base.evolve({"IsUsEast1": True})
        base.evolve({"IsUsEast1": True})
        base.evolve({"IsUsEast1": True}, assumed=True)
        assert solver.call_count == 1

        # The same pins reached in a different order or from another branch.
        first.evolve({"IsProd": True})
        base.evolve({"IsProd": True}).evolve({"IsUsEast1": True})
        base.evolve({"IsProd": True, "IsUsEast1": True})
        assert solver.call_count == 3

        # A reachability question is a set of pins too.
        assert first.is_reachable("IsProd", True) is True
        assert first.evolve({"IsProd": True}).is_reachable("IsUsEast1", True)
        assert solver.call_count == 3

        # An unsatisfiable set is remembered as well.
        for _ in range(2):
            with pytest.raises(Unsatisfiable):
                first.evolve({"IsUsWest2": True})
        assert solver.call_count == 4


def test_pins_keep_facts_and_assumptions_apart():
    cfn = Template(None, template(), regions=["us-east-1"])
    base = create_context_for_template(cfn).conditions

    # Same statuses after the second pin, but only the fact forces IsUsEast1.
    assumed = base.evolve({"IsUsEast1": True}, assumed=True).evolve({"IsProd": True})
    fact = base.evolve({"IsUsEast1": True}).evolve({"IsProd": True})
    assert assumed.status == fact.status
    assert assumed.is_reachable("IsUsEast1", False) is True
    assert fact.is_reachable("IsUsEast1", False) is False


def test_cnf_is_the_template_clauses_plus_one_per_pin():
    cfn = Template(None, template(), regions=["us-east-1"])
    base = create_context_for_template(cfn).conditions
    clauses = len(base.cnf.data)

    pinned = base.evolve({"IsUsEast1": True}, assumed=True).evolve({"IsProd": True})
    assert len(pinned.cnf.data) == clauses + 2
    assert len(pinned.hard_cnf.data) == clauses + 1

    # Each access is a new copy, so changing one does not reach later answers:
    # this evolve would raise Unsatisfiable if Not(IsProd) had been kept.
    pinned.cnf.add_prop(Not(Symbol("IsProd")))
    assert len(pinned.cnf.data) == clauses + 2
    pinned.evolve({"IsAi": True})


def _alarms_reusing_conditions(alarms):
    return {
        "Parameters": {"Stage": {"Type": "String", "AllowedValues": ["beta", "prod"]}},
        "Conditions": {
            "IsProd": {"Fn::Equals": [{"Ref": "Stage"}, "prod"]},
            "IsEast": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
            "IsProdEast": {
                "Fn::And": [{"Condition": "IsProd"}, {"Condition": "IsEast"}]
            },
        },
        "Resources": {
            f"Alarm{i}": {
                "Type": "AWS::CloudWatch::Alarm",
                # Fn::If inside a conditional resource evolves the resource's
                # Conditions, so the cache must reach evolved objects too.
                "Condition": "IsProd",
                "Properties": {
                    "Namespace": "Service",
                    "MetricName": f"Metric{i}",
                    "Statistic": "Sum",
                    "ComparisonOperator": "GreaterThanThreshold",
                    "EvaluationPeriods": 1,
                    "Threshold": {"Fn::If": ["IsProdEast", 1, 10]},
                    "Period": {"Fn::If": ["IsEast", 300, 60]},
                },
            }
            for i in range(alarms)
        },
    }


def test_solver_calls_do_not_grow_with_reused_conditions():
    """Resources that reuse the same conditions in Fn::If ask the same
    questions, so a whole lint solves the same number of pin sets however
    many such resources there are (issue #4991)."""
    calls = []
    for alarms in (5, 20):
        with patch(
            "cfnlint.context.conditions._conditions.satisfiable", wraps=satisfiable
        ) as solver:
            matches = lint(
                json.dumps(_alarms_reusing_conditions(alarms)),
                config=ManualArgs(regions=["us-east-1"]),
            )
        assert matches == []
        calls.append(solver.call_count)

    assert calls[0] > 0
    assert calls[0] == calls[1]


def _subscription_with_exclusive_conditions(count):
    """An SNS subscription missing its required Protocol, with one optional
    property per condition. Every condition compares the same parameter to a
    different value, so at most one of them is true."""
    properties = [
        ("DeliveryPolicy", {"healthyRetryPolicy": {"numRetries": 3}}),
        ("Endpoint", "arn:aws:lambda:us-east-1:123456789012:function:handler"),
        ("FilterPolicy", {"type": ["order"]}),
        ("FilterPolicyScope", "MessageAttributes"),
        ("RawMessageDelivery", True),
        (
            "RedrivePolicy",
            {"deadLetterTargetArn": "arn:aws:sqs:us-east-1:123456789012:dlq"},
        ),
        ("Region", "us-east-1"),
        (
            "ReplayPolicy",
            {"pointType": "Timestamp", "startingPoint": "2024-01-01T00:00:00Z"},
        ),
        ("SubscriptionRoleArn", "arn:aws:iam::123456789012:role/sns"),
    ][:count]
    return {
        "Parameters": {"Env": {"Type": "String", "Default": "none"}},
        "Conditions": {
            f"IsEnv{i}": {"Fn::Equals": [{"Ref": "Env"}, f"env{i}"]}
            for i in range(count)
        },
        "Resources": {
            "Topic": {"Type": "AWS::SNS::Topic"},
            "Subscription": {
                "Type": "AWS::SNS::Subscription",
                "Properties": {
                    "TopicArn": {"Ref": "Topic"},
                    **{
                        name: {"Fn::If": [f"IsEnv{i}", value, {"Ref": "AWS::NoValue"}]}
                        for i, (name, value) in enumerate(properties)
                    },
                },
            },
        },
    }


@pytest.mark.parametrize("count", [7, 9])
def test_scenarios_skip_unsatisfiable_combinations(count):
    """Combinations that pin two exclusive conditions True are never
    satisfiable, so they must not use up the scenario limit before the
    satisfiable ones are reached (issue #5047)."""
    cfn = Template(None, _subscription_with_exclusive_conditions(count))
    context = create_context_for_template(cfn)
    instance = cfn.template["Resources"]["Subscription"]["Properties"]

    scenarios = [
        s.status for _, s in context.conditions.evolve_from_instance(instance, context)
    ]

    # One scenario with every condition False, and one per condition True.
    assert len(scenarios) == count + 1
    assert sorted(sum(s.values()) for s in scenarios) == [0] + [1] * count


def test_scenarios_limit_counts_satisfiable_scenarios():
    """Independent conditions are all satisfiable together, so the limit is
    reached with exactly that many scenarios."""
    count = 8
    cfn = Template(
        None,
        {
            "Parameters": {
                f"P{i}": {"Type": "String", "Default": "a"} for i in range(count)
            },
            "Conditions": {
                f"C{i}": {"Fn::Equals": [{"Ref": f"P{i}"}, "a"]} for i in range(count)
            },
        },
    )
    context = create_context_for_template(cfn)
    instance = [{"Fn::If": [f"C{i}", i, {"Ref": "AWS::NoValue"}]} for i in range(count)]

    scenarios = [
        tuple(sorted(s.status.items()))
        for _, s in context.conditions.evolve_from_instance(instance, context)
    ]

    assert len(scenarios) == context.conditions._max_scenarios
    assert len(set(scenarios)) == len(scenarios)


def test_scenarios_skip_solving_the_only_possible_value():
    """When pinning a condition True is unsatisfiable, pinning it False is
    satisfiable without asking the solver."""
    cfn = Template(None, _subscription_with_exclusive_conditions(3))
    context = create_context_for_template(cfn)
    instance = cfn.template["Resources"]["Subscription"]["Properties"]

    with patch(
        "cfnlint.context.conditions._conditions.satisfiable", wraps=satisfiable
    ) as solver:
        scenarios = list(context.conditions.evolve_from_instance(instance, context))

    assert len(scenarios) == 4
    # 12 sets of pins are evaluated; the three False pins that follow an
    # unsatisfiable True pin are not solved.
    assert solver.call_count == 9


@pytest.mark.parametrize("count", [7, 9])
def test_required_property_with_exclusive_conditions(count):
    """E3003 reports the missing Protocol however many exclusive conditions
    the other properties use (issue #5047)."""
    matches = lint(
        json.dumps(_subscription_with_exclusive_conditions(count)),
        config=ManualArgs(regions=["us-east-1"]),
    )

    assert [(m.rule.id, m.message) for m in matches] == [
        ("E3003", "'Protocol' is a required property")
    ]


@pytest.mark.parametrize("attempts,expected", [(17, 1), (16, 0)])
def test_scenarios_stop_at_the_pin_attempt_limit(attempts, expected):
    """The first scenario takes at most two pins per condition: with nine
    exclusive conditions, the first condition True and then each later one
    tried True and False."""
    cfn = Template(None, _subscription_with_exclusive_conditions(9))
    context = create_context_for_template(cfn)
    instance = cfn.template["Resources"]["Subscription"]["Properties"]
    object.__setattr__(context.conditions, "_max_pin_attempts", attempts)

    scenarios = list(context.conditions.evolve_from_instance(instance, context))

    assert len(scenarios) == expected
