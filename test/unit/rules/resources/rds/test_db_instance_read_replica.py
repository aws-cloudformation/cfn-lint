"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from pathlib import Path

import pytest

from cfnlint import ConfigMixIn
from cfnlint.config import _DEFAULT_RULESDIR
from cfnlint.rules import Rules
from cfnlint.runner import Runner

_FIXTURES = (
    Path(__file__).parent.parent.parent.parent.parent
    / "fixtures"
    / "templates"
    / "issues"
    / "rds_read_replica"
)


@pytest.fixture(scope="module")
def rules():
    return Rules.create_from_directory(_DEFAULT_RULESDIR)


def _run(rules, filename):
    config = ConfigMixIn(
        regions=["us-east-1"],
        templates=[str(_FIXTURES / filename)],
    )
    runner = Runner(config)
    runner.rules = rules
    return list(runner.run())


def test_read_replica_ignored_properties(rules):
    # Regression test for https://github.com/aws-cloudformation/cfn-lint/issues/4817
    # StorageEncrypted, MasterUsername and DBName are silently ignored on a
    # read replica: W3692 warns once per property, and the E3020
    # dependentExcluded hard error must not fire.
    matches = _run(rules, "read_replica_ignored_properties.yaml")

    assert not [m for m in matches if m.rule.id == "E3020"], (
        f"E3020 must not fire on ignored read replica properties: {matches!r}"
    )
    warnings = [m for m in matches if m.rule.id == "W3692"]
    assert sorted(m.path[-1] for m in warnings) == [
        "DBName",
        "MasterUsername",
        "StorageEncrypted",
    ], f"expected one W3692 warning per ignored property, got {matches!r}"
    for warning in warnings:
        assert "ignored on a read replica" in warning.message


def test_read_replica_ref_source(rules):
    # The common in-template pattern: SourceDBInstanceIdentifier is a Ref to
    # a source in the same template. Presence is what makes it a read
    # replica, so the ignored properties must still warn.
    matches = _run(rules, "read_replica_ref_source.yaml")

    warnings = [m for m in matches if m.rule.id == "W3692"]
    assert sorted(m.path[-1] for m in warnings) == [
        "DBName",
        "MasterUsername",
        "StorageEncrypted",
    ], f"expected one W3692 warning per ignored property, got {matches!r}"


def test_read_replica_honored_properties(rules):
    # BackupRetentionPeriod and PreferredBackupWindow are honored on read
    # replicas (live verified): no warning, no error.
    matches = _run(rules, "read_replica_honored_properties.yaml")

    assert matches == [], f"expected no matches, got {matches!r}"


def test_source_db_instance(rules):
    # A source DB (no SourceDBInstanceIdentifier) setting these properties
    # is normal: no warning, no error.
    matches = _run(rules, "source_db_instance.yaml")

    assert matches == [], f"expected no matches, got {matches!r}"


def test_non_rds_resource(rules):
    # Non-RDS resources are unaffected by the change.
    matches = _run(rules, "non_rds_resource.yaml")

    assert matches == [], f"expected no matches, got {matches!r}"
