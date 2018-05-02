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
from . import BaseTransformTestCase


class TestServerlessGlobals(BaseTransformTestCase):
    """Test Transform Globals """
    def setUp(self):
        super(TestServerlessGlobals, self).setUp()
        self.template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Transform": "AWS::Serverless-2016-10-31",
            "Globals": {
                "Function": {
                    "Runtime": "nodejs6.10",
                    "Timeout": 180,
                    "Handler": "index.handler"
                }
            },
            "Resources": {
                "myFunction": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {
                        "CodeUri": "s3://testBucket/mySourceCode.zip"
                    }
                }
            }
        }

    def test_function_autopublish_positive(self):
        """Test converstion of serverless function to include AutoPublish"""

        def test_success(cfn):
            """Test success"""
            if 'Globals' in cfn.sections:
                return True
            return False

        self.helper_transform_cfn(self.template, test_success)
