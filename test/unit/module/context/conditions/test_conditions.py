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
