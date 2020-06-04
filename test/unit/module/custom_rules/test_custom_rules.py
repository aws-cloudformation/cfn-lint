"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
import cfnlint.custom_rules
from six import StringIO
from mock import patch
from cfnlint.template import Template  # pylint: disable=E0401
from cfnlint.rules import RulesCollection
from cfnlint.core import DEFAULT_RULESDIR  # pylint: disable=E0401
import cfnlint.decode.cfn_yaml  # pylint: disable=E0401


class TestCustomRuleParsing(BaseTestCase):
    """Test Node Objects """

    def setUp(self):
        """ SetUp template object"""
        self.rules = RulesCollection()
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.create_from_directory(rulesdir)

        self.filenames = {
            "generic_good": {
                "filename": 'test/fixtures/templates/good/generic.yaml'
            }
        }
        self.valid_rule = 'test/fixtures/custom_rules/good/custom_rule_test.txt'
        self.perfect_rule = 'test/fixtures/custom_rules/good/custom_rule_perfect.txt'
        self.invalid_op = 'test/fixtures/custom_rules/bad/custom_rule_invalid_op.txt'
        self.invalid_prop = 'test/fixtures/custom_rules/bad/custom_rule_invalid_prop.txt'
        self.invalid_propkey = 'test/fixtures/custom_rules/bad/custom_rule_invalid_propkey.txt'
        self.invalid_rt = 'test/fixtures/custom_rules/bad/custom_rule_invalid_rt.txt'

    def test_success_parse(self):
        """Test Successful Custom_Rule Parsing"""
        assert(self.run_tests(self.valid_rule).find('Not Equal') > -1)

    def test_perfect_parse(self):
        """Test Successful Custom_Rule Parsing"""
        for _, values in self.filenames.items():
            filename = values.get('filename')
            template = cfnlint.decode.cfn_yaml.load(filename)
            cfn = Template(filename, template, ['us-east-1'])
            matches = cfnlint.custom_rules.check(self.perfect_rule, cfn)
            assert (matches == [])

    def test_invalid_op(self):
        """Test Successful Custom_Rule Parsing"""
        assert (self.run_tests(self.invalid_op).find('not in supported') > -1)

    def test_invalid_prop(self):
        """Test Successful Custom_Rule Parsing"""
        assert (self.run_tests(self.invalid_prop).find('property was not found') > -1)

    def test_invalid_propKey(self):
        """Test Successful Custom_Rule Parsing"""
        assert (self.run_tests(self.invalid_propkey).find('property was not found') > -1)

    def test_invalid_resource_type(self):
        """Test Successful Custom_Rule Parsing"""
        assert (self.run_tests(self.invalid_rt).find('Resource type not found') > -1)

    def run_tests(self, rulename):
        for _, values in self.filenames.items():
            filename = values.get('filename')
            template = cfnlint.decode.cfn_yaml.load(filename)
            cfn = Template(filename, template, ['us-east-1'])
            return cfnlint.custom_rules.check(rulename, cfn)[0].message
