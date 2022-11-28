"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase

from cfnlint.rules import CloudFormationLintRule  # pylint: disable=E0401


class TestCloudFormationRule(BaseTestCase):
    """Test CloudFormation Rule"""

    def test_base(self):
        """Test Base Rule"""

        class TestRule(CloudFormationLintRule):
            """Def Rule"""

            id = "E1000"
            shortdesc = "Test Rule"
            description = "Test Rule Description"
            source_url = "https://github.com/aws-cloudformation/cfn-python-lint/"
            tags = ["resources"]

        self.assertEqual(TestRule.id, "E1000")
        self.assertEqual(TestRule.shortdesc, "Test Rule")
        self.assertEqual(TestRule.description, "Test Rule Description")
        self.assertEqual(
            TestRule.source_url,
            "https://github.com/aws-cloudformation/cfn-python-lint/",
        )
        self.assertEqual(TestRule.tags, ["resources"])

    def test_config(self):
        """Test Configuration"""

        class TestRule(CloudFormationLintRule):
            """Def Rule"""

            id = "E1000"
            shortdesc = "Test Rule"
            description = "Test Rule"
            source_url = "https://github.com/aws-cloudformation/cfn-python-lint/"
            tags = ["resources"]

            def __init__(self):
                """Init"""
                super(TestRule, self).__init__()
                self.config_definition = {
                    "testBoolean": {"default": True, "type": "boolean"},
                    "testString": {"default": "default", "type": "string"},
                    "testInteger": {"default": 1, "type": "integer"},
                }
                self.configure()

            def get_config(self):
                """Get the Config"""
                return self.config

        rule = TestRule()
        config = rule.get_config()
        self.assertTrue(config.get("testBoolean"))
        self.assertEqual(config.get("testString"), "default")
        self.assertEqual(config.get("testInteger"), 1)

        rule.configure({"testBoolean": "false", "testString": "new", "testInteger": 2})

        self.assertFalse(config.get("testBoolean"))
        self.assertEqual(config.get("testString"), "new")
        self.assertEqual(config.get("testInteger"), 2)
