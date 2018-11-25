"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
from cfnlint import Runner, RulesCollection
from testlib.testcase import BaseTestCase


class BaseRuleTestCase(BaseTestCase):
    """Used for Testing Rules"""
    success_templates = [
    ]

    def setUp(self):
        """Setup"""
        self.collection = RulesCollection(include_rules=['I'])

    def helper_file_positive(self):
        """Success test"""
        for filename in self.success_templates:
            template = self.load_template(filename)
            good_runner = Runner(self.collection, filename, template, ['us-east-1'], [])
            good_runner.transform()
            failures = good_runner.run()
            assert [] == failures, 'Got failures {} on {}'.format(failures, filename)

    def helper_file_positive_template(self, filename):
        """Success test with template parameter"""
        template = self.load_template(filename)
        good_runner = Runner(self.collection, filename, template, ['us-east-1'], [])
        good_runner.transform()
        self.assertEqual([], good_runner.run())

    def helper_file_negative(self, filename, err_count, regions=None):
        """Failure test"""
        regions = regions or ['us-east-1']
        template = self.load_template(filename)
        bad_runner = Runner(self.collection, filename, template, regions, [])
        bad_runner.transform()
        errs = bad_runner.run()
        self.assertEqual(err_count, len(errs))
