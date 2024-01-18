"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from datetime import datetime

import pytest

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.lmbd.DeprecatedRuntimeEnd import DeprecatedRuntimeEnd


@pytest.fixture(scope="module")
def rule():
    rule = DeprecatedRuntimeEnd()
    rule.current_date = datetime(2019, 6, 29)
    yield rule


@pytest.fixture(scope="module")
def validator():
    yield CfnTemplateValidator(schema={})


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            "nodejs16.x",
            [],
        ),
        (
            "foo",
            [],
        ),
        (
            "nodejs4.3",
            [
                ValidationError(
                    (
                        "Deprecated runtime 'nodejs4.3' specified. "
                        "Updating disabled since '2019-04-30'. "
                        "Please consider updating to 'nodejs16.x'"
                    ),
                    rule=DeprecatedRuntimeEnd(),
                )
            ],
        ),
    ],
)
def test_lambda_runtime(instance, expected, rule, validator):
    errs = list(rule.lambdaruntime(validator, "LambdaRuntime", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
