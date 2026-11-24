"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
from pathlib import Path

import pytest

import cfnlint.data.schemas.extensions.aws_rds_dbcluster as dbcluster_module
import cfnlint.data.schemas.extensions.aws_rds_dbinstance as dbinstance_module
from cfnlint.rules.resources.rds.DbClusterEngineVersion import DbClusterEngineVersion
from cfnlint.rules.resources.rds.DbInstanceEngineVersion import DbInstanceEngineVersion


def _load_schema(module, filename):
    path = Path(module.__file__).parent / filename
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def dbinstance_schema():
    return _load_schema(dbinstance_module, "engine_version.json")


@pytest.fixture(scope="module")
def dbcluster_schema():
    return _load_schema(dbcluster_module, "engine_version.json")


@pytest.mark.parametrize(
    "instance",
    [
        # https://github.com/aws-cloudformation/cfn-lint/issues/4822
        # Neptune is served by RDS and deploys through both resource types
        {"Engine": "neptune", "DBInstanceClass": "db.t3.medium"},
        # Documented valid values for AWS::RDS::DBInstance
        {"Engine": "sqlserver-dev-ee", "DBInstanceClass": "db.t3.medium"},
        {"Engine": "sqlserver-dev-se", "DBInstanceClass": "db.t3.medium"},
        # The rule lowercases Engine before validating
        {"Engine": "Neptune", "DBInstanceClass": "db.t3.medium"},
        # Sanity: an engine that was already accepted stays accepted
        {"Engine": "mysql", "DBInstanceClass": "db.t3.medium"},
    ],
)
def test_dbinstance_valid_engines(instance, validator, dbinstance_schema):
    rule = DbInstanceEngineVersion()
    rule._schema = dbinstance_schema
    errs = list(rule.validate(validator, "", dict(instance), {}))
    assert errs == [], f"Expected no errors got {errs}"


@pytest.mark.parametrize(
    "instance",
    [
        # https://github.com/aws-cloudformation/cfn-lint/issues/4822
        {"Engine": "neptune"},
        # Sanity: an engine that was already accepted stays accepted
        {"Engine": "mysql"},
    ],
)
def test_dbcluster_valid_engines(instance, validator, dbcluster_schema):
    rule = DbClusterEngineVersion()
    rule._schema = dbcluster_schema
    errs = list(rule.validate(validator, "", dict(instance), {}))
    assert errs == [], f"Expected no errors got {errs}"


@pytest.mark.parametrize(
    "rule_cls,schema_name",
    [
        (DbInstanceEngineVersion, "dbinstance_schema"),
        (DbClusterEngineVersion, "dbcluster_schema"),
    ],
)
def test_invalid_engine_still_rejected(rule_cls, schema_name, validator, request):
    # Guard against an over-permissive edit: unknown engines must still fail
    schema = request.getfixturevalue(schema_name)
    rule = rule_cls()
    rule._schema = schema
    errs = list(rule.validate(validator, "", {"Engine": "not-a-real-engine"}, {}))
    assert len(errs) == 1
    assert "not-a-real-engine" in errs[0].message
