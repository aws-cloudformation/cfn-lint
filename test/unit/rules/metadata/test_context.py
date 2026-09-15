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
    _expected_shape,
)
from cfnlint.template import Template


def _match(rule, template_str):
    """Decode a template string and run one rule's match() against it."""
    decoded = cfn_yaml.loads(template_str)
    cfn = Template("test.yaml", decoded)
    return rule.match(cfn)


def _decoded_template(template_str):
    """Decode a template string into a Template, for tests that reuse a rule."""
    return Template("test.yaml", cfn_yaml.loads(template_str))


def _missing_rule():
    """ContextMissing: flags templates and architecture-relevant resources."""
    return ContextMissing()


class TestContextMissing(BaseTestCase):
    """I4010 missing-context: significance gate + two-finding aggregate."""

    def test_flags_single_significant_resource(self):
        template = "Resources:\n  OrderQueue:\n    Type: AWS::SQS::Queue\n"
        self.assertEqual(1, len(_match(ContextMissing(), template)))

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
        # Primary lists both significant resources; no children (aggregate only).
        self.assertIn("OrderQueue", aggregate.message)
        self.assertIn("OrdersTable", aggregate.message)
        # No LogGroup is required or mentioned anywhere.
        all_text = " ".join(m.message for m in matches)
        self.assertNotIn("LogGroup", all_text)

    def test_single_significant_resource_has_no_template_finding(self):
        template = "Resources:\n  OrderQueue:\n    Type: AWS::SQS::Queue\n"
        matches = _match(_missing_rule(), template)
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

    def test_non_dict_resource_is_skipped(self):
        template = "Resources:\n  Malformed: not-a-dict\n"
        self.assertEqual([], _match(_missing_rule(), template))

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
        self.assertEqual([], _match(_missing_rule(), template))

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
        self.assertEqual([], _match(_missing_rule(), template))

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
        matches = _match(_missing_rule(), template)
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
        matches = _match(_missing_rule(), template)
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
            matches = _match(_missing_rule(), template)
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
            "            - I4011\n"
            "  QueueB:\n"
            "    Type: AWS::SQS::Queue\n"
        )
        matches = _match(_missing_rule(), template)
        self.assertEqual(2, len(matches))
        aggregate = next(
            m for m in matches if not m.message.startswith("This template")
        )
        self.assertIn("QueueA", aggregate.message)


