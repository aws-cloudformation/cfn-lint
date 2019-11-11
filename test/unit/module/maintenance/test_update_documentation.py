"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import sys
import logging
from test.testlib.testcase import BaseTestCase
from mock import patch, mock_open, call
import cfnlint.maintenance
from cfnlint.rules import CloudFormationLintRule, RulesCollection

LOGGER = logging.getLogger('cfnlint.maintenance')
LOGGER.addHandler(logging.NullHandler())


class TestUpdateDocumentation(BaseTestCase):
    """Used for Testing Updating the Documentation"""

    TEST_TEXT = '''
Regular Text
## Rules
'''

    def test_update_iam_policies(self):
        """Success update documentation"""

        class TestRuleError(CloudFormationLintRule):
            """ Def Rule """
            id = 'E1000'
            shortdesc = 'Test Error'
            description = 'Test Description'
            source_url = 'https://github.com/aws-cloudformation/cfn-python-lint/'
            tags = ['resources']

        class TestRuleExpiremental(CloudFormationLintRule):
            """ Def Rule """
            id = 'E1001'
            shortdesc = 'Test Expiremental'
            description = 'Test Description'
            source_url = 'https://github.com/aws-cloudformation/cfn-python-lint/'
            tags = ['resources']
            experimental = True

        class TestRuleWarning(CloudFormationLintRule):
            """ Def Rule """
            id = 'W1001'
            shortdesc = 'Test Warning'
            description = 'Test Description'
            source_url = 'https://github.com/aws-cloudformation/cfn-python-lint/'
            tags = ['resources', 'iam']

        collection = RulesCollection(include_rules=['I'], include_experimental=True)
        collection.register(TestRuleError())
        collection.register(TestRuleWarning())
        collection.register(TestRuleExpiremental())

        if sys.version_info.major == 3:
            builtin_module_name = 'builtins'
        else:
            builtin_module_name = '__builtin__'

        mo = mock_open(read_data=self.TEST_TEXT)
        mo.return_value.__iter__ = lambda self: self
        mo.return_value.__iter__ = lambda self: iter(self.readline, '')
        with patch('{}.open'.format(builtin_module_name), mo) as mock_builtin_open:
            cfnlint.maintenance.update_documentation(collection)

            expected_calls = [
                call('\n'),
                call('Regular Text\n'),
                call('## Rules\n'),
                call('The following **{}** rules are applied by this linter:\n'.format(
                    len(collection))),
                call('(_This documentation is generated from the Rules, do not alter this manually_)\n\n'),
                call('| Rule ID  | Title | Description | Config<br />(Name:Type:Default) | Source | Tags |\n'),
                call('| -------- | ----- | ----------- | ---------- | ------ | ---- |\n'),
                call(
                    '| E0000<a name="E0000"></a> | Parsing error found when parsing the template | Checks for Null values and Duplicate values in resources |  | [Source]() | `base` |\n'),
                call(
                    '| E0001<a name="E0001"></a> | Error found when transforming the template | Errors found when performing transformation on the template |  | [Source]() | `base`,`transform` |\n'),
                call(
                    '| E0002<a name="E0002"></a> | Error processing rule on the template | Errors found when processing a rule on the template |  | [Source]() | `base`,`rule` |\n'),
                call(
                    '| E1000<a name="E1000"></a> | Test Error | Test Description |  | [Source](https://github.com/aws-cloudformation/cfn-python-lint/) | `resources` |\n'),
                call(
                    '| W1001<a name="W1001"></a> | Test Warning | Test Description |  | [Source](https://github.com/aws-cloudformation/cfn-python-lint/) | `resources`,`iam` |\n'),
                call('### Experimental rules\n'),
                call('| Rule ID  | Title | Description | Source | Tags |\n'),
                call('| -------- | ----- | ----------- | ------ | ---- |\n'),
                call(
                    '| E1001<a name="E1001"></a> | Test Expiremental | Test Description |  | [Source](https://github.com/aws-cloudformation/cfn-python-lint/) | `resources` |\n'),
            ]
            mock_builtin_open.return_value.write.assert_has_calls(expected_calls)
            self.assertEqual(len(expected_calls), mock_builtin_open.return_value.write.call_count)
