"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

from cfnlint.decode import cfn_yaml
from cfnlint.rules.metadata.Context import (
    CONTEXT_KEY,
    ContextMissing,
    ContextMissingWhy,
    ContextSchemaViolation,
)
from cfnlint.template import Template


def _match(rule, template_str):
    """Decode a template string and run one rule's match() against it."""
    decoded = cfn_yaml.loads(template_str)
    cfn = Template("test.yaml", decoded)
    return rule.match(cfn)


def _missing_rule():
    """ContextMissing with require_context enabled (off by default)."""
    rule = ContextMissing()
    rule.config["require_context"] = True
    return rule


class TestContextMissing(BaseTestCase):
    """W4010 missing-context: significance gate + two-finding aggregate."""

    def test_disabled_by_default(self):
        template = (
            "Resources:\n"
            "  OrderQueue:\n"
            "    Type: AWS::SQS::Queue\n"
            "  OrdersTable:\n"
            "    Type: AWS::DynamoDB::Table\n"
        )
        self.assertEqual([], _match(ContextMissing(), template))

    def test_enabled_via_require_context(self):
        template = "Resources:\n  OrderQueue:\n    Type: AWS::SQS::Queue\n"
        self.assertEqual(1, len(_match(_missing_rule(), template)))

    def test_low_value_type_is_not_required(self):
        template = "Resources:\n  ServiceLogGroup:\n    Type: AWS::Logs::LogGroup\n"
        self.assertEqual([], _match(_missing_rule(), template))

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
        matches = _match(_missing_rule(), template)
        # Two top-level findings: template diagnostic + one resource aggregate.
        self.assertEqual(2, len(matches))
        aggregate = next(
            m for m in matches if not m.message.startswith("This template")
        )
        # Primary lists both significant resources; one related child rides along.
        self.assertIn("OrderQueue", aggregate.message)
        self.assertIn("OrdersTable", aggregate.message)
        self.assertEqual(1, len(aggregate.context))
        # No LogGroup is required or mentioned anywhere.
        all_text = " ".join(
            [m.message for m in matches] + [c.message for c in aggregate.context]
        )
        self.assertNotIn("LogGroup", all_text)

    def test_single_significant_resource_has_no_template_finding(self):
        template = "Resources:\n  OrderQueue:\n    Type: AWS::SQS::Queue\n"
        matches = _match(_missing_rule(), template)
        self.assertEqual(1, len(matches))
        self.assertFalse(matches[0].message.startswith("This template"))
        self.assertEqual([], matches[0].context)

    def test_template_finding_when_multiple_significant_and_no_context(self):
        template = (
            "Resources:\n"
            "  OrderQueue:\n"
            "    Type: AWS::SQS::Queue\n"
            "  OrdersTable:\n"
            "    Type: AWS::DynamoDB::Table\n"
        )
        matches = _match(_missing_rule(), template)
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
        matches = _match(_missing_rule(), template)
        aggregate = next(
            m for m in matches if not m.message.startswith("This template")
        )
        for logical_id in ("OrderProcessor", "OrderQueue", "OrdersTable"):
            self.assertIn(logical_id, aggregate.message)
        self.assertNotIn("OrderLogs", aggregate.message)
        self.assertEqual(2, len(aggregate.context))
        for child in aggregate.context:
            self.assertEqual(
                "This resource is missing Metadata.com.aws.cloudformation.Context.",
                child.message,
            )
            self.assertTrue(hasattr(child, "location"))

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
        matches = _match(_missing_rule(), template)
        self.assertEqual(1, len(matches))
        self.assertFalse(matches[0].message.startswith("This template"))
        self.assertEqual(1, len(matches[0].context))

    def test_non_dict_resource_is_skipped(self):
        template = "Resources:\n  Malformed: not-a-dict\n"
        self.assertEqual([], _match(_missing_rule(), template))


