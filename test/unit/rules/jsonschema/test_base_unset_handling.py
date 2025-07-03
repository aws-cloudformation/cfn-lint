"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from test.unit.rules import BaseRuleTestCase

from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class TestRule(CloudFormationLintRule):
    """Test Rule for unset handling"""

    id = "E3UNSET"
    shortdesc = "Test Rule"
    description = "Test Rule"
    source_url = ""
    tags: list[str] = []


class TestBaseJsonSchemaUnsetHandling(BaseRuleTestCase):
    """Test Base Json Schema unset value handling"""

    def test_convert_validation_errors_with_unset_values(self):
        """Test that unset validator and instance values are not added to kwargs"""

        class Rule(BaseJsonSchema):
            id = "E3UNSET"

        rule = Rule()

        # Test case 1: Both validator and instance are unset (using defaults)
        error_both_unset = ValidationError(
            "Test error with both unset",
            path=deque(["test"]),
            # Don't pass validator or instance - they default to _unset
        )

        matches = rule._convert_validation_errors_to_matches(["root"], error_both_unset)

        self.assertEqual(len(matches), 1)
        match = matches[0]

        # Check that validator and instance are not in the match attributes
        self.assertFalse(hasattr(match, "validator"))
        self.assertFalse(hasattr(match, "instance"))

    def test_convert_validation_errors_with_set_values(self):
        """Test that set validator and instance values are added to kwargs"""

        class Rule(BaseJsonSchema):
            id = "E3UNSET"

        rule = Rule()

        # Test case: Both validator and instance are set
        error_both_set = ValidationError(
            "Test error with both set",
            path=deque(["test"]),
            validator="type",
            validator_value="string",
            instance=123,
        )

        matches = rule._convert_validation_errors_to_matches(["root"], error_both_set)

        self.assertEqual(len(matches), 1)
        match = matches[0]

        # Check that validator and instance are in the match attributes
        self.assertTrue(hasattr(match, "validator"))
        self.assertTrue(hasattr(match, "instance"))
        self.assertEqual(match.validator, "type")
        self.assertEqual(match.instance, 123)

    def test_convert_validation_errors_mixed_set_unset(self):
        """Test mixed scenarios where one value is set and another is unset"""

        class Rule(BaseJsonSchema):
            id = "E3UNSET"

        rule = Rule()

        # Test case 1: validator is set, instance is unset (default)
        error_validator_set = ValidationError(
            "Test error with validator set",
            path=deque(["test1"]),
            validator="enum",
            # instance defaults to _unset
        )

        matches = rule._convert_validation_errors_to_matches(
            ["root"], error_validator_set
        )

        self.assertEqual(len(matches), 1)
        match = matches[0]

        self.assertTrue(hasattr(match, "validator"))
        self.assertFalse(hasattr(match, "instance"))
        self.assertEqual(match.validator, "enum")

        # Test case 2: validator is unset (default), instance is set
        error_instance_set = ValidationError(
            "Test error with instance set",
            path=deque(["test2"]),
            # validator defaults to _unset
            instance="test_value",
        )

        matches = rule._convert_validation_errors_to_matches(
            ["root"], error_instance_set
        )

        self.assertEqual(len(matches), 1)
        match = matches[0]

        self.assertFalse(hasattr(match, "validator"))
        self.assertTrue(hasattr(match, "instance"))
        self.assertEqual(match.instance, "test_value")

    def test_convert_validation_errors_with_extra_args_and_unset(self):
        """Test that extra_args work correctly when validator/instance are unset"""

        class Rule(BaseJsonSchema):
            id = "E3UNSET"

        rule = Rule()

        error = ValidationError(
            "Test error with extra args and unset values",
            path=deque(["test"]),
            # validator and instance default to _unset
            extra_args={"custom_field": "custom_value", "another_field": 42},
        )

        matches = rule._convert_validation_errors_to_matches(["root"], error)

        self.assertEqual(len(matches), 1)
        match = matches[0]

        # Check that validator and instance are not present
        self.assertFalse(hasattr(match, "validator"))
        self.assertFalse(hasattr(match, "instance"))

        # Check that extra_args are still present
        self.assertTrue(hasattr(match, "custom_field"))
        self.assertTrue(hasattr(match, "another_field"))
        self.assertEqual(match.custom_field, "custom_value")
        self.assertEqual(match.another_field, 42)

    def test_convert_validation_errors_with_context_and_unset(self):
        """Test that context errors also handle unset values correctly"""

        class Rule(BaseJsonSchema):
            id = "E3UNSET"

        rule = Rule()

        # Create context errors with mixed set/unset values
        context_error1 = ValidationError(
            "Context error 1 - validator unset",
            path=deque(["context1"]),
            # validator defaults to _unset
            instance="context_value1",
        )

        context_error2 = ValidationError(
            "Context error 2 - instance unset",
            path=deque(["context2"]),
            validator="type",
            # instance defaults to _unset
        )

        # Main error with context
        main_error = ValidationError(
            "Main error",
            path=deque(["main"]),
            validator="anyOf",
            instance={"test": "value"},
            context=[context_error1, context_error2],
        )

        matches = rule._convert_validation_errors_to_matches(["root"], main_error)

        self.assertEqual(len(matches), 1)
        main_match = matches[0]

        # Check main match has both validator and instance
        self.assertTrue(hasattr(main_match, "validator"))
        self.assertTrue(hasattr(main_match, "instance"))
        self.assertEqual(main_match.validator, "anyOf")
        self.assertEqual(main_match.instance, {"test": "value"})

        # Check context matches
        self.assertEqual(len(main_match.context), 2)

        # Context match 1: validator unset, instance set
        context_match1 = main_match.context[0]
        self.assertFalse(hasattr(context_match1, "validator"))
        self.assertTrue(hasattr(context_match1, "instance"))
        self.assertEqual(context_match1.instance, "context_value1")

        # Context match 2: validator set, instance unset
        context_match2 = main_match.context[1]
        self.assertTrue(hasattr(context_match2, "validator"))
        self.assertFalse(hasattr(context_match2, "instance"))
        self.assertEqual(context_match2.validator, "type")
