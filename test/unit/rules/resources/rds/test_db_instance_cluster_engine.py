"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.decode.cfn_yaml import load
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.resources.rds.DbInstanceClusterEngine import DbInstanceClusterEngine
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    return DbInstanceClusterEngine()


_template = {
    "Resources": {
        "Cluster": {
            "Type": "AWS::RDS::DBCluster",
            "Properties": {
                "Engine": "aurora-mysql",
                "MasterUsername": "admin",
                "MasterUserPassword": "password",
            },
        },
        "Instance": {
            "Type": "AWS::RDS::DBInstance",
            "Properties": {
                "DBClusterIdentifier": {"Ref": "Cluster"},
                "DBInstanceClass": "db.r5.large",
                "Engine": "aurora-mysql",
            },
        },
    },
}


@pytest.mark.parametrize(
    "template,start_path,expected",
    [
        # Matching engines — valid
        (
            _template,
            deque(["Resources", "Instance", "Properties"]),
            [],
        ),
        # Mismatched engines — invalid
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Instance": {
                        "Type": "AWS::RDS::DBInstance",
                        "Properties": {
                            "DBClusterIdentifier": {"Ref": "Cluster"},
                            "DBInstanceClass": "db.r5.large",
                            "Engine": "aurora-postgresql",
                        },
                    },
                },
            },
            deque(["Resources", "Instance", "Properties"]),
            [
                ValidationError(
                    "'aurora-mysql' was expected",
                    validator="const",
                    rule=DbInstanceClusterEngine(),
                    path=deque(["Engine"]),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "properties",
                            "local",
                            "properties",
                            "Engine",
                            "const",
                        ]
                    ),
                ),
            ],
        ),
        # No DBClusterIdentifier — valid (standalone instance)
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Instance": {
                        "Type": "AWS::RDS::DBInstance",
                        "Properties": {
                            "DBInstanceClass": "db.r5.large",
                            "Engine": "mysql",
                        },
                    },
                },
            },
            deque(["Resources", "Instance", "Properties"]),
            [],
        ),
        # Fn::If on the local Engine: mismatch only in the second branch (#4850)
        (
            {
                "Conditions": {
                    "UsePostgres": {
                        "Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"],
                    },
                },
                "Resources": {
                    **_template["Resources"],
                    "Instance": {
                        "Type": "AWS::RDS::DBInstance",
                        "Properties": {
                            "DBClusterIdentifier": {"Ref": "Cluster"},
                            "DBInstanceClass": "db.r5.large",
                            "Engine": {
                                "Fn::If": [
                                    "UsePostgres",
                                    "aurora-mysql",
                                    "aurora-postgresql",
                                ]
                            },
                        },
                    },
                },
            },
            deque(["Resources", "Instance", "Properties"]),
            [
                ValidationError(
                    "'aurora-mysql' was expected",
                    validator="const",
                    rule=DbInstanceClusterEngine(),
                    path=deque(["Engine"]),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "properties",
                            "local",
                            "properties",
                            "Engine",
                            "const",
                        ]
                    ),
                ),
            ],
        ),
        # Fn::If on the remote Cluster Engine: mismatch only in one branch (#4850)
        (
            {
                "Conditions": {
                    "UsePostgres": {
                        "Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"],
                    },
                },
                "Resources": {
                    "Cluster": {
                        "Type": "AWS::RDS::DBCluster",
                        "Properties": {
                            "Engine": {
                                "Fn::If": [
                                    "UsePostgres",
                                    "aurora-postgresql",
                                    "aurora-mysql",
                                ]
                            },
                            "MasterUsername": "admin",
                            "MasterUserPassword": "password",
                        },
                    },
                    "Instance": {
                        "Type": "AWS::RDS::DBInstance",
                        "Properties": {
                            "DBClusterIdentifier": {"Ref": "Cluster"},
                            "DBInstanceClass": "db.r5.large",
                            "Engine": "aurora-mysql",
                        },
                    },
                },
            },
            deque(["Resources", "Instance", "Properties"]),
            [
                ValidationError(
                    "'aurora-postgresql' was expected",
                    validator="const",
                    rule=DbInstanceClusterEngine(),
                    path=deque(["Engine"]),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "properties",
                            "local",
                            "properties",
                            "Engine",
                            "const",
                        ]
                    ),
                ),
            ],
        ),
    ],
    indirect=["template"],
)
def test_validate(template, start_path, expected, rule, validator):
    for instance, instance_validator in get_value_from_path(
        validator, template, start_path
    ):
        errs = list(rule.validate(instance_validator, "", instance, {}))
        assert errs == expected, f"Expected {expected} got {errs}"


def test_cluster_engine_fnif_fixture(rule):
    """Fixture template from #4850: Fn::If on a gathered property"""
    template = load(
        "test/fixtures/templates/bad/resources/rds/cluster-engine-fnif.yaml"
    )
    cfn = Template("", template, regions=["us-east-1"])
    context = create_context_for_template(cfn)
    validator = CfnTemplateValidator(context=context, cfn=cfn)

    errs = []
    for instance, instance_validator in get_value_from_path(
        validator, template, deque(["Resources", "Instance", "Properties"])
    ):
        errs.extend(rule.validate(instance_validator, "", instance, {}))

    assert len(errs) == 1
    assert "aurora-postgresql" in errs[0].message
