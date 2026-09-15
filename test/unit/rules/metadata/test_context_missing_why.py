"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase
from test.unit.rules.metadata._context_helpers import match

from cfnlint.rules.metadata._BaseContext import CONTEXT_KEY
from cfnlint.rules.metadata.ContextMissing import ContextMissing
from cfnlint.rules.metadata.ContextMissingWhy import ContextMissingWhy


class TestContextMissingWhy(BaseTestCase):
    """W4011 missing-why: flags blocks with no 'why' and no trust."""

    def test_cdk_template_is_skipped_entirely(self):
        template = (
            "Resources:\n"
            "  CDKMetadata:\n"
            "    Type: AWS::CDK::Metadata\n"
            "  Notifier:\n"
            "    Type: AWS::SNS::Topic\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        must:\n"
            "          - at least one subscriber\n"
        )
        self.assertEqual([], match(ContextMissingWhy(), template))

    def test_flags_missing_why(self):
        template = (
            "Resources:\n"
            "  Notifier:\n"
            "    Type: AWS::SNS::Topic\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        must:\n"
            "          - at least one subscriber\n"
        )
        matches = match(ContextMissingWhy(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("Notifier", matches[0].message)

    def test_trust_with_low_confidence_satisfies_the_rule(self):
        template = (
            "Resources:\n"
            "  LegacyTable:\n"
            "    Type: AWS::DynamoDB::Table\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        trust:\n"
            "          src: infer\n"
            "          conf: low\n"
            "          note: rationale not documented\n"
        )
        self.assertEqual([], match(ContextMissingWhy(), template))

    def test_resource_without_a_context_block_is_not_flagged(self):
        template = "Resources:\n  OrderQueue:\n    Type: AWS::SQS::Queue\n"
        self.assertEqual([], match(ContextMissingWhy(), template))

    def test_medium_confidence_trust_does_not_excuse_a_missing_why(self):
        # Only conf: low excuses a missing 'why'. medium claims the rationale
        # is partly known, which is not "undocumented".
        template = (
            "Resources:\n"
            "  OrderQueue:\n"
            "    Type: AWS::SQS::Queue\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        trust:\n"
            "          src: infer\n"
            "          conf: medium\n"
        )
        matches = match(ContextMissingWhy(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("OrderQueue", matches[0].message)

    def test_high_confidence_trust_does_not_excuse_a_missing_why(self):
        # conf: high claims the rationale IS known, so it is not an escape
        # hatch; only low acknowledges undocumented rationale.
        template = (
            "Resources:\n"
            "  OrderQueue:\n"
            "    Type: AWS::SQS::Queue\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        trust:\n"
            "          src: authored\n"
            "          conf: high\n"
        )
        matches = match(ContextMissingWhy(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("OrderQueue", matches[0].message)

    def test_low_value_resource_with_context_but_no_why_is_flagged(self):
        # Low-value types are exempt from I4010 (missing-context), but W4011
        # still validates any context they supply.
        template = (
            "Resources:\n"
            "  ServiceLogGroup:\n"
            "    Type: AWS::Logs::LogGroup\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        must:\n"
            "          - retain 30 days\n"
        )
        # Exempt from I4010...
        self.assertEqual([], match(ContextMissing(), template))
        # ...but W4011 still flags missing-why.
        matches = match(ContextMissingWhy(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("ServiceLogGroup", matches[0].message)

    def test_module_with_context_but_no_why_is_flagged(self):
        # MODULE pseudo-resources are exempt from I4010, but W4011 still
        # validates any context they supply.
        template = (
            "Resources:\n"
            "  MyModule:\n"
            "    Type: AWS::S3::Bucket::MODULE\n"
            "    Properties: {}\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        must:\n"
            "          - versioning enabled\n"
        )
        # Exempt from I4010...
        self.assertEqual([], match(ContextMissing(), template))
        # ...but W4011 still flags missing-why.
        matches = match(ContextMissingWhy(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("MyModule", matches[0].message)
