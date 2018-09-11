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
from cfnlint.rules.resources.Configuration import Configuration  # pylint: disable=E0401
from testlib.testcase import BaseTestCase
import cfnlint.helpers
import json

class TestInclude(BaseTestCase):
    """Used for Testing Rules"""

    def setUp(self):
        """Setup"""
        self.collection = RulesCollection()
        self.collection.register(Configuration())

    def tearDown(self):
        """Tear Down"""
        # Reset the Spec override to prevent other tests to fail
        cfnlint.helpers.initialize_specs()

    def test_fail_run(self):
        """Failure test required"""
        filename = 'fixtures/templates/bad/override/include.yaml'
        template = self.load_template(filename)

        with open('fixtures/templates/override_spec/include.json') as fp:
            custom_spec = json.load(fp)
        cfnlint.helpers.set_specs(custom_spec)

        bad_runner = Runner(self.collection, filename, template, ['us-east-1'], [])
        errs = bad_runner.run()
        self.assertEqual(2, len(errs))
