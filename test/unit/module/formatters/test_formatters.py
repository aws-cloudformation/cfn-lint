"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from test.testlib.testcase import BaseTestCase
import cfnlint.formatters


class TestFormatters(BaseTestCase):
    """Test Formatters """

    def test_json_formatter(self):
        """Test JSON formatter"""

        # Run a broken template
        filename = 'test/fixtures/templates/bad/formatters.yaml'
        linter = cfnlint.CliLinter(['--template', filename, '--format',
                                    'json', '--include-checks', 'I'])

        linter.lint()

        # Validate Formatter class initiated
        self.assertEqual('JsonFormatter', linter.formatter.__class__.__name__)
        # We need 3 errors (Information, Warning, Error)
        self.assertEqual(len(linter.matches), 3)
        # Check the errors
        self.assertEqual(linter.matches[0].rule.id, 'I3011')
        self.assertEqual(linter.matches[1].rule.id, 'W1020')
        self.assertEqual(linter.matches[2].rule.id, 'E3012')

        # Get the JSON output
        json_results = json.loads(linter.formatter.print_matches(linter.matches))

        # Check the 3 errors again
        self.assertEqual(len(json_results), 3)

        # Check the errors level description
        self.assertEqual(json_results[0]['Level'], 'Informational')
        self.assertEqual(json_results[1]['Level'], 'Warning')
        self.assertEqual(json_results[2]['Level'], 'Error')
