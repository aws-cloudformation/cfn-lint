"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
from cfnlint import Runner


class TestConditions(BaseTestCase):
    """Test Conditions Logic """

    def setUp(self):
        """ setup the cfn object """
        filename = 'test/fixtures/templates/good/core/conditions.yaml'
        template = {
            'Parameters': {
                'NatType': {
                    'Type': 'String',
                    'AllowedValues': ['None', 'Single NAT', 'High Availability']
                },
                'myEnvironment': {
                    'Type': 'String',
                    'AllowedValues': ['Dev', 'Stage', 'Prod']
                }
            },
            'Conditions': {
                'isProduction': {'Fn::Equals': [{'Ref': 'myEnvironment'}, 'Prod']},
                'isPrimary': {'Fn::Equals': ['True', {'Fn::FindInMap': ['location', {'Ref': 'AWS::Region'}, 'primary']}]},
                'isPrimaryAndProduction': {'Fn::And': [{'Condition': 'isProduction'}, {'Condition': 'isPrimary'}]},
                'isProductionOrStaging': {'Fn::Or': [{'Condition': 'isProduction'}, {'Fn::Equals': [{'Ref': 'myEnvironment'}, 'Stage']}]},
                'isNotProduction': {'Fn::Not': [{'Condition': 'isProduction'}]},
                'isDevelopment': {'Fn::Equals': ['Dev', {'Ref': 'myEnvironment'}]},
                'isPrimaryAndProdOrStage': {'Fn::And': [{'Condition': 'isProductionOrStaging'}, {'Fn::Equals': ['True', {'Fn::FindInMap': ['location', {'Ref': 'AWS::Region'}, 'primary']}]}]},
                'DeployNatGateway': {'Fn::Not': [{'Fn::Equals': [{'Ref': 'NatType'}, 'None']}]},
                'Az1Nat': {
                    'Fn::Or': [
                        {'Fn::Equals': [{'Ref': 'NatType'}, 'Single NAT']},
                        {'Fn::Equals': [{'Ref': 'NatType'}, 'High Availability']}
                    ]
                }
            },
            'Resources': {}
        }
        self.runner = Runner([], filename, template, ['us-east-1'], [])
        self.conditions = self.runner.cfn.conditions

    def test_success_size_of_conditions(self):
        """Test success run"""
        self.assertEqual(len(self.conditions.Conditions), 9)
        self.assertEqual(len(self.conditions.Parameters), 2)
        self.assertListEqual(self.conditions.Parameters['55caa18684cddafa866bdb947fb31ea563b2ea73'], [
                             'None', 'Single NAT', 'High Availability'])

    def test_success_is_production(self):
        """ test isProduction """
        condition = self.conditions.Conditions.get('isProduction')
        self.assertEqual(condition.And, [])  # Doesn't use AND
        self.assertEqual(condition.Or, [])  # Doesn't use Or
        self.assertEqual(condition.Not, [])  # Doesn't use Not
        # Hash representation of this object in sorted JSON
        self.assertEqual(condition.Equals.Left.Function, 'd60d12101638186a2c742b772ec8e69b3e2382b9')
        self.assertIsNone(condition.Equals.Left.String)  # Left operator in Equals is Not a String
        self.assertEqual(condition.Equals.Right.String, 'Prod')  # Right operator in Equals is Prod
        # Right operator in Equals is NOT a function
        self.assertIsNone(condition.Equals.Right.Function)
        # Influenced Equals has the Equals hash sorted and the String operator for comparison
        self.assertEqual(
            condition.Influenced_Equals,
            {
                'd60d12101638186a2c742b772ec8e69b3e2382b9': {'Prod'}
            }
        )

    def test_success_is_primary(self):
        """ test isProduction """
        condition = self.conditions.Conditions.get('isPrimary')
        self.assertEqual(condition.And, [])  # Doesn't use AND
        self.assertEqual(condition.Or, [])  # Doesn't use Or
        self.assertEqual(condition.Not, [])  # Doesn't use Not
        # Hash representation of the FindInMap in sorted JSON
        self.assertEqual(condition.Equals.Right.Function,
                         '5b97e105d6d4fb8cf628bc6affb4e955cfee6d12')
        self.assertIsNone(condition.Equals.Right.String)  # Right has no String
        self.assertEqual(condition.Equals.Left.String, 'True')  # Left has True string
        self.assertIsNone(condition.Equals.Left.Function)  # Left has no Function
        # Influenced Equals summizes the FindInMap and the string it could equal
        self.assertEqual(
            condition.Influenced_Equals,
            {
                '5b97e105d6d4fb8cf628bc6affb4e955cfee6d12': {'True'}
            }
        )

    def test_success_is_primary_and_prod(self):
        """ test isPrimaryAndProduction """
        condition = self.conditions.Conditions.get('isPrimaryAndProduction')
        self.assertEqual(len(condition.And), 2)  # AND has two elements
        self.assertIsNone(condition.Equals)  # Equals is None
        self.assertEqual(condition.Or, [])  # Or is empty
        self.assertEqual(condition.Not, [])  # not is Empty

        # For Condition 1
        # Left function sub condition representation of Equals.  Specifically {'Ref': 'myEnvironment'}
        self.assertEqual(condition.And[0].Equals.Left.Function,
                         'd60d12101638186a2c742b772ec8e69b3e2382b9')
        # No String on the Left of the sub condition
        self.assertIsNone(condition.And[0].Equals.Left.String)
        # Prod string on the Right of sub condition
        self.assertEqual(condition.And[0].Equals.Right.String, 'Prod')
        # No Function on the right of the sub condition
        self.assertIsNone(condition.And[0].Equals.Right.Function)

        # For condition 2 - Evaluation of SubCondition is isPrimary
        # Hash representation of the FindInMap in sorted JSON
        self.assertEqual(condition.And[1].Equals.Right.Function,
                         '5b97e105d6d4fb8cf628bc6affb4e955cfee6d12')
        self.assertIsNone(condition.And[1].Equals.Right.String)  # No string on Right side
        self.assertEqual(condition.And[1].Equals.Left.String, 'True')  # String on Left
        self.assertIsNone(condition.And[1].Equals.Left.Function)  # No Function on the Left

        # Influenced Equals now has two for each sub condition.
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
        self.assertEqual(len(condition.Or), 2)  # Or has two elements
        self.assertIsNone(condition.Equals)  # Equals is None
        self.assertEqual(condition.And, [])  # And is empty
        self.assertEqual(condition.Not, [])  # Not is Empty

        # First condition in Or
        # Has representation of {'Ref': 'myEnvironment'}
        self.assertEqual(condition.Or[0].Equals.Left.Function,
                         'd60d12101638186a2c742b772ec8e69b3e2382b9')
        self.assertIsNone(condition.Or[0].Equals.Left.String)  # No string on the Left
        self.assertEqual(condition.Or[0].Equals.Right.String, 'Prod')  # String on the right
        self.assertIsNone(condition.Or[0].Equals.Right.Function)  # No Function on the Right

        # second condition in Or
        # Has representation of {'Ref': 'myEnvironment'}
        self.assertEqual(condition.Or[1].Left.Function, 'd60d12101638186a2c742b772ec8e69b3e2382b9')
        self.assertIsNone(condition.Or[1].Left.String)  # No String on the Left
        self.assertEqual(condition.Or[1].Right.String, 'Stage')  # String on the Right
        self.assertIsNone(condition.Or[1].Right.Function)  # no Function on the right

        # Influenced Equals has one hash with multiple values
        self.assertEqual(
            condition.Influenced_Equals,
            {
                'd60d12101638186a2c742b772ec8e69b3e2382b9': {'Prod', 'Stage'}
            }
        )

    def test_success_is_not_production(self):
        """ test isNotProduction """
        condition = self.conditions.Conditions.get('isNotProduction')
        self.assertEqual(condition.And, [])  # No And
        self.assertEqual(condition.Or, [])  # No Or
        self.assertEqual(len(condition.Not), 1)   # Not has a length of 1

        # Not only has 1
        # Hash representation of {'Ref': 'myEnvironment'}
        self.assertEqual(condition.Not[0].Equals.Left.Function,
                         'd60d12101638186a2c742b772ec8e69b3e2382b9')
        self.assertIsNone(condition.Not[0].Equals.Left.String)  # no String on Left
        self.assertEqual(condition.Not[0].Equals.Right.String, 'Prod')  # String on Right
        self.assertIsNone(condition.Not[0].Equals.Right.Function)  # No function on right
        # Influnced equals has the hash and value
        self.assertEqual(
            condition.Influenced_Equals,
            {
                'd60d12101638186a2c742b772ec8e69b3e2382b9': {'Prod'}
            }
        )

    def test_success_is_development(self):
        """ test isDevelopment """
        condition = self.conditions.Conditions.get('isDevelopment')
        self.assertEqual(condition.And, [])  # No And
        self.assertEqual(condition.Or, [])  # No Or
        self.assertEqual(condition.Not, [])  # No Not
        # Has representation of {'Ref': 'myEnvironment'}
        self.assertEqual(condition.Equals.Right.Function,
                         'd60d12101638186a2c742b772ec8e69b3e2382b9')
        self.assertIsNone(condition.Equals.Right.String)  # no String on Right
        self.assertEqual(condition.Equals.Left.String, 'Dev')  # String on Left
        self.assertIsNone(condition.Equals.Left.Function)  # no Function on Left
        # Influenced equals still looks the same even though its on the other side
        self.assertEqual(
            condition.Influenced_Equals,
            {
                'd60d12101638186a2c742b772ec8e69b3e2382b9': {'Dev'}
            }
        )

    def test_condition_relationship(self):
        """ Test condition relationships """
        # test the relationship of isProduction and isPrimaryAndProduction
        # isPrimaryAndProduction can only be True when isProduction is True
        self.assertEqualListOfDicts(
            self.conditions.get_scenarios(['isProduction', 'isPrimaryAndProduction']),
            [
                {'isProduction': True, 'isPrimaryAndProduction': True},
                {'isProduction': True, 'isPrimaryAndProduction': False},
                {'isProduction': False, 'isPrimaryAndProduction': False}
            ]
        )
        # Test isProduction and isDevelopment relationships
        # both can't be true at the same time and both could be false if the environment is Staging
        self.assertEqualListOfDicts(
            self.conditions.get_scenarios(['isProduction', 'isDevelopment']),
            [
                {'isProduction': True, 'isDevelopment': False},
                {'isProduction': False, 'isDevelopment': True},
                {'isProduction': False, 'isDevelopment': False}
            ]
        )
        # Test the relationship of isProduction and isNotProduction
        # Vice-versa one has to be False when the other is True
        self.assertEqualListOfDicts(
            self.conditions.get_scenarios(['isProduction', 'isNotProduction']),
            [
                {'isProduction': True, 'isNotProduction': False},
                {'isProduction': False, 'isNotProduction': True}
            ]
        )
        # Test the relationship of isProduction and is isProductionOrStaging
        # isProductionOrStaging is True when isProduction is True but can
        # also be true if the environment was Staging
        self.assertEqualListOfDicts(
            self.conditions.get_scenarios(['isProduction', 'isProductionOrStaging']),
            [
                {'isProduction': True, 'isProductionOrStaging': True},
                {'isProduction': False, 'isProductionOrStaging': True},
                {'isProduction': False, 'isProductionOrStaging': False},
            ]
        )
        # We cover all the possible scenarios in this case
        self.assertEqualListOfDicts(
            self.conditions.get_scenarios(['isProduction', 'isPrimaryAndProdOrStage']),
            [
                {'isProduction': True, 'isPrimaryAndProdOrStage': True},
                {'isProduction': True, 'isPrimaryAndProdOrStage': False},
                {'isProduction': False, 'isPrimaryAndProdOrStage': True},
                {'isProduction': False, 'isPrimaryAndProdOrStage': False},
            ]
        )
        # Two unrelated conditions return all the options
        self.assertEqualListOfDicts(
            self.conditions.get_scenarios(['isProduction', 'isPrimary']),
            [
                {'isProduction': True, 'isPrimary': True},
                {'isProduction': True, 'isPrimary': False},
                {'isProduction': False, 'isPrimary': True},
                {'isProduction': False, 'isPrimary': False},
            ]
        )
        # Multiple conditions with parameters specified
        self.assertEqualListOfDicts(
            self.conditions.get_scenarios(['DeployNatGateway', 'Az1Nat']),
            [
                {'DeployNatGateway': True, 'Az1Nat': True},
                {'DeployNatGateway': False, 'Az1Nat': False}
            ]
        )


