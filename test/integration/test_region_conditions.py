"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from pathlib import Path

import pytest

from cfnlint import lint


@pytest.mark.parametrize(
    "fixture,regions,rule,expected",
    [
        ("a", ["us-east-1"], "E3019", 0),
        ("a", ["us-west-2"], "E3019", 2),
        ("a", ["us-east-1", "us-west-2"], "E3019", 2),
        ("a", ["us-west-2", "us-east-1"], "E3019", 2),
        ("b", ["ca-west-1"], "E3628", 0),
        ("b", ["us-east-1", "ca-west-1"], "E3628", 0),
        ("c", ["ca-west-1"], "E3628", 0),
        ("c", ["ca-west-1", "us-east-1"], "E3628", 0),
        ("d", ["us-east-1"], "E3684", 0),
        ("d", ["cn-north-1", "us-east-1"], "E3684", 1),
        ("e", ["us-east-1"], "E3502", 0),
        ("e", ["us-west-2"], "E3502", 3),
        ("e", ["us-east-1", "us-west-2"], "E3502", 3),
    ],
)
def test_region_conditions(fixture, regions, rule, expected):
    template = Path(
        f"test/fixtures/templates/issues/region_conditions_{fixture}.yaml"
    ).read_text()

    results = lint(template, regions=regions)
    matches = [match for match in results if match.rule.id == rule]

    assert len(matches) == expected, matches
    assert all("Exception" not in match.message for match in results)
    assert not any(match.rule.id == "W1028" for match in results)
