"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import sys
import json
import subprocess
from test.testlib.testcase import BaseTestCase


class BaseCliTestCase(BaseTestCase):
    """Used for Testing CLI"""
    scenarios = []

    def setUp(self):
        """ Common Settings """
        self.maxDiff = None

    def run_scenarios(self, extra_params=None):
        """Success test"""
        extra_params = extra_params or []
        for scenario in self.scenarios:
            filename = scenario.get('filename')
            results_filename = scenario.get('results_filename')
            expected_results = scenario.get('results', [])
            exit_code = scenario.get('exit_code')

            if results_filename and not expected_results:
                with open(results_filename) as json_data:
                    expected_results = json.load(json_data)

            try:
                result = subprocess.check_output(['cfn-lint'] + extra_params + ['--format', 'json',
                                                                                '--', filename])

                self.assertEqual(0, exit_code, 'Expected {} exit code, got {} on {}'.format(
                    exit_code, 0, filename))

                if isinstance(result, bytes):
                    result = result.decode('utf8')
                matches = json.loads(result)

                if sys.version_info[0] >= 3:
                    self.assertCountEqual(expected_results, matches, 'Expected {} failures, got {} on {}'.format(
                        len(expected_results), len(matches), filename))
                else:
                    self.assertItemsEqual(expected_results, matches, 'Expected {} failures, got {} on {}'.format(
                        len(expected_results), len(matches), filename))

            except subprocess.CalledProcessError as error:
                self.assertEqual(error.returncode, exit_code, 'Expected {} exit code, got {} on {}'.format(
                    exit_code, error.returncode, filename))

                if isinstance(error.output, bytes):
                    error.output = error.output.decode('utf8')
                matches = json.loads(error.output)

                if sys.version_info[0] >= 3:
                    self.assertCountEqual(expected_results, matches, 'Expected {} failures, got {} on {}'.format(
                        len(expected_results), len(matches), filename))
                else:
                    self.assertItemsEqual(expected_results, matches, 'Expected {} failures, got {} on {}'.format(
                        len(expected_results), len(matches), filename))
