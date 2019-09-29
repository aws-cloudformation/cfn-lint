"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from cfnlint.rules import CloudFormationLintRule  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


class TestCloudFormationRule(BaseTestCase):
    """ Test CloudFormation Rule """
    def test_base(self):
        """ Test Base Rule """
        class TestRule(CloudFormationLintRule):
            """ Def Rule """
            id = 'E1000'
            shortdesc = 'Test Rule'
            description = 'Test Rule Description'
            source_url = 'https://github.com/aws-cloudformation/cfn-python-lint/'
            tags = ['resources']

        self.assertEqual(TestRule.id, 'E1000')
        self.assertEqual(TestRule.shortdesc, 'Test Rule')
        self.assertEqual(TestRule.description, 'Test Rule Description')
        self.assertEqual(TestRule.source_url, 'https://github.com/aws-cloudformation/cfn-python-lint/')
        self.assertEqual(TestRule.tags, ['resources'])

    def test_config(self):
        """ Test Configuration """
        class TestRule(CloudFormationLintRule):
            """ Def Rule """
            id = 'E1000'
            shortdesc = 'Test Rule'
            description = 'Test Rule'
            source_url = 'https://github.com/aws-cloudformation/cfn-python-lint/'
            tags = ['resources']

            def __init__(self):
                """Init"""
                super(TestRule, self).__init__()
                self.config_definition = {
                    'testBoolean': {
                        'default': True,
                        'type': 'boolean'
                    },
                    'testString': {
                        'default': 'default',
                        'type': 'string'
                    },
                    'testInteger': {
                        'default': 1,
                        'type': 'integer'
                    }
                }
                self.configure()

            def get_config(self):
                """ Get the Config """
                return self.config

        rule = TestRule()
        config = rule.get_config()
        self.assertTrue(config.get('testBoolean'))
        self.assertEqual(config.get('testString'), 'default')
        self.assertEqual(config.get('testInteger'), 1)

        rule.configure({
            'testBoolean': 'false',
            'testString': 'new',
            'testInteger': 2
        })

        self.assertFalse(config.get('testBoolean'))
        self.assertEqual(config.get('testString'), 'new')
        self.assertEqual(config.get('testInteger'), 2)
