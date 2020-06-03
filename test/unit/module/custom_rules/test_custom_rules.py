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
        self.valid_rule = 'test/fixtures/templates/good/custom_rule_test.txt'
        self.invalid_op = 'test/fixtures/templates/bad/custom_rule_invalid_op.txt'
        self.invalid_prop = 'test/fixtures/templates/bad/custom_rule_invalid_prop.txt'
        self.invalid_propkey = 'test/fixtures/templates/bad/custom_rule_invalid_propkey.txt'
        self.invalid_rt = 'test/fixtures/templates/bad/custom_rule_invalid_rt.txt'

    def test_success_parse(self):
        """Test Successful YAML Parsing"""
        for _, values in self.filenames.items():
            filename = values.get('filename')
            failures = values.get('failures')
            template = cfnlint.decode.cfn_yaml.load(filename)
            cfn = Template(filename, template, ['us-east-1'])
            matches = cfnlint.custom_rules.check(self.valid_rule, cfn)
            assert (matches[0].message.find('Not Equal') > -1)

    def test_invalid_op(self):
        """Test Successful YAML Parsing"""
        for _, values in self.filenames.items():
            filename = values.get('filename')
            failures = values.get('failures')
            template = cfnlint.decode.cfn_yaml.load(filename)
            cfn = Template(filename, template, ['us-east-1'])
            matches = cfnlint.custom_rules.check(self.invalid_op, cfn)
            assert (matches[0].message.find('not in supported') > -1)

    def test_invalid_prop(self):
        """Test Successful YAML Parsing"""
        for _, values in self.filenames.items():
            filename = values.get('filename')
            failures = values.get('failures')
            template = cfnlint.decode.cfn_yaml.load(filename)
            cfn = Template(filename, template, ['us-east-1'])
            matches = cfnlint.custom_rules.check(self.invalid_prop, cfn)
            assert (matches[0].message.find('property was not found') > -1)

    def test_invalid_propKey(self):
        """Test Successful YAML Parsing"""
        for _, values in self.filenames.items():
            filename = values.get('filename')
            failures = values.get('failures')
            template = cfnlint.decode.cfn_yaml.load(filename)
            cfn = Template(filename, template, ['us-east-1'])
            matches = cfnlint.custom_rules.check(self.invalid_propkey, cfn)
            assert (matches[0].message.find('property was not found') > -1)

    def test_invalid_resource_type(self):
        """Test Successful YAML Parsing"""
        for _, values in self.filenames.items():
            filename = values.get('filename')
            failures = values.get('failures')
            template = cfnlint.decode.cfn_yaml.load(filename)
            cfn = Template(filename, template, ['us-east-1'])
            matches = cfnlint.custom_rules.check(self.invalid_rt, cfn)
            assert (matches[0].message.find('Invalid Resource Type') > -1)
