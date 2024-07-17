"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.FunctionEnvironmentKeys import FunctionEnvironmentKeys


@pytest.fixture(scope="module")
def rule():
    rule = FunctionEnvironmentKeys()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"Foo": "Bar"},
            [],
        ),
        (
            {"AWS_REGION": "Bar"},
            [
                ValidationError(
                    (
                        "'AWS_REGION' is a reserved variable name, one of "
                        "['_HANDLER', '_X_AMZN_TRACE_ID', 'AWS_DEFAULT_REGION', "
                        "'AWS_REGION', 'AWS_EXECUTION_ENV', "
                        "'AWS_LAMBDA_FUNCTION_NAME', "
                        "'AWS_LAMBDA_FUNCTION_MEMORY_SIZE', "
                        "'AWS_LAMBDA_FUNCTION_VERSION', "
                        "'AWS_LAMBDA_INITIALIZATION_TYPE', "
                        "'AWS_LAMBDA_LOG_GROUP_NAME', "
                        "'AWS_LAMBDA_LOG_STREAM_NAME', "
                        "'AWS_ACCESS_KEY', 'AWS_ACCESS_KEY_ID', "
                        "'AWS_SECRET_ACCESS_KEY', "
                        "'AWS_SESSION_TOKEN', 'AWS_LAMBDA_RUNTIME_API', "
                        "'LAMBDA_TASK_ROOT', 'LAMBDA_RUNTIME_DIR']"
                    ),
                    schema_path=deque(["propertyNames", "not"]),
                    path=deque(["AWS_REGION"]),
                    rule=FunctionEnvironmentKeys(),
                    validator="not",
                )
            ],
        ),
        (
            {
                "Foo": "Bar",
                "AWS_REGION": "Bar",
                "Bar": "Foo",
                "AWS_ACCESS_KEY": "Foo",
            },
            [
                ValidationError(
                    (
                        "'AWS_REGION' is a reserved variable name, one of "
                        "['_HANDLER', '_X_AMZN_TRACE_ID', 'AWS_DEFAULT_REGION', "
                        "'AWS_REGION', 'AWS_EXECUTION_ENV', "
                        "'AWS_LAMBDA_FUNCTION_NAME', "
                        "'AWS_LAMBDA_FUNCTION_MEMORY_SIZE', "
                        "'AWS_LAMBDA_FUNCTION_VERSION', "
                        "'AWS_LAMBDA_INITIALIZATION_TYPE', "
                        "'AWS_LAMBDA_LOG_GROUP_NAME', "
                        "'AWS_LAMBDA_LOG_STREAM_NAME', "
                        "'AWS_ACCESS_KEY', 'AWS_ACCESS_KEY_ID', "
                        "'AWS_SECRET_ACCESS_KEY', "
                        "'AWS_SESSION_TOKEN', 'AWS_LAMBDA_RUNTIME_API', "
                        "'LAMBDA_TASK_ROOT', 'LAMBDA_RUNTIME_DIR']"
                    ),
                    schema_path=deque(["propertyNames", "not"]),
                    path=deque(["AWS_REGION"]),
                    rule=FunctionEnvironmentKeys(),
                    validator="not",
                ),
                ValidationError(
                    (
                        "'AWS_ACCESS_KEY' is a reserved variable name, one of "
                        "['_HANDLER', '_X_AMZN_TRACE_ID', 'AWS_DEFAULT_REGION', "
                        "'AWS_REGION', 'AWS_EXECUTION_ENV', "
                        "'AWS_LAMBDA_FUNCTION_NAME', "
                        "'AWS_LAMBDA_FUNCTION_MEMORY_SIZE', "
                        "'AWS_LAMBDA_FUNCTION_VERSION', "
                        "'AWS_LAMBDA_INITIALIZATION_TYPE', "
                        "'AWS_LAMBDA_LOG_GROUP_NAME', "
                        "'AWS_LAMBDA_LOG_STREAM_NAME', "
                        "'AWS_ACCESS_KEY', 'AWS_ACCESS_KEY_ID', "
                        "'AWS_SECRET_ACCESS_KEY', "
                        "'AWS_SESSION_TOKEN', 'AWS_LAMBDA_RUNTIME_API', "
                        "'LAMBDA_TASK_ROOT', 'LAMBDA_RUNTIME_DIR']"
                    ),
                    schema_path=deque(["propertyNames", "not"]),
                    path=deque(["AWS_ACCESS_KEY"]),
                    rule=FunctionEnvironmentKeys(),
                    validator="not",
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "LambdaRuntime", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
