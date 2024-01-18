"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from datetime import datetime

import pytest

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.lmbd.DeprecatedRuntimeEnd import DeprecatedRuntimeEnd
from cfnlint.rules.resources.lmbd.DeprecatedRuntimeEol import DeprecatedRuntimeEol


@pytest.fixture(scope="module")
def rule():
    rule = DeprecatedRuntimeEnd()
    rule.current_date = datetime(2019, 6, 29)
    child_rule = DeprecatedRuntimeEol()
    child_rule.current_date = datetime(2019, 6, 29)
    rule.child_rules["W2531"] = child_rule
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
            "nodejs6.10",
            [
                ValidationError(
                    (
                        "EOL runtime 'nodejs6.10' specified. "
                        "Runtime is EOL since '2019-04-30' and "
                        "updating will be disabled at '2019-08-12'. "
                        "Please consider updating to 'nodejs16.x'"
                    ),
                    rule=DeprecatedRuntimeEol(),
                )
            ],
        ),
    ],
)
def test_lambda_runtime(instance, expected, rule, validator):
    errs = list(rule.lambdaruntime(validator, "LambdaRuntime", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
