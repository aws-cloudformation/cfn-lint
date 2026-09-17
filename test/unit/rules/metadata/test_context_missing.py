"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase
from test.unit.rules.metadata._context_helpers import match, missing_rule

from cfnlint.rules.metadata._BaseContext import CONTEXT_KEY
from cfnlint.rules.metadata.ContextMissing import ContextMissing


class TestContextMissing(BaseTestCase):
    """I4010 missing-context: significance gate + two-finding aggregate."""

    def test_flags_single_significant_resource(self):
        template = "Resources:\n  OrderQueue:\n    Type: AWS::SQS::Queue\n"
        self.assertEqual(1, len(match(ContextMissing(), template)))

    def test_low_value_type_is_not_required(self):
        template = "Resources:\n  ServiceLogGroup:\n    Type: AWS::Logs::LogGroup\n"
        self.assertEqual([], match(missing_rule(), template))

    def test_mixed_significant_and_low_value_only_flags_significant(self):
        # A larger stack mixing significant resources with low-value LogGroups:
        # the aggregate must cover only the significant resources, and no LogGroup
        # may appear in any emitted message (template, primary, or related child).
        template = (
            "Resources:\n"
            "  OrderQueue:\n"
            "    Type: AWS::SQS::Queue\n"
            "  OrdersTable:\n"
            "    Type: AWS::DynamoDB::Table\n"
            "  ServiceLogGroup:\n"
            "    Type: AWS::Logs::LogGroup\n"
            "  AuditLogGroup:\n"
            "    Type: AWS::Logs::LogGroup\n"
        )
        matches = match(missing_rule(), template)
        # Two top-level findings: template diagnostic + one resource aggregate.
        self.assertEqual(2, len(matches))
        aggregate = next(
            m for m in matches if not m.message.startswith("This template")
        )
        # Primary lists both significant resources; no children (aggregate only).
        self.assertIn("OrderQueue", aggregate.message)
        self.assertIn("OrdersTable", aggregate.message)
        # No LogGroup is required or mentioned anywhere.
        all_text = " ".join(m.message for m in matches)
        self.assertNotIn("LogGroup", all_text)

    def test_single_significant_resource_has_no_template_finding(self):
        template = "Resources:\n  OrderQueue:\n    Type: AWS::SQS::Queue\n"
        matches = match(missing_rule(), template)
        self.assertEqual(1, len(matches))
        self.assertFalse(matches[0].message.startswith("This template"))

    def test_template_finding_when_multiple_significant_and_no_context(self):
        template = (
            "Resources:\n"
            "  OrderQueue:\n"
            "    Type: AWS::SQS::Queue\n"
            "  OrdersTable:\n"
            "    Type: AWS::DynamoDB::Table\n"
        )
        matches = match(missing_rule(), template)
        template_findings = [
            m for m in matches if m.message.startswith("This template")
        ]
        self.assertEqual(1, len(template_findings))
        self.assertEqual(["Metadata"], template_findings[0].path)

    def test_aggregate_primary_lists_all_children_ride_on_context(self):
        template = (
            "Resources:\n"
            "  OrderProcessor:\n"
            "    Type: AWS::Lambda::Function\n"
            "  OrderQueue:\n"
            "    Type: AWS::SQS::Queue\n"
            "  OrdersTable:\n"
            "    Type: AWS::DynamoDB::Table\n"
            "  OrderLogs:\n"
            "    Type: AWS::Logs::LogGroup\n"
        )
        matches = match(missing_rule(), template)
        aggregate = next(
            m for m in matches if not m.message.startswith("This template")
        )
        for logical_id in ("OrderProcessor", "OrderQueue", "OrdersTable"):
            self.assertIn(logical_id, aggregate.message)
        self.assertNotIn("OrderLogs", aggregate.message)

    def test_template_context_present_suppresses_template_finding(self):
        template = (
            "Metadata:\n"
            f"  {CONTEXT_KEY}:\n"
            "    arch: two queues\n"
            "Resources:\n"
            "  OrderQueue:\n"
            "    Type: AWS::SQS::Queue\n"
            "  AuditQueue:\n"
            "    Type: AWS::SQS::Queue\n"
        )
        matches = match(missing_rule(), template)
        self.assertEqual(1, len(matches))
        self.assertFalse(matches[0].message.startswith("This template"))

    def test_non_dict_resource_is_skipped(self):
        template = "Resources:\n  Malformed: not-a-dict\n"
        self.assertEqual([], match(missing_rule(), template))

    def test_cdk_template_is_skipped_entirely(self):
        template = (
            "Resources:\n"
            "  CDKMetadata:\n"
            "    Type: AWS::CDK::Metadata\n"
            "    Properties:\n"
            "      Analytics: v2:some-data\n"
            "  UserQueue:\n"
            "    Type: AWS::SQS::Queue\n"
            "  UserTopic:\n"
            "    Type: AWS::SNS::Topic\n"
        )
        self.assertEqual([], match(missing_rule(), template))

    def test_cdk_template_without_metadata_resource_is_skipped(self):
        # Covers analyticsReporting: false (no AWS::CDK::Metadata, has aws:cdk:path).
        template = (
            "Resources:\n"
            "  UserQueue:\n"
            "    Type: AWS::SQS::Queue\n"
            "    Metadata:\n"
            "      aws:cdk:path: Stack/UserQueue/Resource\n"
            "  UserTopic:\n"
            "    Type: AWS::SNS::Topic\n"
            "    Metadata:\n"
            "      aws:cdk:path: Stack/UserTopic/Resource\n"
        )
        self.assertEqual([], match(missing_rule(), template))

    def test_ignore_checks_on_one_resource_preserves_aggregate_for_others(self):
        template = (
            "Resources:\n"
            "  SuppressedQueue:\n"
            "    Type: AWS::SQS::Queue\n"
            "    Metadata:\n"
            "      cfn-lint:\n"
            "        config:\n"
            "          ignore_checks:\n"
            "            - I4010\n"
            "  UnsuppressedTopic:\n"
            "    Type: AWS::SNS::Topic\n"
        )
        matches = match(missing_rule(), template)
        # With one of two significant resources suppressed, missing drops to 1,
        # so the len(missing) >= 2 template gate should no longer fire.
        self.assertEqual(1, len(matches))
        self.assertFalse(matches[0].message.startswith("This template"))
        self.assertIn("UnsuppressedTopic", matches[0].message)
        self.assertNotIn("SuppressedQueue", matches[0].message)

    def test_ignore_checks_on_all_resources_suppresses_both_findings(self):
        template = (
            "Resources:\n"
            "  QueueA:\n"
            "    Type: AWS::SQS::Queue\n"
            "    Metadata:\n"
            "      cfn-lint:\n"
            "        config:\n"
            "          ignore_checks:\n"
            "            - I4010\n"
            "  QueueB:\n"
            "    Type: AWS::SQS::Queue\n"
            "    Metadata:\n"
            "      cfn-lint:\n"
            "        config:\n"
            "          ignore_checks:\n"
            "            - I4010\n"
        )
        matches = match(missing_rule(), template)
        self.assertEqual(0, len(matches))

    def test_ignore_checks_rule_id_prefix_does_not_suppress(self):
        # Directive keys are matched exactly, as cfn-lint's runner does. A rule
        # id prefix such as 'I' or 'I40' is not a directive for I4010, so it
        # must leave both findings intact.
        for prefix in ("I", "I40", "I401"):
            template = (
                "Resources:\n"
                "  QueueA:\n"
                "    Type: AWS::SQS::Queue\n"
                "    Metadata:\n"
                "      cfn-lint:\n"
                "        config:\n"
                "          ignore_checks:\n"
                f"            - {prefix}\n"
                "  QueueB:\n"
                "    Type: AWS::SQS::Queue\n"
            )
            matches = match(missing_rule(), template)
            self.assertEqual(2, len(matches), f"prefix {prefix!r}: {matches}")
            aggregate = next(
                m for m in matches if not m.message.startswith("This template")
            )
            self.assertIn("QueueA", aggregate.message)

    def test_ignore_checks_for_another_rule_does_not_suppress(self):
        template = (
            "Resources:\n"
            "  QueueA:\n"
            "    Type: AWS::SQS::Queue\n"
            "    Metadata:\n"
            "      cfn-lint:\n"
            "        config:\n"
            "          ignore_checks:\n"
            "            - W4011\n"
            "  QueueB:\n"
            "    Type: AWS::SQS::Queue\n"
        )
        matches = match(missing_rule(), template)
        self.assertEqual(2, len(matches))
        aggregate = next(
            m for m in matches if not m.message.startswith("This template")
        )
        self.assertIn("QueueA", aggregate.message)
