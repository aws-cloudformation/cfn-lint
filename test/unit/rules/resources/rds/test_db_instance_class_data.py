"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
from pathlib import Path

import pytest

import cfnlint.data.schemas.extensions.aws_rds_dbinstance as dbinstance_module
from cfnlint.rules.resources.rds.DbInstanceDbInstanceClassWithEngine import (
    DbInstanceDbInstanceClassWithEngine,
)


def _load_schema(filename):
    path = Path(dbinstance_module.__file__).parent / filename
    return json.loads(path.read_text(encoding="utf-8"))


def _minor_of(pattern):
    # patterns look like ^(5\.7\..+|5\.7)$ ; take the second alternative
    inner = pattern.strip("^$")
    assert inner.startswith("(") and inner.endswith(")")
    return inner[1:-1].split("|")[1].replace("\\.", ".")


@pytest.fixture(scope="module")
def class_schema():
    return _load_schema("db_instance_class.json")


@pytest.fixture(scope="module")
def version_schema():
    return _load_schema("engine_version.json")


def _branches(schema):
    for entry in schema["allOf"]:
        engine = entry["if"]["properties"]["Engine"].get("const")
        if not engine:
            continue
        yield (
            engine,
            _minor_of(entry["if"]["properties"]["EngineVersion"]["pattern"]),
            entry,
        )


def _mysql_57_branch(class_schema):
    for engine, minor, entry in _branches(class_schema):
        if engine == "mysql" and minor == "5.7":
            return entry
    raise AssertionError("mysql 5.7 branch not found")


def test_mysql_57_enum_excludes_t4g_medium(class_schema):
    # https://github.com/aws-cloudformation/cfn-lint/issues/4853
    # RDS offers mysql 5.7.44 only on db.m5, db.r5 and db.t3 classes in
    # us-east-1, and the docs give db.t4g.medium on MySQL as 8.4 and 8.0.
    entry = _mysql_57_branch(class_schema)
    enum = entry["then"]["properties"]["DBInstanceClass"]["enum"]

    assert "db.t4g.medium" not in enum

    expected = sorted(
        [
            f"db.m5.{s}"
            for s in [
                "large",
                "xlarge",
                "2xlarge",
                "4xlarge",
                "8xlarge",
                "12xlarge",
                "16xlarge",
                "24xlarge",
            ]
        ]
        + [
            f"db.r5.{s}"
            for s in [
                "large",
                "xlarge",
                "2xlarge",
                "4xlarge",
                "8xlarge",
                "12xlarge",
                "16xlarge",
                "24xlarge",
            ]
        ]
        + [
            f"db.t3.{s}"
            for s in ["small", "micro", "medium", "large", "xlarge", "2xlarge"]
        ]
    )
    assert sorted(enum) == expected


def test_no_cross_engine_version_branches(class_schema, version_schema):
    # Guards the generator bug from
    # https://github.com/aws-cloudformation/cfn-lint/issues/4853 where
    # dict.fromkeys handed every engine the same dict, so e.g. aurora-mysql
    # carried a branch for the MariaDB version 10.11. Every branch must pair
    # an engine with one of its own versions from engine_version.json.
    valid_minors = {}
    for entry in version_schema["allOf"]:
        engine = entry["if"]["properties"]["Engine"].get("const")
        if not engine:
            continue
        valid_minors[engine] = {
            ".".join(str(v).split(".")[:2])
            for v in entry["then"]["properties"]["EngineVersion"]["enum"]
        }

    bad = [
        f"{engine} {minor}"
        for engine, minor, _ in _branches(class_schema)
        if minor not in valid_minors.get(engine, set())
    ]
    assert bad == [], f"branches for versions the engine does not have: {bad}"


def test_repro_template_4853(class_schema, validator):
    # Exact repro from https://github.com/aws-cloudformation/cfn-lint/issues/4853
    rule = DbInstanceDbInstanceClassWithEngine()
    rule._schema = class_schema
    instance = {
        "Engine": "mysql",
        "EngineVersion": "5.7.44-rds.20260902",
        "DBInstanceClass": "db.t4g.medium",
        "AllocatedStorage": "20",
    }
    errors = list(rule.validate(validator, "", instance, {}))
    assert len(errors) == 1
    assert errors[0].rule.id == "E3062"
    assert "db.t4g.medium" in errors[0].message


def test_valid_mysql_57_combo_still_passes(class_schema, validator):
    rule = DbInstanceDbInstanceClassWithEngine()
    rule._schema = class_schema
    instance = {
        "Engine": "mysql",
        "EngineVersion": "5.7.44-rds.20260902",
        "DBInstanceClass": "db.r5.large",
    }
    errors = list(rule.validate(validator, "", instance, {}))
    assert errors == []


def test_valid_mysql_80_t4g_still_passes(class_schema, validator):
    # db.t4g.medium is valid for MySQL 8.0/8.4 per the docs; the fix must not
    # turn it into a false positive.
    rule = DbInstanceDbInstanceClassWithEngine()
    rule._schema = class_schema
    instance = {
        "Engine": "mysql",
        "EngineVersion": "8.0.44",
        "DBInstanceClass": "db.t4g.medium",
    }
    errors = list(rule.validate(validator, "", instance, {}))
    assert errors == []