class TestBadConditions(BaseTestCase):
    """Test Badly Formmated Conditions """

    def test_no_failure_on_list(self):
        """ setup the cfn object """
        template = {
            'Conditions': [
                {'isProduction': {'Fn::Equals': [{'Ref:' 'myEnvironment'}, 'prod']}}
            ],
            'Resources': {}
        }
        runner = Runner([], 'test.yaml', template, ['us-east-1'], [])
        self.assertEqual(runner.cfn.conditions.Conditions, {})

    def test_no_failure_on_missing(self):
        """ setup the cfn object """
        template = {
            'Conditions': {
                'isProduction': {'Fn::Equals': [{'Ref:' 'myEnvironment'}, 'prod']}
            },
            'Resources': {}
        }
        runner = Runner([], 'test.yaml', template, ['us-east-1'], [])

        scenarios = runner.cfn.conditions.get_scenarios(['isNotProduction'])
        self.assertEqual(scenarios, [])

        # Empty results if any item in the list doesn't exist
        scenarios = runner.cfn.conditions.get_scenarios(['isProduction', 'isNotProduction'])
        self.assertEqual(scenarios, [])

    def test_bad_condition_formating(self):
        """ setup the cfn object """
        template = {
            'Conditions': {
                'isNotProduction': {'Fn::Not': [{'Fn::Equals': [{'Ref:' 'myEnvironment'}, 'prod']}]},
                'isProduction': [{'Fn::Equals': [{'Ref:' 'myEnvironment'}, 'prod']}]
            },
            'Resources': {}
        }
        runner = Runner([], 'test.yaml', template, ['us-east-1'], [])

        scenarios = runner.cfn.conditions.get_scenarios(['isProduction'])
        self.assertEqual(scenarios, [{'isProduction': True}, {'isProduction': False}])
