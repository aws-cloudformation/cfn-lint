"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

from cfnlint.rules.metadata.ContextMissing import ContextMissing
from cfnlint.rules.metadata.ContextMissingWhy import ContextMissingWhy
from cfnlint.rules.metadata.ContextSchemaViolation import ContextSchemaViolation


class TestEnablementGating(BaseTestCase):
    """Both gates (I prefix + experimental) must be open before rules fire."""

    def test_i4010_off_by_default(self):
        self.assertFalse(
            ContextMissing().is_enabled(
                include_experimental=False, include_rules=["W", "E"]
            )
        )

    def test_i4010_informational_gate_alone_is_not_enough(self):
        self.assertFalse(
            ContextMissing().is_enabled(
                include_experimental=False, include_rules=["W", "E", "I"]
            )
        )

    def test_i4010_enabled_when_both_gates_open(self):
        self.assertTrue(
            ContextMissing().is_enabled(
                include_experimental=True, include_rules=["W", "E", "I"]
            )
        )

    def test_i4011_off_by_default(self):
        self.assertFalse(
            ContextMissingWhy().is_enabled(
                include_experimental=False, include_rules=["W", "E"]
            )
        )

    def test_i4011_enabled_when_both_gates_open(self):
        self.assertTrue(
            ContextMissingWhy().is_enabled(
                include_experimental=True, include_rules=["W", "E", "I"]
            )
        )

    def test_i4012_off_by_default(self):
        self.assertFalse(
            ContextSchemaViolation().is_enabled(
                include_experimental=False, include_rules=["W", "E"]
            )
        )

    def test_i4012_enabled_when_both_gates_open(self):
        self.assertTrue(
            ContextSchemaViolation().is_enabled(
                include_experimental=True, include_rules=["W", "E", "I"]
            )
        )

    def test_config_surface_i4010_has_both_options(self):
        self.assertEqual(
            sorted(ContextMissing().config_definition.keys()),
            ["additional_incidental_patterns", "additional_low_value_types"],
        )

    def test_config_surface_i4011_has_only_incidental_patterns(self):
        self.assertEqual(
            sorted(ContextMissingWhy().config_definition.keys()),
            ["additional_incidental_patterns"],
        )

    def test_config_surface_i4012_has_only_incidental_patterns(self):
        self.assertEqual(
            sorted(ContextSchemaViolation().config_definition.keys()),
            ["additional_incidental_patterns"],
        )
