"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to
  deal in the Software without restriction, including without limitation the
  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
  sell copies of the Software, and to permit persons to whom the Software is
  furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  THE SOFTWARE.
"""
from copy import copy
from mock import patch
from six import StringIO
import cfnlint
import cfnlint.template
import cfnlint.helpers  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


class TestTemplateLint(BaseTestCase):
    """Test Run Checks """

    def test_init(self):
        """test invalid rules"""

        filename = 'test/fixtures/templates/good/generic.yaml'
        linter = cfnlint.Linter(
            ['--', filename])

        template_linter = cfnlint.template.TemplateLinter(
            config=linter.config,
            filename=linter.config.templates[0])

        self.assertEqual(template_linter.filename, filename)
        self.assertEqual(template_linter.config.regions, ['us-east-1'])

    def test_init_inline(self):
        """ Test Inline """

        filename = None
        file_content = '''
          Metadata:
            cfn-lint:
              config:
                regions:
                - us-east-1
                - us-east-2
        '''

        with patch('sys.stdin', StringIO(file_content)):
            linter = cfnlint.Linter()
            self.assertEqual(linter.config.templates, filename)

            template_linter = cfnlint.template.TemplateLinter(
                config=linter.config,
                filename=filename)
            matches = template_linter.decode()
            self.assertEqual(matches, [])
            self.assertEqual(
                template_linter.config.regions,
                ['us-east-1', 'us-east-2'])

    def test_init_multiple_templates(self):
        """ Test Inline """

        # We are mimicing what happens inside cfnlint.Linter.lint() function
        # to validate the logic there since the TemplateLinter gets
        # re-initialized.  Hence the copy of the cfnlint.config item.  Those
        # items are not kept but we need to test how config is handled between
        # them

        filename = None
        file_content_1 = '''
          Metadata:
            cfn-lint:
              config:
                regions:
                - us-east-1
                - us-east-2
        '''
        file_content_2 = '''
          Metadata:
            cfn-lint:
              config:
                regions:
                - ca-central-1
        '''
        linter = cfnlint.Linter()

        template_linter_1 = None
        with patch('sys.stdin', StringIO(file_content_1)):
            template_linter_1 = cfnlint.template.TemplateLinter(
                config=linter.config,
                filename=filename)
            matches = template_linter_1.decode()
            self.assertEqual(matches, [])
            self.assertEqual(
                template_linter_1.config.regions,
                ['us-east-1', 'us-east-2'])

        template_linter_2 = None
        with patch('sys.stdin', StringIO(file_content_2)):
            template_linter_2 = cfnlint.template.TemplateLinter(
                linter.config, filename)
            matches = template_linter_2.decode()
            self.assertEqual(matches, [])
            self.assertEqual(
                template_linter_2.config.regions,
                ['ca-central-1'])

        self.assertEqual(
            linter.config.regions, ['us-east-1'],
            'Core config should not represent what was set by a template')

    def test_init_multiple_templates_with_core_config(self):
        """ Test Inline """

        # We are mimicing what happens inside cfnlint.Linter.lint() function
        # to validate the logic there since the TemplateLinter gets
        # re-initialized.  Hence the copy of the cfnlint.config item.  Those
        # items are not kept but we need to test how config is handled between
        # them

        filename = None
        file_content_1 = '''
          Metadata:
            cfn-lint:
              config:
                regions:
                - us-east-1
                - us-east-2
        '''
        file_content_2 = '''
          Metadata:
            cfn-lint:
              config:
                ignore_checks:
                - E3001
        '''
        linter = cfnlint.Linter(['--regions', 'ap-east-1'])

        template_linter_1 = None
        with patch('sys.stdin', StringIO(file_content_1)):
            template_linter_1 = cfnlint.template.TemplateLinter(
                config=linter.config,
                filename=filename)
            matches = template_linter_1.decode()
            self.assertEqual(matches, [])
            # active config is still ap-east-1
            self.assertEqual(
                template_linter_1.config.regions, ['ap-east-1'])
            # template is still parsed and has the correct values
            self.assertEqual(
                template_linter_1.config.template_args.get('regions'),
                ['us-east-1', 'us-east-2']
            )

        template_linter_2 = None
        with patch('sys.stdin', StringIO(file_content_2)):
            template_linter_2 = cfnlint.template.TemplateLinter(
                config=copy(linter.config),
                filename=filename)
            matches = template_linter_2.decode()
            self.assertEqual(matches, [])
            # active config for regions is ap-east-1
            self.assertEqual(
                template_linter_2.config.regions, ['ap-east-1'])
            # Has template override
            self.assertEqual(
                template_linter_2.config.ignore_checks, ['E3001']
            )

        # Core config remains unmodified
        self.assertEqual(
            linter.config.ignore_checks, [],
            'Core config should not represent what was set by a template')
