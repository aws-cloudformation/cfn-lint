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
from cfnlint import Runner, RulesCollection, TransformsCollection, DEFAULT_TRANSFORMSDIR
from testlib.testcase import BaseTestCase


class BaseRuleTestCase(BaseTestCase):
    """Used for Testing Rules"""
    success_templates = [
        'templates/good/generic.yaml',
        'templates/quickstart/nist_high_master.yaml',
        'templates/quickstart/nist_application.yaml',
        'templates/quickstart/nist_config_rules.yaml',
        'templates/quickstart/nist_iam.yaml',
        'templates/quickstart/nist_logging.yaml',
        'templates/quickstart/nist_vpc_management.yaml',
        'templates/quickstart/nist_vpc_production.yaml',
        'templates/quickstart/openshift_master.yaml',
        'templates/quickstart/openshift.yaml',
        'templates/quickstart/cis_benchmark.yaml',
        'templates/good/properties_ec2_vpc.yaml',
        'templates/good/minimal.yaml',
        'templates/good/transform.yaml',
        'templates/good/conditions.yaml',
        'templates/good/properties_elb.yaml',
        'templates/good/functions_sub.yaml',
        'templates/good/functions_cidr.yaml',
        'templates/good/resources_lambda.yaml',
        'templates/good/transform_serverless_api.yaml',
        'templates/good/transform_serverless_function.yaml',
        'templates/good/transform_serverless_globals.yaml',
    ]

    def setUp(self):
        """Setup"""
        self.collection = RulesCollection()
        self.transforms = TransformsCollection()
        self.transforms.extend(
            TransformsCollection.create_from_directory(DEFAULT_TRANSFORMSDIR))

    def helper_file_positive(self):
        """Success test"""
        for filename in self.success_templates:
            template = self.load_template(filename)
            good_runner = Runner(self.collection, self.transforms, filename, template, [], ['us-east-1'], [])
            good_runner.transform()
            self.assertEqual([], good_runner.run())

    def helper_file_positive_template(self, filename):
        """Success test with template parameter"""
        template = self.load_template(filename)
        good_runner = Runner(self.collection, self.transforms, filename, template, [], ['us-east-1'], [])
        good_runner.transform()
        self.assertEqual([], good_runner.run())

    def helper_file_negative(self, filename, err_count):
        """Failure test"""
        template = self.load_template(filename)
        bad_runner = Runner(self.collection, self.transforms, filename, template, [], ['us-east-1'], [])
        bad_runner.transform()
        errs = bad_runner.run()
        self.assertEqual(err_count, len(errs))
