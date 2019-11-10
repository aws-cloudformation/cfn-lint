"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
from cfnlint import conditions


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

    def test_basic_condition_w_int(self):
        """ Test getting a condition setup """
        template = {
            'Conditions': {
                'myCondition1': {
                    'Fn::Equals': [{'Ref': 'myParameter'}, 1]
                },
                'myCondition2': {
                    'Fn::Equals': [1, {'Ref': 'myParameter'}]
                }
            }
        }
        result = conditions.Condition(template, 'myCondition1')
        self.assertFalse(result.test({'410f41081170ebc3bc99d8f424ad8e01633f444a': '2'}))
        self.assertTrue(result.test({'410f41081170ebc3bc99d8f424ad8e01633f444a': '1'}))
        result = conditions.Condition(template, 'myCondition2')
        self.assertFalse(result.test({'410f41081170ebc3bc99d8f424ad8e01633f444a': '2'}))
        self.assertTrue(result.test({'410f41081170ebc3bc99d8f424ad8e01633f444a': '1'}))

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

    def test_direct_condition(self):
        """ Test direction condition"""
        template = {
            'Conditions': {
                'condition1': {
                    'Fn::Equals': [{'Ref': 'AWS::Region'}, 'us-east-1']
                },
                'directcondition': {'Condition': 'condition1'}
            }
        }
        result = conditions.Condition(template, 'directcondition')
        self.assertTrue(
            result.test({'36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-east-1'}))
        self.assertFalse(
            result.test({'36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-west-1'}))

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

    def test_two_function_condition(self):
        """ Test getting a condition setup """
        template = {
            'Conditions': {
                'myCondition': {
                    'Fn::Equals': [{'Ref': 'AWS::Region'}, {'Ref': 'PrimaryRegion'}]
                }
            }
        }
        result = conditions.Condition(template, 'myCondition')
        self.assertFalse(result.test({'36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-east-1'}))
        self.assertTrue(result.test(
            {'36305712594f5e76fbcbbe2f82cd3f850f6018e9': '36cf15035d5be0f36e03d67b66cddb6081f5855d'}))

    def test_empty_string_in_equals(self):
        """ Empty String in Condition """
        template = {
            'Conditions': {
                'isSet': {'Fn::Equals': [{'Ref': 'myEnvironment'}, '']}
            },
            'Resources': {}
        }
        result = conditions.Condition(template, 'isSet')
        self.assertEqual(result.And, [])  # No And
        self.assertEqual(result.Or, [])  # No Or
        self.assertEqual(result.Not, [])  # No Not
        self.assertIsNotNone(result.Equals)
        self.assertEqual(result.Influenced_Equals, {
                         'd60d12101638186a2c742b772ec8e69b3e2382b9': {''}})


class TestBadConditions(BaseTestCase):
    """Test Badly Formmated Condition """

    def test_bad_format_condition(self):
        """ Badly formmated Condition """
        template = {
            'Conditions': {
                'isProduction': [{'Fn::Equals': [{'Ref:' 'myEnvironment'}, 'prod']}]
            },
            'Resources': {}
        }
        result = conditions.Condition(template, 'isProduction')
        self.assertEqual(result.And, [])  # No And
        self.assertEqual(result.Or, [])  # No Or
        self.assertEqual(result.Not, [])  # No Not
        self.assertIsNone(result.Equals)
        self.assertEqual(result.Influenced_Equals, {})

    def test_bad_format_condition_2(self):
        """ Badly formmated Condition """
        template = {
            'Conditions': {
                'isProduction': {'Fn::Equals': [[{'Ref:' 'myEnvironment'}], 'prod']}
            },
            'Resources': {}
        }
        result = conditions.Condition(template, 'isProduction')
        self.assertEqual(result.And, [])  # No And
        self.assertEqual(result.Or, [])  # No Or
        self.assertEqual(result.Not, [])  # No Not
        self.assertIsNone(result.Equals)
        self.assertEqual(result.Influenced_Equals, {})

    def test_bad_format_condition_3(self):
        """ Badly formmated Condition """
        template = {
            'Conditions': {
                'isProduction': {'Fn::Equals': [{'Ref': 'myEnvironment', 'Ref1': 'myEnvironment'}, 'prod']}
            },
            'Resources': {}
        }
        result = conditions.Condition(template, 'isProduction')
        self.assertEqual(result.And, [])  # No And
        self.assertEqual(result.Or, [])  # No Or
        self.assertEqual(result.Not, [])  # No Not
        self.assertIsNone(result.Equals)
        self.assertEqual(result.Influenced_Equals, {})

    def test_bad_format_condition_bad_equals_dict(self):
        """ Badly formmated Condition """
        template = {
            'Conditions': {
                'isProduction': {'Fn::Equals': {'Ref': 'myEnvironment', 'Value': 'prod'}}
            },
            'Resources': {}
        }
        result = conditions.Condition(template, 'isProduction')
        self.assertEqual(result.And, [])  # No And
        self.assertEqual(result.Or, [])  # No Or
        self.assertEqual(result.Not, [])  # No Not
        self.assertIsNone(result.Equals)
        self.assertEqual(result.Influenced_Equals, {})

    def test_bad_format_condition_bad_equals_size(self):
        """ Badly formmated Condition """
        template = {
            'Conditions': {
                'isProduction': {'Fn::Equals': [{'Ref': 'myEnvironment'}, 'Value', 'prod']}
            },
            'Resources': {}
        }
        result = conditions.Condition(template, 'isProduction')
        self.assertEqual(result.And, [])  # No And
        self.assertEqual(result.Or, [])  # No Or
        self.assertEqual(result.Not, [])  # No Not
        self.assertIsNone(result.Equals)
        self.assertEqual(result.Influenced_Equals, {})

    def test_nested_conditions(self):
        """ Test getting a condition setup """
        template = {
            'Conditions': {
                'condition1': {
                    'Fn::Equals': [{'Ref': 'AWS::Region'}, 'us-east-1']
                },
                'condition2': {
                    'Fn::Equals': [{'Ref': 'myEnvironment'}, 'prod']
                },
                'orCondition': {'Fn::Or': [
                    {'Fn::And': [{'Condition': 'condition1'}, {'Condition': 'condition2'}]},
                    {'Fn::Or': [
                        {'Fn::Equals': [{'Ref': 'AWS::Region'}, 'us-west-2']},
                        {'Fn::Equals': [{'Ref': 'AWS::Region'}, 'eu-north-1']},
                    ]}
                ]}
            }
        }
        result = conditions.Condition(template, 'orCondition')
        self.assertEqual(
            result.Influenced_Equals,
            {
                '36305712594f5e76fbcbbe2f82cd3f850f6018e9': {'us-east-1', 'us-west-2', 'eu-north-1'},
                'd60d12101638186a2c742b772ec8e69b3e2382b9': {'prod'}
            }
        )
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
        self.assertTrue(
            result.test({
                '36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-west-2',
                'd60d12101638186a2c742b772ec8e69b3e2382b9': 'dev'}))
