"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase
from test.unit.rules.metadata._context_helpers import match, missing_rule

from cfnlint.rules.metadata._BaseContext import CONTEXT_KEY, _expected_shape
from cfnlint.rules.metadata.ContextSchemaViolation import ContextSchemaViolation


class TestContextSchemaRules(BaseTestCase):
    """I4012 validates a supplied Context block against schema v1."""

    def test_cdk_template_is_skipped_entirely(self):
        template = (
            "Resources:\n"
            "  CDKMetadata:\n"
            "    Type: AWS::CDK::Metadata\n"
            "  Fn:\n"
            "    Type: AWS::Lambda::Function\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        why: 12345\n"
        )
        # why: 12345 is a schema violation (string expected), but the
        # entire template is CDK-synthesized so I4012 skips it.
        self.assertEqual([], match(ContextSchemaViolation(), template))

    def test_malformed_field_wrong_type(self):
        template = (
            "Resources:\n"
            "  Fn:\n"
            "    Type: AWS::Lambda::Function\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        why: ok\n"
            "        must: not a list\n"
        )
        matches = match(ContextSchemaViolation(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("array of strings", matches[0].message)

    def test_supplied_context_on_low_value_is_still_validated(self):
        template = (
            "Resources:\n"
            "  ServiceLogGroup:\n"
            "    Type: AWS::Logs::LogGroup\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        why: audit trail\n"
            "        must: not a list\n"
        )
        # Exempt from the missing-context requirement...
        self.assertEqual([], match(missing_rule(), template))
        # ...but its supplied context is still validated.
        matches = match(ContextSchemaViolation(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("ServiceLogGroup", matches[0].message)
        self.assertIn("array of strings", matches[0].message)

    def test_unknown_field_is_reported_once(self):
        template = (
            "Resources:\n"
            "  Fn:\n"
            "    Type: AWS::Lambda::Function\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        why: ok\n"
            "        unrecognizedfield: 1\n"
        )
        matches = match(ContextSchemaViolation(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("not a recognized Context field", matches[0].message)

    def test_invalid_enum_value(self):
        template = (
            "Resources:\n"
            "  Fn:\n"
            "    Type: AWS::Lambda::Function\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        why: ok\n"
            "        mutable: not-a-valid-level\n"
        )
        matches = match(ContextSchemaViolation(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("mutable", matches[0].message)

    def test_misplaced_field_both_directions(self):
        template = (
            "Metadata:\n"
            f"  {CONTEXT_KEY}:\n"
            "    arch: ok here\n"
            "    why: resource-only field on template\n"
            "Resources:\n"
            "  Fn:\n"
            "    Type: AWS::Lambda::Function\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        why: ok\n"
            "        arch: template-only field on resource\n"
        )
        matches = match(ContextSchemaViolation(), template)
        self.assertEqual(2, len(matches))

    def test_resource_context_block_that_is_not_a_mapping(self):
        template = (
            "Resources:\n"
            "  Fn:\n"
            "    Type: AWS::Lambda::Function\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}: just a string\n"
        )
        matches = match(ContextSchemaViolation(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("Fn", matches[0].message)
        self.assertIn("Expected a mapping of Context fields", matches[0].message)

    def test_template_context_block_that_is_not_a_mapping(self):
        template = (
            f"Metadata:\n  {CONTEXT_KEY}: just a string\n"
            "Resources:\n"
            "  Fn:\n"
            "    Type: AWS::Lambda::Function\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        why: ok\n"
        )
        matches = match(ContextSchemaViolation(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("Template", matches[0].message)
        self.assertIn("Expected a mapping of Context fields", matches[0].message)

    def test_expected_shape_for_trust_object(self):
        template = (
            "Resources:\n"
            "  Fn:\n"
            "    Type: AWS::Lambda::Function\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        why: ok\n"
            "        trust: a string\n"
        )
        matches = match(ContextSchemaViolation(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("object with required 'src' and 'conf'", matches[0].message)

    def test_expected_shape_for_mutability_level_ref(self):
        template = (
            "Resources:\n"
            "  Fn:\n"
            "    Type: AWS::Lambda::Function\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        why: ok\n"
            "        mutable:\n"
            "          - must-never-change\n"
        )
        messages = [m.message for m in match(ContextSchemaViolation(), template)]
        self.assertTrue(
            any("one of: must-never-change" in message for message in messages),
            messages,
        )

    def test_expected_shape_for_ref_entry_array(self):
        template = f"Metadata:\n  {CONTEXT_KEY}:\n    arch: ok\n    ref: 5\n"
        matches = match(ContextSchemaViolation(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("array of ref entries", matches[0].message)

    def test_expected_shape_for_mutability_mapping(self):
        template = (
            "Resources:\n"
            "  Fn:\n"
            "    Type: AWS::Lambda::Function\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        why: ok\n"
            "        mutability: not-a-map\n"
        )
        matches = match(ContextSchemaViolation(), template)
        self.assertEqual(1, len(matches))
        self.assertIn(
            "mapping of property name to mutability level", matches[0].message
        )

    def test_expected_shape_for_plain_string_field(self):
        template = (
            "Resources:\n"
            "  Fn:\n"
            "    Type: AWS::Lambda::Function\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        why:\n"
            "          - a list\n"
        )
        matches = match(ContextSchemaViolation(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("expected shape: string", matches[0].message)

    def test_expected_shape_falls_back_for_a_field_not_in_the_schema(self):
        # Defensive branch: unreachable through match() because every field the
        # schema defines hits an explicit branch. Called directly so a field
        # added later is known to degrade to a message rather than raise.
        self.assertEqual(
            "see the 'nosuchfield' definition in the Context schema",
            _expected_shape("nosuchfield", "ResourceContext"),
        )

    def test_resource_without_a_context_block_is_not_validated(self):
        template = "Resources:\n  OrderQueue:\n    Type: AWS::SQS::Queue\n"
        self.assertEqual([], match(ContextSchemaViolation(), template))

    def test_all_supplied_context_is_validated_even_with_trust(self):
        template = (
            "Resources:\n"
            "  OrderQueue:\n"
            "    Type: AWS::SQS::Queue\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        trust:\n"
            "          src: infer\n"
            "          conf: low\n"
            "        must: not a list\n"
        )
        matches = match(ContextSchemaViolation(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("array of strings", matches[0].message)
