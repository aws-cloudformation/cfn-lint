"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path, create_context_for_template
from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.RetentionPeriodOnResourceTypesWithAutoExpiringContent import (  # noqa: E501
    RetentionPeriodOnResourceTypesWithAutoExpiringContent,
)
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = RetentionPeriodOnResourceTypesWithAutoExpiringContent()
    yield rule


@pytest.fixture(scope="module")
def validator():
    cfn = Template(
        "",
        {
            "Resources": {
                "MyRdsDbInstance": {
                    "Type": "AWS::RDS::DBInstance",
                }
            }
        },
    )
    context = create_context_for_template(cfn).evolve(
        functions=FUNCTIONS,
        path=Path(
            path=deque(["Resources", "MyRdsDbInstance", "Properties"]),
        ),
    )
    yield CfnTemplateValidator(schema={}, context=context, cfn=cfn)


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid retention period",
            {"MessageRetentionPeriod": "90"},
            [],
        ),
        (
            "Valid with SourceDBInstanceIdentifier",
            {"SourceDBInstanceIdentifier": "source-db"},
            [],
        ),
        (
            "Invalid when not specified",
            {
                "Engine": "mysql",
            },
            [
                ValidationError(
                    (
                        "The default retention period will delete the data after "
                        "a pre-defined time. Set an explicit values to avoid data "
                        "loss on resource. 'BackupRetentionPeriod' is a "
                        "required property"
                    ),
                    rule=RetentionPeriodOnResourceTypesWithAutoExpiringContent(),
                    schema_path=deque(["then", "required"]),
                    validator="required",
                    validator_value=["BackupRetentionPeriod"],
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, False, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"
