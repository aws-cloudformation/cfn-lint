"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.DynamicReferenceSecretsManagerArn import (
    DynamicReferenceSecretsManagerArn,
)


@pytest.fixture(scope="module")
def rule():
    rule = DynamicReferenceSecretsManagerArn()
    yield rule


@pytest.mark.parametrize(
    "name,instance,path,expected",
    [
        (
            "Valid secrets manager",
            "{{resolve:secretsmanager:Parameter}}",
            {
                "path": deque(["Resources", "MyResource", "Properties", "Password"]),
            },
            [],
        ),
        (
            "Valid sub not to secrets manaager",
            "secretsmanager",
            {
                "path": deque(
                    ["Resources", "MyResource", "Properties", "Password", "Fn::Sub"]
                ),
            },
            [],
        ),
        (
            "Valid secrets manager outside of Resources",
            "{{resolve:secretsmanager:Parameter}}",
            {
                "path": deque(["Parameters", "Type", "Default"]),
            },
            [],
        ),
        (
            "Valid secrets manager outside of Resources",
            "{{resolve:secretsmanager:Parameter}}",
            {
                "path": deque(["Metadata", "Value"]),
            },
            [],
        ),
        (
            "Invalid secrets manager when ARN was expected",
            "{{resolve:secretsmanager:secret}}",
            {
                "path": deque(["Resources", "MyResource", "Properties", "SecretArn"]),
            },
            [
                ValidationError(
                    (
                        "Dynamic reference '{{resolve:secretsmanager:secret}}'"
                        " to secrets manager when the field 'SecretArn' expects "
                        "the ARN to the secret and not the secret"
                    ),
                    rule=DynamicReferenceSecretsManagerArn(),
                )
            ],
        ),
        (
            "Invalid secrets manager when ARN was expected",
            '\\"{{resolve:secretsmanager:${MyParameter}}}\\"',
            {
                "path": deque(
                    ["Resources", "MyResource", "Properties", "SecretArn", "Fn::Sub"]
                ),
            },
            [
                ValidationError(
                    (
                        "Dynamic reference "
                        "'\\\\\"{{resolve:secretsmanager:${MyParameter}}}\\\\\"'"
                        " to secrets manager when the field 'SecretArn' "
                        "expects the ARN to the secret and not the secret"
                    ),
                    rule=DynamicReferenceSecretsManagerArn(),
                )
            ],
        ),
    ],
    indirect=["path"],
)
def test_validate(name, instance, path, expected, validator, rule):
    errs = list(rule.validate(validator, {}, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"
