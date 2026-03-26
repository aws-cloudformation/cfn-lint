"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.Lifecycle import ResourceLifecycle
from cfnlint.rules.resources.LifecycleMaintenance import ResourceLifecycleMaintenance
from cfnlint.rules.resources.LifecycleSunset import ResourceLifecycleSunset
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = ResourceLifecycle()
    rule.child_rules = {
        "W3696": ResourceLifecycleSunset(),
        "W3697": ResourceLifecycleMaintenance(),
    }
    yield rule


@pytest.fixture(scope="module")
def cfn():
    return Template("", {}, regions=["us-east-1"])


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


@pytest.mark.parametrize(
    "name,lc,schema,expected",
    [
        (
            "Shutdown with date",
            {"status": "shutdown", "date": "2024-05-01"},
            {"typeName": "AWS::OpsWorks::Stack"},
            [
                ValidationError(
                    (
                        "Resource type 'AWS::OpsWorks::Stack' is from a "
                        "service that was shut down on 2024-05-01"
                    ),
                    rule=ResourceLifecycle(),
                ),
            ],
        ),
        (
            "Sunset with date",
            {"status": "sunset", "date": "2026-10-07"},
            {"typeName": "AWS::Proton::EnvironmentTemplate"},
            [
                ValidationError(
                    (
                        "Resource type 'AWS::Proton::EnvironmentTemplate' "
                        "is from a service that will be shut down on "
                        "2026-10-07. Plan to migrate to an alternative"
                    ),
                    rule=ResourceLifecycleSunset(),
                ),
            ],
        ),
        (
            "Maintenance with date",
            {"status": "maintenance", "date": "2024-10-01"},
            {"typeName": "AWS::AutoScaling::LaunchConfiguration"},
            [
                ValidationError(
                    (
                        "Resource type "
                        "'AWS::AutoScaling::LaunchConfiguration' is from a "
                        "service in maintenance mode since 2024-10-01. "
                        "Consider migrating to an alternative"
                    ),
                    rule=ResourceLifecycleMaintenance(),
                ),
            ],
        ),
        (
            "Sunset without date",
            {"status": "sunset"},
            {"typeName": "AWS::WAF::WebACL"},
            [
                ValidationError(
                    (
                        "Resource type 'AWS::WAF::WebACL' is from a "
                        "service that is sunsetting"
                    ),
                    rule=ResourceLifecycleSunset(),
                ),
            ],
        ),
        (
            "No lifecycle",
            None,
            {"typeName": "AWS::S3::Bucket"},
            [],
        ),
        (
            "Invalid lifecycle type",
            "not a dict",
            {"typeName": "AWS::S3::Bucket"},
            [],
        ),
        (
            "Unknown status",
            {"status": "unknown"},
            {"typeName": "AWS::S3::Bucket"},
            [],
        ),
    ],
)
def test_lifecycle(name, lc, schema, expected, rule, context, cfn):
    validator = CfnTemplateValidator(context=context, cfn=cfn, schema=schema)
    errs = list(rule.lifecycle(validator, lc, {}, schema))
    assert errs == expected, f"Test {name!r} got {errs!r}"
