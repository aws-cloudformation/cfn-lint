"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

from cfnlint.rules import CloudFormationLintRule


class TestCloudFormationRule(BaseTestCase):
    """Test CloudFormation Rule"""

    def test_base(self):
        """Test Base Rule"""

        class TestRule(CloudFormationLintRule):
            """Def Rule"""

            id = "E1000"
            shortdesc = "Test Rule"
            description = "Test Rule Description"
            source_url = "https://github.com/aws-cloudformation/cfn-lint/"
            tags = ["resources"]

        self.assertEqual(TestRule.id, "E1000")
        self.assertEqual(TestRule.shortdesc, "Test Rule")
        self.assertEqual(TestRule.description, "Test Rule Description")
        self.assertEqual(
            TestRule.source_url,
            "https://github.com/aws-cloudformation/cfn-lint/",
        )
        self.assertEqual(TestRule.tags, ["resources"])

    def test_config(self):
        """Test Configuration"""

        class TestRule(CloudFormationLintRule):
            """Def Rule"""

            id = "E1000"
            shortdesc = "Test Rule"
            description = "Test Rule"
            source_url = "https://github.com/aws-cloudformation/cfn-lint/"
            tags = ["resources"]

            def __init__(self):
                """Init"""
                super(TestRule, self).__init__()
                self.config_definition = {
                    "testBoolean": {"default": True, "type": "boolean"},
                    "testString": {"default": "default", "type": "string"},
                    "testInteger": {"default": 1, "type": "integer"},
                    "testListBoolean": {
                        "type": "list",
                        "itemtype": "boolean",
                        "default": [False],
                    },
                    "testListString": {
                        "type": "list",
                        "itemtype": "string",
                        "default": ["bar"],
                    },
                    "testListInteger": {
                        "type": "list",
                        "itemtype": "integer",
                        "default": [0],
                    },
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
        self.assertListEqual(config.get("testListBoolean"), [False])
        self.assertListEqual(config.get("testListString"), ["bar"])
        self.assertListEqual(config.get("testListInteger"), [0])

        rule.configure(
            {
                "testBoolean": "false",
                "testString": "new",
                "testInteger": 2,
                "testListBoolean": ["true"],
                "testListString": ["foo"],
                "testListInteger": [1],
            }
        )

        self.assertFalse(config.get("testBoolean"))
        self.assertEqual(config.get("testString"), "new")
        self.assertEqual(config.get("testInteger"), 2)
        self.assertListEqual(config.get("testListBoolean"), [True])
        self.assertListEqual(config.get("testListString"), ["foo"])
        self.assertListEqual(config.get("testListInteger"), [1])

    def test_experimental(self):
        """Test Configuration"""

        class TestRule(CloudFormationLintRule):
            """Def Rule"""

            id = "E1000"
            shortdesc = "Test Rule"
            description = "Test Rule"
            source_url = "https://github.com/aws-cloudformation/cfn-lint/"
            tags = ["resources"]

            def __init__(self):
                """Init"""
                super(TestRule, self).__init__()
                self.config_definition = {
                    "experimental": {"default": True, "type": "boolean"},
                }
                self.configure()

            def get_config(self):
                """Get the Config"""
                return self.config

        rule = TestRule()
        rule.configure({}, True)
        config = rule.get_config()
        self.assertTrue(config.get("experimental"))

        rule.configure({}, False)
        config = rule.get_config()
        self.assertFalse(config.get("experimental"))

    def test_non_configured_experimental(self):
        class TestRule(CloudFormationLintRule):
            """Def Rule"""

            id = "E1000"
            shortdesc = "Test Rule"
            description = "Test Rule"
            source_url = "https://github.com/aws-cloudformation/cfn-lint/"
            tags = ["resources"]

        rule = TestRule()

        rule.configure({}, True)
        self.assertFalse(rule.config.get("experimental"))

    def test_none_equal(self):
        class TestRule(CloudFormationLintRule):
            """Def Rule"""

            id = "E1000"
            shortdesc = "Test Rule"
            description = "Test Rule"
            source_url = "https://github.com/aws-cloudformation/cfn-lint/"
            tags = ["resources"]

        rule = TestRule()

        self.assertNotEqual(rule, None)
