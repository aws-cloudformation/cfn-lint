"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
from cfnlint import Template
from cfnlint.rules import CloudFormationLintRule, RulesCollection
from cfnlint.core import DEFAULT_RULESDIR  # pylint: disable=E0401
import cfnlint.decode.cfn_yaml  # pylint: disable=E0401


class TestTemplate(BaseTestCase):
    """Test Template RulesCollection in cfnlint """

    def setUp(self):
        """ SetUp template object"""
        self.rules = RulesCollection()
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.create_from_directory(rulesdir)

    def test_rule_ids_unique(self):
        """Test Rule IDs are Unique"""
        existing_rules = []
        for rule in self.rules:
            self.assertFalse(rule.id in existing_rules)
            existing_rules.append(rule.id)

    def test_rule_ids_are_formatted_correctly(self):
        """Test Rule IDs are property formmated"""
        for rule in self.rules:
            self.assertIn(rule.id[0], ['W', 'I', 'E'])
            self.assertEqual(len(rule.id), 5)
            self.assertTrue(isinstance(int(rule.id[1:]), int))

    def test_success_run(self):
        """ Test Run Logic"""
        filename = 'test/fixtures/templates/good/generic.yaml'
        template = cfnlint.decode.cfn_yaml.load(filename)
        cfn = Template(filename, template, ['us-east-1'])

        matches = []
        matches.extend(self.rules.run(filename, cfn))
        assert(matches == [])

    def test_fail_run(self):
        """Test failure run"""
        filename = 'test/fixtures/templates/bad/generic.yaml'
        template = cfnlint.decode.cfn_yaml.load(filename)
        cfn = Template(filename, template, ['us-east-1'])
        expected_err_count = 35
        matches = []
        matches.extend(self.rules.run(filename, cfn))
        assert len(matches) == expected_err_count, 'Expected {} failures, got {}'.format(
            expected_err_count, len(matches))

    def test_fail_sub_properties_run(self):
        """Test failure run"""
        filename = 'test/fixtures/templates/bad/resources/properties/onlyone.yaml'
        template = cfnlint.decode.cfn_yaml.load(filename)
        cfn = Template(filename, template, ['us-east-1'])

        matches = []
        matches.extend(self.rules.run(filename, cfn))
        assert len(matches) == 6, 'Expected {} failures, got {}'.format(5, len(matches))

    def test_success_filtering_of_rules_default(self):
        """Test extend function"""
        class rule_e0000(CloudFormationLintRule):
            """Error Rule"""
            id = 'E0000'

        class rule_w0000(CloudFormationLintRule):
            """Warning Rule"""
            id = 'W0000'

        class rule_i0000(CloudFormationLintRule):
            """Info Rule"""
            id = 'I0000'

        rules_to_add = [rule_e0000, rule_w0000, rule_i0000]
        rules = RulesCollection(ignore_rules=None, include_rules=None)
        rules.extend(rules_to_add)
        self.assertEqual(len(rules), 2)
        for rule in rules:
            self.assertIn(rule.id, ['W0000', 'E0000'])

    def test_success_filtering_of_rules_include_info(self):
        """Test extend function"""
        class rule_e0000(CloudFormationLintRule):
            """Error Rule"""
            id = 'E0000'

        class rule_w0000(CloudFormationLintRule):
            """Warning Rule"""
            id = 'W0000'

        class rule_i0000(CloudFormationLintRule):
            """Info Rule"""
            id = 'I0000'

        rules_to_add = [rule_e0000, rule_w0000, rule_i0000]
        rules = RulesCollection(ignore_rules=None, include_rules=['I'])
        rules.extend(rules_to_add)
        self.assertEqual(len(rules), 3)
        for rule in rules:
            self.assertIn(rule.id, ['I0000', 'W0000', 'E0000'])

    def test_success_filtering_of_rules_exclude(self):
        """Test extend function"""
        class rule_e0000(CloudFormationLintRule):
            """Error Rule"""
            id = 'E0000'

        class rule_w0000(CloudFormationLintRule):
            """Warning Rule"""
            id = 'W0000'

        class rule_i0000(CloudFormationLintRule):
            """Info Rule"""
            id = 'I0000'

        rules_to_add = [rule_e0000, rule_w0000, rule_i0000]
        rules = RulesCollection(ignore_rules=['E'])
        rules.extend(rules_to_add)
        self.assertEqual(len(rules), 1)
        for rule in rules:
            self.assertIn(rule.id, ['W0000'])

    def test_success_filtering_of_rules_exclude_long(self):
        """Test extend function"""
        class rule_e0000(CloudFormationLintRule):
            """Error Rule"""
            id = 'E0000'

        class rule_e0010(CloudFormationLintRule):
            """Error Rule"""
            id = 'E0010'

        class rule_e0002(CloudFormationLintRule):
            """Error Rule"""
            id = 'E0002'

        rules_to_add = [rule_e0000, rule_e0010, rule_e0002]
        rules = RulesCollection(ignore_rules=['E000'])
        rules.extend(rules_to_add)
        self.assertEqual(len(rules), 1)
        for rule in rules:
            self.assertIn(rule.id, ['E0010'])

    def test_success_filtering_of_rules_exclude_longer(self):
        """Test extend function"""
        class rule_e0000(CloudFormationLintRule):
            """Error Rule"""
            id = 'E0000'

        class rule_e0010(CloudFormationLintRule):
            """Error Rule"""
            id = 'E0010'

        class rule_e0002(CloudFormationLintRule):
            """Error Rule"""
            id = 'E0002'

        rules_to_add = [rule_e0000, rule_e0010, rule_e0002]
        rules = RulesCollection(ignore_rules=['E0002'])
        rules.extend(rules_to_add)
        self.assertEqual(len(rules), 2)
        for rule in rules:
            self.assertIn(rule.id, ['E0000', 'E0010'])
