"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context.conditions import Conditions, Unsatisfiable


@pytest.fixture
def conditions():
    return Conditions.create_from_instance(
        {
            "East": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
            "West": {"Fn::Equals": ["us-west-2", {"Ref": "AWS::Region"}]},
            "NotEast": {"Fn::Not": [{"Condition": "East"}]},
            "Either": {"Fn::Or": [{"Condition": "East"}, {"Condition": "West"}]},
        },
        {},
        {},
    )


@pytest.mark.parametrize(
    "regions,status",
    [
        (["us-east-1"], {"East": False}),
        (["us-west-2"], {"West": False}),
        (["us-east-1"], {"NotEast": True}),
        (["us-east-1", "us-west-2"], {"East": True, "West": True}),
        (["us-east-1", "us-west-2"], {"Either": False}),
    ],
)
def test_impossible_region_scenarios(conditions, regions, status):
    with pytest.raises(Unsatisfiable):
        conditions.evolve_for_regions(regions).evolve(status)


def test_region_binding_after_resource_condition(conditions):
    evolved = conditions.evolve({"Either": True}).evolve_for_regions(["us-east-1"])
    assert evolved.evolve({"East": True, "West": False})
    with pytest.raises(Unsatisfiable):
        evolved.evolve({"West": True})
    assert evolved.is_reachable("West", True)


def test_unknown_regions_remain_possible(conditions):
    assert conditions.evolve_for_regions(["eu-west-1"]).evolve(
        {"East": False, "West": False, "NotEast": True}
    )
    assert conditions.evolve_for_regions([]) is conditions
