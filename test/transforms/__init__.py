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
from cfnlint import Runner, TransformsCollection, DEFAULT_TRANSFORMSDIR
from testlib.testcase import BaseTestCase


class BaseTransformTestCase(BaseTestCase):
    """Used for Testing Transforms"""
    def setUp(self):
        """Setup"""
        self.transforms = TransformsCollection()
        self.transforms.extend(
            TransformsCollection.create_from_directory(DEFAULT_TRANSFORMSDIR))

    def helper_transform_template(self, template, test_function):
        """Success test with template parameter"""
        good_runner = Runner([], self.transforms, 'test', template, [], ['us-east-1'], [])
        good_runner.transform()
        self.assertTrue(test_function(good_runner.cfn.template))

    def helper_transform_cfn(self, template, test_function):
        """Test the bigger CFN template"""
        good_runner = Runner([], self.transforms, 'test', template, [], ['us-east-1'], [])
        good_runner.transform()
        self.assertTrue(test_function(good_runner.cfn))
