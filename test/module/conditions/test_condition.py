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
from cfnlint import conditions
from testlib.testcase import BaseTestCase


class TestCondition(BaseTestCase):
    """ Test Good Condition """
    def test_basic_condition(self):
        """ Test getting a condition setup """
        template = {
            'Conditions': {
                'myCondition': {
                    'Fn::Equals': [{'Ref': 'AWS::Region'}, 'us-east-1']
                }
            }
        }
        result = conditions.Condition(template, 'myCondition')
        self.assertTrue(result.test({'36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-east-1'}))
        self.assertFalse(result.test({'36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-west-1'}))

    def test_not_condition(self):
        """ Test getting a condition setup """
        template = {
            'Conditions': {
                'myCondition': {
                    'Fn::Equals': [{'Ref': 'AWS::Region'}, 'us-east-1']
                },
                'notCondition': {'Fn::Not': [{'Condition': 'myCondition'}]}
            }
        }
        result = conditions.Condition(template, 'notCondition')
        self.assertFalse(result.test({'36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-east-1'}))
        self.assertTrue(result.test({'36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-west-1'}))

    def test_or_condition(self):
        """ Test getting a condition setup """
        template = {
            'Conditions': {
                'condition1': {
                    'Fn::Equals': [{'Ref': 'AWS::Region'}, 'us-east-1']
                },
                'condition2': {
                    'Fn::Equals': [{'Ref': 'AWS::Region'}, 'us-west-1']
                },
                'orCondition': {'Fn::Or': [{'Condition': 'condition1'}, {'Condition': 'condition2'}]}
            }
        }
        result = conditions.Condition(template, 'orCondition')
        self.assertTrue(result.test({'36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-east-1'}))
        self.assertTrue(result.test({'36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-west-1'}))
        self.assertFalse(result.test({'36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-west-2'}))

    def test_and_condition(self):
        """ Test getting a condition setup """
        template = {
            'Conditions': {
                'condition1': {
                    'Fn::Equals': [{'Ref': 'AWS::Region'}, 'us-east-1']
                },
                'condition2': {
                    'Fn::Equals': [{'Ref': 'myEnvironment'}, 'prod']
                },
                'andCondition': {'Fn::And': [{'Condition': 'condition1'}, {'Condition': 'condition2'}]}
            }
        }
        result = conditions.Condition(template, 'andCondition')
        self.assertTrue(
            result.test({
                '36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-east-1',
                'd60d12101638186a2c742b772ec8e69b3e2382b9': 'prod'}))
        self.assertFalse(
            result.test({
                '36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-east-1',
                'd60d12101638186a2c742b772ec8e69b3e2382b9': 'dev'}))
        self.assertFalse(
            result.test({
                '36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-west-1',
                'd60d12101638186a2c742b772ec8e69b3e2382b9': 'prod'}))
