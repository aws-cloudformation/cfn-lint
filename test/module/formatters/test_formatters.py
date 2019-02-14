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
import json
import cfnlint.formatters
from testlib.testcase import BaseTestCase


class TestFormatters(BaseTestCase):
    """Test Formatters """

    def test_json_formatter(self):
        """Test JSON formatter"""

        # Run a broken template
        filename = 'test/fixtures/templates/bad/formatters.yaml'
        (args, filenames, formatter) = cfnlint.core.get_args_filenames([
            '--template', filename, '--format', 'json', '--include-checks', 'I'])

        results = []
        for filename in filenames:
            (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
            results.extend(
                cfnlint.core.run_checks(
                    filename, template, rules, ['us-east-1']))

        # Validate Formatter class initiated
        self.assertEqual('JsonFormatter', formatter.__class__.__name__)
        # We need 3 errors (Information, Warning, Error)
        self.assertEqual(len(results), 3)
        # Check the errors
        self.assertEqual(results[0].rule.id, 'I3011')
        self.assertEqual(results[1].rule.id, 'W1020')
        self.assertEqual(results[2].rule.id, 'E3012')

        # Get the JSON output
        json_results = json.loads(formatter.print_matches(results))

        # Check the 3 errors again
        self.assertEqual(len(json_results), 3)
        
        # Check the errors level description
        self.assertEqual(json_results[0]['Level'], 'Informational')
        self.assertEqual(json_results[1]['Level'], 'Warning')
        self.assertEqual(json_results[2]['Level'], 'Error')
