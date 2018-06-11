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


class TestFnIfScenario(BaseTestCase):
    """Test condition Parsing """
    def setUp(self):
        """ SetUp template object"""
        self.processors = cfnlint.processors.ProcessorsCollection()

    def test_condition_scenarios_simple(self):
        """Test Successful JSON Parsing"""
        filename = 'test.yaml'
        template = {
            'Conditions': {
                'isProduction': {
                    'Fn::Equals': [
                        {'Ref': 'myEnvironment'},
                        'Production'
                    ]
                },
                'isNotProduction': {
                    'Fn::Not': [
                        {'Condition': 'isProduction'}
                    ]
                },
                'isProductionPrimaryRegion': {
                    'Fn::And': [
                        {'Condition': 'isProduction'},
                        {'Fn::Equals': [{'Ref': 'AWS::Region'}, 'us-east-1']}
                    ]
                },
                'isProductionOrPrimaryRegion': {
                    'Fn::Or': [
                        {'Condition': 'isProduction'},
                        {'Fn::Equals': [{'Ref': 'AWS::Region'}, 'us-east-1']}
                    ]
                }
            }
        }
        cfn = Template(filename, template, ['us-east-1'])
        for processor in self.processors:
            if processor.type == 'FnIf':
                matches = processor.get_condition_scenarios(cfn)

        correct = [
            {'isNotProduction': False, 'isProductionPrimaryRegion': True, 'isProduction': True, 'isProductionOrPrimaryRegion': True},
            {'isNotProduction': True, 'isProductionPrimaryRegion': False, 'isProduction': False, 'isProductionOrPrimaryRegion': True},
            {'isNotProduction': False, 'isProductionPrimaryRegion': False, 'isProduction': True, 'isProductionOrPrimaryRegion': True},
            {'isNotProduction': True, 'isProductionPrimaryRegion': False, 'isProduction': False, 'isProductionOrPrimaryRegion': False}
        ]

        assert len(matches) == len(correct)
        for c in correct:
            matched = False
            for match in matches:
                if c == match:
                    matched = True
            assert matched is True, 'Expected {} in matches'.format(c)

    def test_condition_scenarios_comples(self):
        pass
