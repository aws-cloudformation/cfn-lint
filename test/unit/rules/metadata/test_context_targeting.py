"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase
from test.unit.rules.metadata._context_helpers import (
    decoded_template,
    match,
    missing_rule,
)

from cfnlint.rules.metadata._BaseContext import CONTEXT_KEY
from cfnlint.rules.metadata.ContextMissing import ContextMissing
from cfnlint.rules.metadata.ContextSchemaViolation import ContextSchemaViolation


class TestTargetingAndConfig(BaseTestCase):
    """Shared targeting policy and configuration options."""

    def test_cdk_metadata_resource_is_incidental(self):
        template = "Resources:\n  CDKMetadata:\n    Type: AWS::CDK::Metadata\n"
        self.assertEqual([], match(missing_rule(), template))

    def test_cdk_metadata_logical_id_with_other_type_is_incidental(self):
        template = "Resources:\n  CDKMetadata:\n    Type: AWS::SQS::Queue\n"
        self.assertEqual([], match(missing_rule(), template))

    def test_aws_cdk_path_marks_template_as_cdk(self):
        # Any resource carrying aws:cdk:path triggers _is_cdk_template, which
        # short-circuits match() to return [] before incidental-ID matching.
        # This covers CDK stacks synthesized with analyticsReporting: false
        # (no AWS::CDK::Metadata resource).
        template = (
            "Resources:\n"
            "  StackHelperFn:\n"
            "    Type: AWS::Lambda::Function\n"
            "    Metadata:\n"
            "      aws:cdk:path: Stack/MyResource/Provider/Resource\n"
        )
        self.assertEqual([], match(missing_rule(), template))

    def test_non_string_resource_type_is_not_low_value(self):
        template = "Resources:\n  Weird:\n    Type:\n      - AWS::SQS::Queue\n"
        self.assertEqual(1, len(match(missing_rule(), template)))

    def test_module_pseudo_resource_is_not_required_to_carry_context(self):
        template = (
            "Resources:\n"
            "  MyModule:\n"
            "    Type: AWS::S3::Bucket::MODULE\n"
            "    Properties: {}\n"
        )
        self.assertEqual([], match(missing_rule(), template))

    def test_module_does_not_count_toward_the_template_finding(self):
        template = (
            "Resources:\n"
            "  MyModule:\n"
            "    Type: AWS::S3::Bucket::MODULE\n"
            "    Properties: {}\n"
            "  OrderQueue:\n"
            "    Type: AWS::SQS::Queue\n"
        )
        matches = match(missing_rule(), template)
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
        self.assertEqual([], match(missing_rule(), template))
        matches = match(ContextSchemaViolation(), template)
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
        self.assertEqual([], match(missing_rule(), template))

    def test_aws_custom_resource_singleton_is_incidental(self):
        # Fixed logical ID (lambdaPurpose + uuid); changing it orphans deployed
        # functions. Isolates this branch -- the ID does not match LogRetention,
        # Provider(?=framework), or framework*.
        template = (
            "Resources:\n"
            "  AWS679f53fac002430cb0da5b7982bd2287:\n"
            "    Type: AWS::Lambda::Function\n"
        )
        self.assertEqual([], match(missing_rule(), template))

    def test_provider_framework_logical_id_is_incidental(self):
        # Isolates (?<=[a-z])Provider(?=framework) -- 'frameworkHandler' does not
        # match frameworkonEvent|isComplete|onTimeout.
        template = (
            "Resources:\n"
            "  AppProviderframeworkHandler123:\n"
            "    Type: AWS::Lambda::Function\n"
        )
        self.assertEqual([], match(missing_rule(), template))

    def test_provider_substring_does_not_over_match(self):
        template = (
            "Resources:\n"
            "  DataProviderTable:\n"
            "    Type: AWS::DynamoDB::Table\n"
            "  OrderProviderQueue:\n"
            "    Type: AWS::SQS::Queue\n"
        )
        matches = match(missing_rule(), template)
        self.assertEqual(2, len(matches))

    def test_gaps_field_is_now_a_schema_violation(self):
        template = (
            f"Metadata:\n  {CONTEXT_KEY}:\n    arch: ok\n    gaps:\n      - some gap\n"
        )
        matches = match(ContextSchemaViolation(), template)
        self.assertTrue(
            any("not a recognized Context field" in m.message for m in matches)
        )

    def test_additional_low_value_types_config_excludes(self):
        rule = ContextMissing()
        rule.config["additional_low_value_types"] = ["AWS::Events::EventBus"]
        template = "Resources:\n  Bus:\n    Type: AWS::Events::EventBus\n"
        self.assertEqual([], rule.match(decoded_template(template)))

    def test_additional_incidental_patterns_config_excludes(self):
        rule = ContextMissing()
        rule.config["additional_incidental_patterns"] = ["MyHelper"]
        template = "Resources:\n  MyHelperQueue:\n    Type: AWS::SQS::Queue\n"
        self.assertEqual([], rule.match(decoded_template(template)))

    def test_additional_incidental_pattern_matching_neither_candidate(self):
        rule = ContextMissing()
        rule.config["additional_incidental_patterns"] = ["NoSuchThing"]
        template = "Resources:\n  OrderQueue:\n    Type: AWS::SQS::Queue\n"
        self.assertEqual(1, len(rule.match(decoded_template(template))))

    def test_severity_is_informational(self):
        self.assertEqual("informational", ContextMissing().severity)

    def test_invalid_regex_in_additional_incidental_patterns_is_skipped(self):
        rule = ContextMissing()
        rule.config["additional_incidental_patterns"] = ["[invalid"]
        template = "Resources:\n  Queue:\n    Type: AWS::SQS::Queue\n"
        matches = rule.match(decoded_template(template))
        self.assertEqual(1, len(matches))

    def test_non_list_additional_low_value_types_is_ignored(self):
        rule = ContextMissing()
        rule.config["additional_low_value_types"] = "not-a-list"
        template = "Resources:\n  Queue:\n    Type: AWS::SQS::Queue\n"
        matches = rule.match(decoded_template(template))
        self.assertEqual(1, len(matches))

    def test_non_list_additional_incidental_patterns_is_ignored(self):
        rule = ContextMissing()
        rule.config["additional_incidental_patterns"] = "not-a-list"
        template = "Resources:\n  Queue:\n    Type: AWS::SQS::Queue\n"
        matches = rule.match(decoded_template(template))
        self.assertEqual(1, len(matches))
