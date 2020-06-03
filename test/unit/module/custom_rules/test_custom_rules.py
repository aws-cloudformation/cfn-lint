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
        self.customrules = 'test/fixtures/templates/good/custom_rule_test.txt'

    def test_success_parse(self):
        """Test Successful YAML Parsing"""
        for _, values in self.filenames.items():
            filename = values.get('filename')
            failures = values.get('failures')
            template = cfnlint.decode.cfn_yaml.load(filename)
            cfn = Template(filename, template, ['us-east-1'])
            matches = cfnlint.custom_rules.check(self.customrules, cfn)
            assert (matches[0].message.find('Not Equal') > -1)
