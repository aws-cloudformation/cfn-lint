"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase
from typing import Any, Dict

from cfnlint import ConfigMixIn
from cfnlint.decode.decode import decode_str
from cfnlint.rules import CloudFormationLintRule, Match, RuleMatch, Rules
from cfnlint.runner import TemplateRunner


class TestCloudFormationRuleChild(BaseTestCase):
    """Test CloudFormation Rule"""

    def test_child_rules(self) -> None:
        class TestRuleParent(CloudFormationLintRule):
            """Def Rule"""

            id = "E1000"
            shortdesc = "Test Rule"
            description = "Test Rule Description"
            source_url = "https://github.com/aws-cloudformation/cfn-lint/"
            tags = ["resources"]
            child_rules: Dict[str, Any] = {"E1001": None}

            def match(self, _):
                return self.child_rules["E1001"].failure()

        class TestRuleChild(CloudFormationLintRule):
            """Def Rule"""

            id = "E1001"
            shortdesc = "Test Rule"
            description = "Test Rule Description"
            source_url = "https://github.com/aws-cloudformation/cfn-lint/"
            tags = ["resources"]

            def failure(self):
                return [RuleMatch(["key"], "failure", rule=self)]

        rule_collection = Rules()
        test_rule_parent = TestRuleParent()
        test_rule_child = TestRuleChild()
        rule_collection.register(test_rule_parent)
        rule_collection.register(test_rule_child)

        template, _ = decode_str('{"key": "value"}')
        self.assertIsNotNone(template)
        if template is not None:
            runner = TemplateRunner(None, template, ConfigMixIn([]), rule_collection)
            failures = list(runner.run())

            self.assertListEqual(
                failures,
                [
                    Match(
                        linenumber=1,
                        columnnumber=2,
                        linenumberend=1,
                        columnnumberend=7,
                        filename=None,
                        rule=test_rule_child,
                        message="failure",
                    )
                ],
            )

    def test_child_rules_suppressed(self) -> None:
        class TestRuleParent(CloudFormationLintRule):
            """Def Rule"""

            id = "E1000"
            shortdesc = "Test Rule"
            description = "Test Rule Description"
            source_url = "https://github.com/aws-cloudformation/cfn-lint/"
            tags = ["resources"]
            child_rules: Dict[str, Any] = {"E1001": None}

            def match(self, _):
                if self.child_rules.get("E1001"):
                    return self.child_rules["E1001"].failure()
                return []

        class TestRuleChild(CloudFormationLintRule):
            """Def Rule"""

            id = "E1001"
            shortdesc = "Test Rule"
            description = "Test Rule Description"
            source_url = "https://github.com/aws-cloudformation/cfn-lint/"
            tags = ["resources"]

            def failure(self):
                return [RuleMatch(["key"], "failure", rule=self)]

        rule_collection = Rules()
        test_rule_parent = TestRuleParent()
        test_rule_child = TestRuleChild()
        rule_collection.register(test_rule_parent)
        rule_collection.register(test_rule_child)

        template, _ = decode_str('{"key": "value"}')
        self.assertIsNotNone(template)
        if template is not None:
            runner = TemplateRunner(
                None,
                template,
                ConfigMixIn(ignore_checks=["E1001"]),
                rule_collection,
            )
            failures = list(runner.run())

            self.assertListEqual(failures, [])

    def test_child_rules_configured(self) -> None:
        class TestRuleParent(CloudFormationLintRule):
            """Def Rule"""

            id = "E1000"
            shortdesc = "Test Rule"
            description = "Test Rule Description"
            source_url = "https://github.com/aws-cloudformation/cfn-lint/"
            tags = ["resources"]
            child_rules: Dict[str, Any] = {"E1001": None}

            def match(self, _):
                return self.child_rules["E1001"].failure()

        class TestRuleChild(CloudFormationLintRule):
            """Def Rule"""

            id = "E1001"
            shortdesc = "Test Rule"
            description = "Test Rule Description"
            source_url = "https://github.com/aws-cloudformation/cfn-lint/"
            tags = ["resources"]

            def __init__(self):
                """Init"""
                super(TestRuleChild, self).__init__()
                self.config_definition = {"pass": {"default": True, "type": "boolean"}}
                self.configure()

            def failure(self):
                if self.config["pass"]:
                    return [RuleMatch(["key"], "failure", rule=self)]
                return []

        rule_collection = Rules()
        test_rule_parent = TestRuleParent()
        test_rule_child = TestRuleChild()
        rule_collection.register(test_rule_parent)
        rule_collection.register(test_rule_child)

        template, _ = decode_str('{"key": "value"}')
        self.assertIsNotNone(template)
        if template is not None:
            runner = TemplateRunner(
                None,
                template,
                ConfigMixIn(configure_rules={"E1001": {"pass": False}}),
                rule_collection,
            )
            failures = list(runner.run())

            self.assertListEqual(failures, [])