class TestContextMissingWhy(BaseTestCase):
    """W4011 missing-why: flags blocks with neither 'why' nor 'gaps'."""

    def test_flags_missing_why(self):
        template = (
            "Resources:\n"
            "  Notifier:\n"
            "    Type: AWS::SNS::Topic\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        ops: check the TTL\n"
        )
        matches = _match(ContextMissingWhy(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("Notifier", matches[0].message)

    def test_gaps_entry_satisfies_the_rule(self):
        template = (
            "Resources:\n"
            "  LegacyTable:\n"
            "    Type: AWS::DynamoDB::Table\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        gaps:\n"
            "          - rationale not documented\n"
        )
        self.assertEqual([], _match(ContextMissingWhy(), template))


class TestContextSchemaRules(BaseTestCase):
    """W4012 validates a supplied Context block against schema v1."""

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
        matches = _match(ContextSchemaViolation(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("array of strings", matches[0].message)

    def test_supplied_context_on_low_value_is_still_validated(self):
        # Design contract: require missing context selectively, but VALIDATE
        # supplied context everywhere. A LogGroup is exempt from W4010, yet a
        # malformed Context block an author wrote on it is still flagged.
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
        self.assertEqual([], _match(_missing_rule(), template))
        # ...but its supplied context is still validated.
        matches = _match(ContextSchemaViolation(), template)
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
            "        bogusfield: 1\n"
        )
        matches = _match(ContextSchemaViolation(), template)
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
        matches = _match(ContextSchemaViolation(), template)
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
        matches = _match(ContextSchemaViolation(), template)
        self.assertEqual(2, len(matches))


class TestTargetingAndConfig(BaseTestCase):
    """Shared targeting policy and configuration options."""

    def test_cdk_metadata_resource_is_incidental(self):
        template = "Resources:\n  CDKMetadata:\n    Type: AWS::CDK::Metadata\n"
        self.assertEqual([], _match(_missing_rule(), template))

    def test_framework_handler_logical_ids_are_incidental(self):
        # CloudFormation strips hyphens from logical IDs at synth, so the CDK
        # provider-framework handlers render hyphen-free (e.g. frameworkonEvent).
        # The incidental ID pattern must match them with no Provider prefix.
        template = (
            "Resources:\n"
            "  StackframeworkonEventABC123:\n"
            "    Type: AWS::Lambda::Function\n"
            "  StackframeworkisCompleteABC123:\n"
            "    Type: AWS::Lambda::Function\n"
            "  StackframeworkonTimeoutABC123:\n"
            "    Type: AWS::Lambda::Function\n"
            "  LogRetentionaae0aa3c5b4d4f87b02d85b201efdd8a:\n"
            "    Type: AWS::Lambda::Function\n"
        )
        self.assertEqual([], _match(_missing_rule(), template))

    def test_provider_substring_does_not_over_match(self):
        # "Provider" embedded in a resource name is a primary resource, not a
        # CDK framework helper, so a missing Context block is still flagged.
        template = (
            "Resources:\n"
            "  DataProviderTable:\n"
            "    Type: AWS::DynamoDB::Table\n"
            "  OrderProviderQueue:\n"
            "    Type: AWS::SQS::Queue\n"
        )
        matches = _match(_missing_rule(), template)
        # Two findings: template diagnostic + resource aggregate covering both.
        self.assertEqual(2, len(matches))

    def test_opt_out_marker_suppresses_schema_rules(self):
        template = (
            "Metadata:\n"
            f"  {CONTEXT_KEY}:\n"
            "    gaps:\n"
            "      - context intentionally omitted\n"
            "    why: misplaced but opted out\n"
        )
        self.assertEqual([], _match(ContextSchemaViolation(), template))

    def test_additional_low_value_types_config_excludes(self):
        rule = ContextMissing()
        rule.config["require_context"] = True
        rule.config["additional_low_value_types"] = ["AWS::Events::EventBus"]
        template = "Resources:\n  Bus:\n    Type: AWS::Events::EventBus\n"
        self.assertEqual([], rule.match(_decoded_template(template)))

    def test_additional_incidental_patterns_config_excludes(self):
        rule = ContextMissing()
        rule.config["require_context"] = True
        rule.config["additional_incidental_patterns"] = ["MyHelper"]
        template = "Resources:\n  MyHelperQueue:\n    Type: AWS::SQS::Queue\n"
        self.assertEqual([], rule.match(_decoded_template(template)))

    def test_default_severity_is_warning(self):
        self.assertEqual("warning", ContextMissing().severity)

    def test_configured_severity_is_honored(self):
        rule = ContextMissing()
        rule.config["severity"] = "error"
        self.assertEqual("error", rule.severity)

    def test_invalid_severity_falls_back_to_warning(self):
        rule = ContextMissing()
        rule.config["severity"] = "catastrophic"
        self.assertEqual("warning", rule.severity)

    def test_invalid_regex_in_additional_incidental_patterns_is_skipped(self):
        # An invalid regex in the config should not crash the rule; the
        # malformed pattern is silently skipped (except re.error branch).
        rule = ContextMissing()
        rule.config["require_context"] = True
        rule.config["additional_incidental_patterns"] = ["[invalid"]
        template = "Resources:\n  Queue:\n    Type: AWS::SQS::Queue\n"
        matches = rule.match(_decoded_template(template))
        self.assertEqual(1, len(matches))

    def test_non_list_additional_low_value_types_is_ignored(self):
        # If config somehow holds a non-list value, the guard returns []
        # rather than crashing (else [] branch in _extra_low_value_types).
        rule = ContextMissing()
        rule.config["require_context"] = True
        rule.config["additional_low_value_types"] = "not-a-list"
        template = "Resources:\n  Queue:\n    Type: AWS::SQS::Queue\n"
        matches = rule.match(_decoded_template(template))
        self.assertEqual(1, len(matches))

    def test_non_list_additional_incidental_patterns_is_ignored(self):
        # Same guard for additional_incidental_patterns (else [] branch).
        rule = ContextMissing()
        rule.config["require_context"] = True
        rule.config["additional_incidental_patterns"] = "not-a-list"
        template = "Resources:\n  Queue:\n    Type: AWS::SQS::Queue\n"
        matches = rule.match(_decoded_template(template))
        self.assertEqual(1, len(matches))


def _decoded_template(template_str):
    return Template("test.yaml", cfn_yaml.loads(template_str))
