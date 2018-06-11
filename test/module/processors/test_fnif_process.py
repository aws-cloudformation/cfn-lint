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
import cfnlint.processors  # pylint: disable=E0401
from cfnlint import Template  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


class TestFnIfProcess(BaseTestCase):
    """Test condition Parsing """
    def setUp(self):
        """ SetUp template object"""
        self.processors = cfnlint.processors.ProcessorsCollection()

    def test_processor(self):
        """Test Successful JSON Parsing"""
        filename = 'test.yaml'
        template = {
            'Resources': {
                'myInstance': {
                    'Properties': {
                        'Fn::If': [
                            'isProduction',
                            {
                                'ImageId': {
                                    'Fn::If': [
                                        'isProductionPrimaryRegion',
                                        'ami-1234567',
                                        'ami-abcdef'
                                    ]
                                }
                            },
                            {
                                'LaunchTemplate': 'template'
                            }
                        ]
                    }
                }
            }
        }
        cfn = Template(filename, template, ['us-east-1'])
        scenario = {
            'isProduction': True, 'isProductionOrPrimaryRegion': True,
            'isNotProduction': False, 'isProductionPrimaryRegion': True
        }

        for processor in self.processors:
            if processor.type == 'FnIf':
                results = processor.process_template(cfn, scenario)


        assert results.template == {
            'Resources': {
                'myInstance': {
                    'Properties': {
                        'ImageId': 'ami-1234567'
                    }
                }
            }
        }

    def test_condition_scenarios_comples(self):
        pass