class TestContextMissingWhy(BaseTestCase):
    """I4011 missing-why: flags blocks with no 'why' and no trust."""

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
        self.assertEqual([], _match(ContextMissingWhy(), template))

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
        matches = _match(ContextMissingWhy(), template)
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
        self.assertEqual([], _match(ContextMissingWhy(), template))

    def test_resource_without_a_context_block_is_not_flagged(self):
        template = "Resources:\n  OrderQueue:\n    Type: AWS::SQS::Queue\n"
        self.assertEqual([], _match(ContextMissingWhy(), template))

    def test_trust_block_alone_not_flagged_for_missing_why(self):
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
        self.assertEqual([], _match(ContextMissingWhy(), template))

    def test_high_confidence_trust_does_not_excuse_a_missing_why(self):
        # conf: high claims the rationale IS known, so it is not an escape
        # hatch; only low/medium acknowledge undocumented rationale.
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
        matches = _match(ContextMissingWhy(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("OrderQueue", matches[0].message)

    def test_low_value_resource_with_context_but_no_why_is_flagged(self):
        # Low-value types are exempt from I4010 (missing-context), but I4011
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
        self.assertEqual([], _match(ContextMissing(), template))
        # ...but I4011 still flags missing-why.
        matches = _match(ContextMissingWhy(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("ServiceLogGroup", matches[0].message)

    def test_module_with_context_but_no_why_is_flagged(self):
        # MODULE pseudo-resources are exempt from I4010, but I4011 still
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
        self.assertEqual([], _match(ContextMissing(), template))
        # ...but I4011 still flags missing-why.
        matches = _match(ContextMissingWhy(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("MyModule", matches[0].message)


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
        self.assertEqual([], _match(ContextSchemaViolation(), template))

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
            "        unrecognizedfield: 1\n"
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

    def test_resource_context_block_that_is_not_a_mapping(self):
        template = (
            "Resources:\n"
            "  Fn:\n"
            "    Type: AWS::Lambda::Function\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}: just a string\n"
        )
        matches = _match(ContextSchemaViolation(), template)
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
        matches = _match(ContextSchemaViolation(), template)
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
        matches = _match(ContextSchemaViolation(), template)
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
        messages = [m.message for m in _match(ContextSchemaViolation(), template)]
        self.assertTrue(
            any("one of: must-never-change" in message for message in messages),
            messages,
        )

    def test_expected_shape_for_ref_entry_array(self):
        template = f"Metadata:\n  {CONTEXT_KEY}:\n    arch: ok\n    ref: 5\n"
        matches = _match(ContextSchemaViolation(), template)
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
        matches = _match(ContextSchemaViolation(), template)
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
        matches = _match(ContextSchemaViolation(), template)
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
        self.assertEqual([], _match(ContextSchemaViolation(), template))

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
        matches = _match(ContextSchemaViolation(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("array of strings", matches[0].message)


class TestTargetingAndConfig(BaseTestCase):
    """Shared targeting policy and configuration options."""

    def test_cdk_metadata_resource_is_incidental(self):
        template = "Resources:\n  CDKMetadata:\n    Type: AWS::CDK::Metadata\n"
        self.assertEqual([], _match(_missing_rule(), template))

    def test_cdk_metadata_logical_id_with_other_type_is_incidental(self):
        template = "Resources:\n  CDKMetadata:\n    Type: AWS::SQS::Queue\n"
        self.assertEqual([], _match(_missing_rule(), template))

    def test_cdk_path_provider_segment_is_incidental(self):
        # The (?:^|/)Provider(?:/|$) alternative in _INCIDENTAL_PATH_PATTERN marks
        # a resource incidental when its aws:cdk:path contains a /Provider/ segment,
        # even if the path does NOT contain a framework-* handler suffix. This test
        # isolates that branch -- removing the /Provider/ alternative from the pattern
        # would cause this test to fail, since 'Provider' alone does not match the
        # framework-onEvent|isComplete|onTimeout alternatives.
        template = (
            "Resources:\n"
            "  StackHelperFn:\n"
            "    Type: AWS::Lambda::Function\n"
            "    Metadata:\n"
            "      aws:cdk:path: Stack/MyResource/Provider/Resource\n"
        )
        self.assertEqual([], _match(_missing_rule(), template))

    def test_non_string_resource_type_is_not_low_value(self):
        template = "Resources:\n  Weird:\n    Type:\n      - AWS::SQS::Queue\n"
        self.assertEqual(1, len(_match(_missing_rule(), template)))

    def test_module_pseudo_resource_is_not_required_to_carry_context(self):
        template = (
            "Resources:\n"
            "  MyModule:\n"
            "    Type: AWS::S3::Bucket::MODULE\n"
            "    Properties: {}\n"
        )
        self.assertEqual([], _match(_missing_rule(), template))

    def test_module_does_not_count_toward_the_template_finding(self):
        template = (
            "Resources:\n"
            "  MyModule:\n"
            "    Type: AWS::S3::Bucket::MODULE\n"
            "    Properties: {}\n"
            "  OrderQueue:\n"
            "    Type: AWS::SQS::Queue\n"
        )
        matches = _match(_missing_rule(), template)
        self.assertEqual(1, len(matches))
        self.assertFalse(matches[0].message.startswith("This template"))
        self.assertNotIn("MyModule", matches[0].message)

    def test_supplied_context_on_a_module_is_still_validated(self):
        template = (
            "Resources:\n"
            "  MyModule:\n"
            "    Type: AWS::S3::Bucket::MODULE\n"
            "    Properties: {}\n"
            "    Metadata:\n"
            f"      {CONTEXT_KEY}:\n"
            "        why: wraps the shared bucket conventions\n"
            "        must: not a list\n"
        )
        self.assertEqual([], _match(_missing_rule(), template))
        matches = _match(ContextSchemaViolation(), template)
        self.assertEqual(1, len(matches))
        self.assertIn("MyModule", matches[0].message)
        self.assertIn("array of strings", matches[0].message)

    def test_framework_handler_logical_ids_are_incidental(self):
        # CFN strips hyphens (framework-onEvent -> frameworkonEvent).
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

    def test_aws_custom_resource_singleton_is_incidental(self):
        # The AwsCustomResource provider singleton has a fixed logical ID derived
        # from lambdaPurpose + uuid (AWS679f53fac002430cb0da5b7982bd2287). Changing
        # this ID would orphan deployed functions, so the pattern anchors it exactly.
        # This test isolates that branch -- removing the singleton alternative from
        # _INCIDENTAL_ID_PATTERN would cause this test to fail, since the ID does
        # not match LogRetention, Provider(?=framework), or framework*.
        template = (
            "Resources:\n"
            "  AWS679f53fac002430cb0da5b7982bd2287:\n"
            "    Type: AWS::Lambda::Function\n"
        )
        self.assertEqual([], _match(_missing_rule(), template))

    def test_provider_framework_logical_id_is_incidental(self):
        # The (?<=[a-z])Provider(?=framework) alternative in _INCIDENTAL_ID_PATTERN
        # matches IDs where 'Provider' immediately precedes 'framework' but the
        # suffix is NOT one of the known handler names (onEvent/isComplete/onTimeout).
        # This test isolates that branch -- removing Provider(?=framework) from the
        # pattern would cause the test to fail, since 'frameworkHandler' does not
        # match the frameworkonEvent|frameworkisComplete|frameworkonTimeout ones.
        template = (
            "Resources:\n"
            "  AppProviderframeworkHandler123:\n"
            "    Type: AWS::Lambda::Function\n"
        )
        self.assertEqual([], _match(_missing_rule(), template))

    def test_provider_substring_does_not_over_match(self):
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

    def test_gaps_field_is_now_a_schema_violation(self):
        template = (
            f"Metadata:\n  {CONTEXT_KEY}:\n    arch: ok\n    gaps:\n      - some gap\n"
        )
        matches = _match(ContextSchemaViolation(), template)
        self.assertTrue(
            any("not a recognized Context field" in m.message for m in matches)
        )

    def test_additional_low_value_types_config_excludes(self):
        rule = ContextMissing()
        rule.config["additional_low_value_types"] = ["AWS::Events::EventBus"]
        template = "Resources:\n  Bus:\n    Type: AWS::Events::EventBus\n"
        self.assertEqual([], rule.match(_decoded_template(template)))

    def test_additional_incidental_patterns_config_excludes(self):
        rule = ContextMissing()
        rule.config["additional_incidental_patterns"] = ["MyHelper"]
        template = "Resources:\n  MyHelperQueue:\n    Type: AWS::SQS::Queue\n"
        self.assertEqual([], rule.match(_decoded_template(template)))

    def test_additional_incidental_pattern_matching_neither_candidate(self):
        rule = ContextMissing()
        rule.config["additional_incidental_patterns"] = ["NoSuchThing"]
        template = "Resources:\n  OrderQueue:\n    Type: AWS::SQS::Queue\n"
        self.assertEqual(1, len(rule.match(_decoded_template(template))))

    def test_severity_is_informational(self):
        self.assertEqual("informational", ContextMissing().severity)

    def test_invalid_regex_in_additional_incidental_patterns_is_skipped(self):
        rule = ContextMissing()
        rule.config["additional_incidental_patterns"] = ["[invalid"]
        template = "Resources:\n  Queue:\n    Type: AWS::SQS::Queue\n"
        matches = rule.match(_decoded_template(template))
        self.assertEqual(1, len(matches))

    def test_non_list_additional_low_value_types_is_ignored(self):
        rule = ContextMissing()
        rule.config["additional_low_value_types"] = "not-a-list"
        template = "Resources:\n  Queue:\n    Type: AWS::SQS::Queue\n"
        matches = rule.match(_decoded_template(template))
        self.assertEqual(1, len(matches))

    def test_non_list_additional_incidental_patterns_is_ignored(self):
        rule = ContextMissing()
        rule.config["additional_incidental_patterns"] = "not-a-list"
        template = "Resources:\n  Queue:\n    Type: AWS::SQS::Queue\n"
        matches = rule.match(_decoded_template(template))
        self.assertEqual(1, len(matches))


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
        # I4010 is the only rule that exempts low-value types, so it registers
        # both config options.
        self.assertEqual(
            sorted(ContextMissing().config_definition.keys()),
            ["additional_incidental_patterns", "additional_low_value_types"],
        )

    def test_config_surface_i4011_has_only_incidental_patterns(self):
        # I4011 validates supplied context everywhere -- low-value types are
        # not exempt -- so it exposes only additional_incidental_patterns.
        self.assertEqual(
            sorted(ContextMissingWhy().config_definition.keys()),
            ["additional_incidental_patterns"],
        )

    def test_config_surface_i4012_has_only_incidental_patterns(self):
        # I4012 validates supplied context everywhere -- low-value types are
        # not exempt -- so it exposes only additional_incidental_patterns.
        self.assertEqual(
            sorted(ContextSchemaViolation().config_definition.keys()),
            ["additional_incidental_patterns"],
        )
