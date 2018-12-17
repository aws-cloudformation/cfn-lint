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
from cfnlint import conditions, Runner
from testlib.testcase import BaseTestCase


class TestConditions(BaseTestCase):
    """Test Conditions Logic """
    def setUp(self):
        """ setup the cfn object """
        filename = 'test/fixtures/templates/good/core/conditions.yaml'
        template = self.load_template(filename)
        self.runner = Runner([], filename, template, ['us-east-1'], [])
        self.conditions = self.runner.cfn.conditions

    def assertEqualUnordered(self, l1, l2):
        """ Assert equal unordered lists of dicts """
        self.assertEqual(len(l1), len(l2))
        s_l1 = sorted(sorted(d.items()) for d in l1)
        s_l2 = sorted(sorted(d.items()) for d in l2)
        self.assertListEqual(s_l1, s_l2)

    def test_success_size_of_conditions(self):
        """Test success run"""
        self.assertEqual(len(self.conditions.Conditions), 7)

    def test_success_is_production(self):
        """ test isProduction """
        condition = self.conditions.Conditions.get('isProduction')
        self.assertEqual(condition.And, [])
        self.assertEqual(condition.Or, [])
        self.assertEqual(condition.Not, [])
        self.assertEqual(condition.Equals.Left.Function, 'd60d12101638186a2c742b772ec8e69b3e2382b9')
        self.assertIsNone(condition.Equals.Left.String)
        self.assertEqual(condition.Equals.Right.String, 'Prod')
        self.assertIsNone(condition.Equals.Right.Function)
        self.assertEqual(
            condition.Influenced_Equals,
            {
                'd60d12101638186a2c742b772ec8e69b3e2382b9': {'Prod'}
            }
        )

    def test_success_is_primary(self):
        """ test isProduction """
        condition = self.conditions.Conditions.get('isPrimary')
        self.assertEqual(condition.And, [])
        self.assertEqual(condition.Or, [])
        self.assertEqual(condition.Not, [])
        self.assertEqual(condition.Equals.Right.Function, '5b97e105d6d4fb8cf628bc6affb4e955cfee6d12')
        self.assertIsNone(condition.Equals.Right.String)
        self.assertEqual(condition.Equals.Left.String, 'True')
        self.assertIsNone(condition.Equals.Left.Function)
        self.assertEqual(
            condition.Influenced_Equals,
            {
                '5b97e105d6d4fb8cf628bc6affb4e955cfee6d12': {'True'}
            }
        )

    def test_success_is_primary_and_prod(self):
        """ test isPrimaryAndProduction """
        condition = self.conditions.Conditions.get('isPrimaryAndProduction')
        self.assertEqual(len(condition.And), 2)
        self.assertIsNone(condition.Equals)
        self.assertEqual(condition.Or, [])
        self.assertEqual(condition.Not, [])
        self.assertEqual(condition.And[0].Equals.Left.Function, 'd60d12101638186a2c742b772ec8e69b3e2382b9')
        self.assertIsNone(condition.And[0].Equals.Left.String)
        self.assertEqual(condition.And[0].Equals.Right.String, 'Prod')
        self.assertIsNone(condition.And[0].Equals.Right.Function)
        self.assertEqual(condition.And[1].Equals.Right.Function, '5b97e105d6d4fb8cf628bc6affb4e955cfee6d12')
        self.assertIsNone(condition.And[1].Equals.Right.String)
        self.assertEqual(condition.And[1].Equals.Left.String, 'True')
        self.assertIsNone(condition.And[1].Equals.Left.Function)
        self.assertEqual(
            condition.Influenced_Equals,
            {
                'd60d12101638186a2c742b772ec8e69b3e2382b9': {'Prod'},
                '5b97e105d6d4fb8cf628bc6affb4e955cfee6d12': {'True'}
            }
        )

    def test_success_is_production_or_stage(self):
        """ test isProductionOrStaging """
        condition = self.conditions.Conditions.get('isProductionOrStaging')
        self.assertEqual(len(condition.Or), 2)
        self.assertIsNone(condition.Equals)
        self.assertEqual(condition.And, [])
        self.assertEqual(condition.Not, [])
        self.assertEqual(condition.Or[0].Equals.Left.Function, 'd60d12101638186a2c742b772ec8e69b3e2382b9')
        self.assertIsNone(condition.Or[0].Equals.Left.String)
        self.assertEqual(condition.Or[0].Equals.Right.String, 'Prod')
        self.assertIsNone(condition.Or[0].Equals.Right.Function)
        self.assertEqual(condition.Or[1].Left.Function, 'd60d12101638186a2c742b772ec8e69b3e2382b9')
        self.assertIsNone(condition.Or[1].Left.String)
        self.assertEqual(condition.Or[1].Right.String, 'Stage')
        self.assertIsNone(condition.Or[1].Right.Function)
        self.assertEqual(
            condition.Influenced_Equals,
            {
                'd60d12101638186a2c742b772ec8e69b3e2382b9': {'Prod', 'Stage'}
            }
        )

    def test_success_is_not_production(self):
        """ test isNotProduction """
        condition = self.conditions.Conditions.get('isNotProduction')
        self.assertEqual(condition.And, [])
        self.assertEqual(condition.Or, [])
        self.assertEqual(len(condition.Not), 1)
        self.assertEqual(condition.Not[0].Equals.Left.Function, 'd60d12101638186a2c742b772ec8e69b3e2382b9')
        self.assertIsNone(condition.Not[0].Equals.Left.String)
        self.assertEqual(condition.Not[0].Equals.Right.String, 'Prod')
        self.assertIsNone(condition.Not[0].Equals.Right.Function)
        self.assertEqual(
            condition.Influenced_Equals,
            {
                'd60d12101638186a2c742b772ec8e69b3e2382b9': {'Prod'}
            }
        )

    def test_success_is_development(self):
        """ test isDevelopment """
        condition = self.conditions.Conditions.get('isDevelopment')
        self.assertEqual(condition.And, [])
        self.assertEqual(condition.Or, [])
        self.assertEqual(condition.Not, [])
        self.assertEqual(condition.Equals.Left.Function, 'd60d12101638186a2c742b772ec8e69b3e2382b9')
        self.assertIsNone(condition.Equals.Left.String)
        self.assertEqual(condition.Equals.Right.String, 'Dev')
        self.assertIsNone(condition.Equals.Right.Function)
        self.assertEqual(
            condition.Influenced_Equals,
            {
                'd60d12101638186a2c742b772ec8e69b3e2382b9': {'Dev'}
            }
        )

    def test_condition_relationship(self):
        """ Test condition relationships """
        self.assertEqualUnordered(
            self.conditions.get_scenarios(['isProduction', 'isPrimaryAndProduction']),
            [
                {'isProduction': True, 'isPrimaryAndProduction': True},
                {'isProduction': True, 'isPrimaryAndProduction': False},
                {'isProduction': False, 'isPrimaryAndProduction': False}
            ]
        )
        self.assertEqualUnordered(
            self.conditions.get_scenarios(['isProduction', 'isDevelopment']),
            [
                {'isProduction': True, 'isDevelopment': False},
                {'isProduction': False, 'isDevelopment': True},
                {'isProduction': False, 'isDevelopment': False}
            ]
        )
        self.assertEqualUnordered(
            self.conditions.get_scenarios(['isProduction', 'isNotProduction']),
            [
                {'isProduction': True, 'isNotProduction': False},
                {'isProduction': False, 'isNotProduction': True}
            ]
        )
        self.assertEqualUnordered(
            self.conditions.get_scenarios(['isProduction', 'isProductionOrStaging']),
            [
                {'isProduction': True, 'isProductionOrStaging': True},
                {'isProduction': False, 'isProductionOrStaging': True},
                {'isProduction': False, 'isProductionOrStaging': False},
            ]
        )

        self.assertEqualUnordered(
            self.conditions.get_scenarios(['isProduction', 'isPrimaryAndProdOrStage']),
            [
                {'isProduction': True, 'isPrimaryAndProdOrStage': True},
                {'isProduction': True, 'isPrimaryAndProdOrStage': False},
                {'isProduction': False, 'isPrimaryAndProdOrStage': True},
                {'isProduction': False, 'isPrimaryAndProdOrStage': False},
            ]
        )


class TestBadConditions(BaseTestCase):
    """Test Badly Formmated Conditions """
    def test_no_failure_on_list(self):
        """ setup the cfn object """
        filename = 'test/fixtures/templates/bad/core/conditions_list.yaml'
        template = self.load_template(filename)
        runner = Runner([], filename, template, ['us-east-1'], [])
        self.assertEqual(runner.cfn.conditions.Conditions, {})

    def test_no_failure_on_missing(self):
        """ setup the cfn object """
        filename = 'test/fixtures/templates/bad/core/conditions_list.yaml'
        template = self.load_template(filename)
        runner = Runner([], filename, template, ['us-east-1'], [])
        self.assertEqual(runner.cfn.conditions.Conditions, {})

        scenarios = runner.cfn.conditions.get_scenarios(['isProduction'])
        self.assertEqual(scenarios, [])
