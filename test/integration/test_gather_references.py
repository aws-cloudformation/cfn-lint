"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
from pathlib import Path

import pytest

from cfnlint import lint


def test_literal_and_intrinsic_remote_properties():
    template = Path(
        "test/fixtures/templates/issues/cfn_gather_literal_references.yaml"
    ).read_text()

    matches = [
        match
        for match in lint(template, regions=["us-east-1"])
        if match.rule.id in {"E3502", "E3707", "E3709"}
    ]

    assert len(matches) == 1
    assert matches[0].path[:2] == ["Resources", "ControlMismatch"]
    assert matches[0].message == (
        "Source queue type 'standard' does not match destination queue type 'FIFO'"
    )


@pytest.mark.parametrize(
    "engine,encrypted,expected",
    [
        ("aurora-mysql", True, set()),
        ("aurora-postgresql", True, {"E3707"}),
        ("aurora-mysql", False, {"E3709"}),
    ],
)
def test_known_cluster_properties(engine, encrypted, expected):
    template = {
        "Resources": {
            "Cluster": {
                "Type": "AWS::RDS::DBCluster",
                "Properties": {"Engine": "aurora-mysql", "StorageEncrypted": True},
            },
            "Instance": {
                "Type": "AWS::RDS::DBInstance",
                "Properties": {
                    "Engine": engine,
                    "StorageEncrypted": encrypted,
                    "DBClusterIdentifier": {"Ref": "Cluster"},
                },
            },
        }
    }

    matches = [
        match
        for match in lint(json.dumps(template), regions=["us-east-1"])
        if match.rule.id in {"E3707", "E3709"}
    ]

    assert {match.rule.id for match in matches} == expected
    assert all(match.path[:2] == ["Resources", "Instance"] for match in matches)
