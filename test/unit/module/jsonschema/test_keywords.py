"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from unittest.mock import Mock

import pytest

from cfnlint.jsonschema import ValidationError, _keywords
from cfnlint.jsonschema.validators import CfnTemplateValidator
from cfnlint.rules import CloudFormationLintRule


class Error(CloudFormationLintRule):
    id = "E1111"

    def validate(self, validator, s, instance, schema):
        if s:
            yield ValidationError(
                "Error",
                rule=self,
            )


class Warning(CloudFormationLintRule):
    id = "W1111"

    def validate(self, validator, s, instance, schema):
        yield ValidationError(
            "Warning",
            rule=self,
        )


@pytest.fixture
def validator():
    validator = CfnTemplateValidator(schema={})
    validator = validator.extend(
        validators={
            "error": Error().validate,
            "warning": Warning().validate,
        }
    )
    return validator({})


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid anyOf",
            "foo",
            [{"const": "foo"}, {"const": "bar"}],
            [],
        ),
        (
            "Valid anyOf with error rule",
            "foo",
            [{"const": "foo"}, {"error": True}],
            [],
        ),
        (
            "Invalid anyOf with error rule",
            "foo",
            [{"error": True}, {"error": True}],
            [
                ValidationError(
                    "'foo' is not valid under any of the given schemas",
                    path=deque([]),
                    schema_path=deque([]),
                    context=[
                        ValidationError(
                            "Error",
                            rule=Error(),
                            path=deque([]),
                            validator="error",
                            schema_path=deque([0, "error"]),
                        ),
                        ValidationError(
                            "Error",
                            rule=Error(),
                            path=deque([]),
                            validator="error",
                            schema_path=deque([1, "error"]),
                        ),
                    ],
                ),
            ],
        ),
        (
            "Valid anyOf with a warning validation error",
            "foo",
            [{"warning": True, "error": True}, {"error": True}],
            [
                ValidationError(
                    "'foo' is not valid under any of the given schemas",
                    path=deque([]),
                    schema_path=deque([]),
                    context=[
                        ValidationError(
                            "Error",
                            rule=Error(),
                            path=deque([]),
                            validator="error",
                            schema_path=deque([0, "error"]),
                        ),
                        ValidationError(
                            "Error",
                            rule=Error(),
                            path=deque([]),
                            validator="error",
                            schema_path=deque([1, "error"]),
                        ),
                        ValidationError(
                            "Warning",
                            rule=Warning(),
                            path=deque([]),
                            validator="warning",
                            schema_path=deque([0, "warning"]),
                        ),
                    ],
                ),
            ],
        ),
        (
            "Valid anyOf without a warning validation error",
            "foo",
            [{"error": True}, {"warning": True}],
            [],
        ),
    ],
)
def test_anyof(name, instance, schema, validator, expected):
    errs = list(_keywords.anyOf(validator, schema, instance, schema))
    assert errs == expected, f"{name!r} got errors {errs!r}"


def test_if_validator_context_evolution():
    """Test that the if_validator evolves context with allow_exceptions=False"""

    # Create a mock validator with a mock context
    mock_validator = Mock()
    mock_context = Mock()
    mock_validator.context = mock_context

    # Mock the context.evolve method to return a new context
    mock_evolved_context = Mock()
    mock_context.evolve.return_value = mock_evolved_context

    # Mock the function_filter.evolve method
    mock_function_filter = Mock()
    mock_validator.function_filter = mock_function_filter
    mock_function_filter.evolve.return_value = Mock()

    # Mock the first validator.evolve call (for function_filter)
    mock_evolved_validator = Mock()
    mock_validator.evolve.return_value = mock_evolved_validator

    # Set up the evolved validator's context and methods
    mock_evolved_validator.context = mock_context
    mock_evolved_validator.descend.return_value = iter([])

    # Mock the second evolve call (for context) on the evolved validator
    mock_if_validator = Mock()
    mock_evolved_validator.evolve.return_value = mock_if_validator

    # Mock the final evolve call (for schema) and is_valid
    mock_final_validator = Mock()
    mock_final_validator.is_valid.return_value = True
    mock_if_validator.evolve.return_value = mock_final_validator

    # Create a simple schema
    schema = {"if": {"const": "test"}, "then": {"const": "result"}}

    # Call the if_ function
    list(_keywords.if_(mock_validator, schema, "test", schema))

    # Verify that context.evolve was called with allow_exceptions=False
    mock_context.evolve.assert_called_once_with(allow_exceptions=False)

    # Verify that the evolved validator's evolve was called with the evolved context
    mock_evolved_validator.evolve.assert_called_once_with(context=mock_evolved_context)
