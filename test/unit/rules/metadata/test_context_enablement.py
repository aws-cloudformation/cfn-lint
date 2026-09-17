"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

from cfnlint.rules.metadata.ContextMissing import ContextMissing
from cfnlint.rules.metadata.ContextMissingWhy import ContextMissingWhy
from cfnlint.rules.metadata.ContextSchemaViolation import ContextSchemaViolation


class TestEnablementGating(BaseTestCase):
    """Enablement gating for the Context rules.

    All three are experimental, so a default run (experimental gate closed)
    never fires them. Once experimental is open, severity decides the rest:
    I4010 is informational and additionally needs 'I' in the check set, while
    W4011/W4012 are warnings and fire on the experimental gate alone.
    """

    def test_i4010_off_by_default(self):
        self.assertFalse(
            ContextMissing().is_enabled(
                include_experimental=False, include_rules=["W", "E"]
            )
        )

    def test_i4010_informational_gate_alone_is_not_enough(self):
        # 'I' in the check set but experimental still closed.
        self.assertFalse(
            ContextMissing().is_enabled(
                include_experimental=False, include_rules=["W", "E", "I"]
            )
        )

    def test_i4010_experimental_alone_is_not_enough(self):
        # Experimental open but no 'I': the informational rule stays off. This
        # is what distinguishes I4010 from the W4011/W4012 warnings below.
        self.assertFalse(
            ContextMissing().is_enabled(
                include_experimental=True, include_rules=["W", "E"]
            )
        )

    def test_i4010_enabled_when_both_gates_open(self):
        self.assertTrue(
            ContextMissing().is_enabled(
                include_experimental=True, include_rules=["W", "E", "I"]
            )
        )

    def test_w4011_off_by_default(self):
        self.assertFalse(
            ContextMissingWhy().is_enabled(
                include_experimental=False, include_rules=["W", "E"]
            )
        )

    def test_w4011_enabled_by_experimental_gate_alone(self):
        # A warning needs no 'I' -- the experimental gate is the only gate.
        self.assertTrue(
            ContextMissingWhy().is_enabled(
                include_experimental=True, include_rules=["W", "E"]
            )
        )

    def test_w4012_off_by_default(self):
        self.assertFalse(
            ContextSchemaViolation().is_enabled(
                include_experimental=False, include_rules=["W", "E"]
            )
        )

    def test_w4012_enabled_by_experimental_gate_alone(self):
        self.assertTrue(
            ContextSchemaViolation().is_enabled(
                include_experimental=True, include_rules=["W", "E"]
            )
        )

    def test_severity_prefixes(self):
        # I4010 informational (context absent); W4011/W4012 warnings (author
        # supplied a block that is incomplete or invalid).
        self.assertEqual("I", ContextMissing().id[0])
        self.assertEqual("W", ContextMissingWhy().id[0])
        self.assertEqual("W", ContextSchemaViolation().id[0])

    def test_config_surface_i4010_has_both_options(self):
        self.assertEqual(
            sorted(ContextMissing().config_definition.keys()),
            ["additional_incidental_patterns", "additional_low_value_types"],
        )

    def test_config_surface_w4011_has_only_incidental_patterns(self):
        self.assertEqual(
            sorted(ContextMissingWhy().config_definition.keys()),
            ["additional_incidental_patterns"],
        )

    def test_config_surface_w4012_has_only_incidental_patterns(self):
        self.assertEqual(
            sorted(ContextSchemaViolation().config_definition.keys()),
            ["additional_incidental_patterns"],
        )
