"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
from typing import Any, Dict

from cfnlint.decode import decode_str
from cfnlint.rules import CloudFormationLintRule  # pylint: disable=E0401
from cfnlint.rules import Match, RuleMatch, RulesCollection
from cfnlint.runner import Runner


class TestCloudFormationRuleChild(BaseTestCase):
    """Test CloudFormation Rule"""

    def test_child_rules(self):
        class TestRuleParent(CloudFormationLintRule):
            """Def Rule"""

            id = "E1000"
            shortdesc = "Test Rule"
            description = "Test Rule Description"
            source_url = "https://github.com/aws-cloudformation/cfn-python-lint/"
            tags = ["resources"]
            child_rules: Dict[str, Any] = {"E1001": None}

            def match(self, _):
                return self.child_rules["E1001"].failure()

        class TestRuleChild(CloudFormationLintRule):
            """Def Rule"""

            id = "E1001"
            shortdesc = "Test Rule"
            description = "Test Rule Description"
            source_url = "https://github.com/aws-cloudformation/cfn-python-lint/"
            tags = ["resources"]

            def failure(self):
                return [RuleMatch(["key"], "failure", rule=self)]

        rule_collection = RulesCollection()
        test_rule_parent = TestRuleParent()
        test_rule_child = TestRuleChild()
        rule_collection.register(test_rule_parent)
        rule_collection.register(test_rule_child)

        template, _ = decode_str('{"key": "value"}')
        runner = Runner(rule_collection, None, template, ["us-east-1"], [])
        failures = runner.run()

        self.assertListEqual(
            failures, [Match(1, 2, 1, 7, None, test_rule_child, "failure")]
        )

    def test_child_rules_suppressed(self):
        class TestRuleParent(CloudFormationLintRule):
            """Def Rule"""

            id = "E1000"
            shortdesc = "Test Rule"
            description = "Test Rule Description"
            source_url = "https://github.com/aws-cloudformation/cfn-python-lint/"
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
            source_url = "https://github.com/aws-cloudformation/cfn-python-lint/"
            tags = ["resources"]

            def failure(self):
                return [RuleMatch(["key"], "failure", rule=self)]

        rule_collection = RulesCollection(ignore_rules=["E1001"])
        test_rule_parent = TestRuleParent()
        test_rule_child = TestRuleChild()
        rule_collection.register(test_rule_parent)
        rule_collection.register(test_rule_child)

        template, _ = decode_str('{"key": "value"}')
        runner = Runner(rule_collection, None, template, ["us-east-1"], [])
        failures = runner.run()

        self.assertListEqual(failures, [])

    def test_child_rules_configured(self):
        class TestRuleParent(CloudFormationLintRule):
            """Def Rule"""

            id = "E1000"
            shortdesc = "Test Rule"
            description = "Test Rule Description"
            source_url = "https://github.com/aws-cloudformation/cfn-python-lint/"
            tags = ["resources"]
            child_rules: Dict[str, Any] = {"E1001": None}

            def match(self, _):
                return self.child_rules["E1001"].failure()

        class TestRuleChild(CloudFormationLintRule):
            """Def Rule"""

            id = "E1001"
            shortdesc = "Test Rule"
            description = "Test Rule Description"
            source_url = "https://github.com/aws-cloudformation/cfn-python-lint/"
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

        rule_collection = RulesCollection()
        test_rule_parent = TestRuleParent()
        test_rule_child = TestRuleChild()
        rule_collection.register(test_rule_parent)
        rule_collection.register(test_rule_child)
        rule_collection.configure(configure_rules={"E1001": {"pass": False}})

        template, _ = decode_str('{"key": "value"}')
        runner = Runner(rule_collection, None, template, ["us-east-1"], [])
        failures = runner.run()

        self.assertListEqual(failures, [])
