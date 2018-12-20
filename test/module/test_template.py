"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
from cfnlint import Template  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


class TestTemplate(BaseTestCase):
    """Test Template Class in cfnlint """
    def setUp(self):
        """ SetUp template object"""
        filename = 'test/fixtures/templates/good/generic.yaml'
        template = self.load_template(filename)
        self.template = Template(filename, template)
        self.resource_names = [
            'IamPipeline',
            'RootInstanceProfile',
            'RolePolicies',
            'MyEC2Instance',
            'RootRole',
            'mySnsTopic',
            'MyEC2Instance1',
            'ElasticLoadBalancer'
        ]
        self.parameter_names = [
            'WebServerPort',
            'Package',
            'Package1',
            'pIops'
        ]

    def test_get_resources_success(self):
        """Test Success on Get Resources"""
        valid_resource_count = 11
        resources = self.template.get_resources()
        assert len(resources) == valid_resource_count, 'Expected {} resources, got {}'.format(valid_resource_count, len(resources))

    def test_get_resources_bad(self):
        """Don't get resources that aren't properly configured"""
        template = {
            'Resources': {
                'Properties': {
                    'BucketName': "bucket_test"
                },
                'Type': "AWS::S3::Bucket"
            }
        }
        self.template = Template('test.yaml', template)
        resources = self.template.get_resources()
        assert resources == {}

    def test_get_resource_names(self):
        """ Test Resource Names"""
        resource_names = self.template.get_resource_names()
        assert bool(set(resource_names).intersection(self.resource_names))

    def test_get_parameters(self):
        """ Test Get Parameters"""
        valid_parameter_count = 7
        parameters = self.template.get_parameters()
        assert len(parameters) == valid_parameter_count, 'Expected {} parameters, got {}'.format(valid_parameter_count, len(parameters))

    def test_get_parameter_names(self):
        """Test Get Parameter Names"""
        parameters = self.template.get_parameter_names()
        assert bool(set(parameters).intersection(self.parameter_names))

    def test_get_valid_refs(self):
        """ Get Valid REFs"""
        valid_ref_count = 26
        refs = self.template.get_valid_refs()
        assert len(refs) == valid_ref_count, 'Expected {} refs, got {}'.format(valid_ref_count, len(refs))

    def test_conditions_return_object_success(self):
        """Test condition object response and nested IFs"""
        template = [
            'isProd',
            {
                'Key': 'Environment1',
                'Value': 'Prod'
            },
            {
                'Fn::If': [
                    'isDev',
                    {
                        'Key': 'Environment2',
                        'Value': 'Dev'
                    },
                    {
                        "Ref": "AWS::NoValue"
                    }
                ]
            }
        ]

        results = self.template.get_condition_values(template, [])
        self.assertEqual(results, [
            {'Path': [1], 'Value': {'Value': 'Prod', 'Key': 'Environment1'}},
            {'Path': [2, 'Fn::If', 1], 'Value': {'Value': 'Dev', 'Key': 'Environment2'}}
        ])

    def test_conditions_return_list_success(self):
        """Test condition list response"""
        template = [
            'PrimaryRegion',
            [
                'EN'
            ],
            [
                'BE',
                'LU',
                'NL'
            ]
        ]

        results = self.template.get_condition_values(template, [])
        self.assertEqual(results, [
            {'Value': ['EN'], 'Path': [1]}, {'Value': ['BE', 'LU', 'NL'], 'Path': [2]}
        ])

    def test_conditions_return_string_success(self):
        """Test condition object response and nested IFs"""
        template = [
            'isProd',
            {
                'Ref': 'Sample'
            },
            'String'
        ]

        results = self.template.get_condition_values(template, [])
        self.assertEqual(results, [
            {'Path': [1], 'Value': {'Ref': 'Sample'}}, {'Path': [2], 'Value': 'String'}
        ])

    def test_is_resource_available(self):
        """ Test is resource available """
        filename = 'test/fixtures/templates/good/core/conditions.yaml'
        template = self.load_template(filename)
        template = Template(filename, template)
        self.assertEqual(
            template.is_resource_available(
                ['Resources', 'AMIIDLookup', 'Properties', 'Role', 'Fn::If', 1, 'Fn::GetAtt', ['LambdaExecutionRole', 'Arn']],
                'LambdaExecutionRole'
            ),
            []
        )
        self.assertEqual(
            template.is_resource_available(
                ['Outputs', 'lambdaArn', 'Value', 'Fn::GetAtt', ['LambdaExecutionRole', 'Arn']],
                'LambdaExecutionRole'
            ),
            []
        )

    def test_is_resource_not_available(self):
        """ Test is resource available """
        filename = 'test/fixtures/templates/bad/functions/relationship_conditions.yaml'
        template = self.load_template(filename)
        template = Template(filename, template)
        self.assertEqual(
            template.is_resource_available(
                ['Resources', 'AMIIDLookup', 'Properties', 'Role', 'Fn::If', 1, 'Fn::GetAtt', ['LambdaExecutionRole', 'Arn']],
                'LambdaExecutionRole'
            ),
            [{'isPrimary': False}]
        )
        self.assertEqual(
            template.is_resource_available(
                ['Outputs', 'lambdaArn', 'Value', 'Fn::GetAtt', ['LambdaExecutionRole', 'Arn']],
                'LambdaExecutionRole'
            ),
            [{'isPrimary': False}]
        )

    def test_get_conditions_from_path(self):
        """ Test is resource available """
        filename = 'test/fixtures/templates/good/core/conditions.yaml'
        template = self.load_template(filename)
        template = Template(filename, template)
        # Gets the condition when in the middle of the Path
        self.assertEqual(
            template.get_conditions_from_path(
                template.template,
                ['Resources', 'AMIIDLookup', 'Properties', 'Role', 'Fn::If', 1, 'Fn::GetAtt', ['LambdaExecutionRole', 'Arn']]
            ),
            {'isPrimary': {True}}
        )
        self.assertEqual(
            template.get_conditions_from_path(
                template.template,
                ['Outputs', 'lambdaArn', 'Value', 'Fn::GetAtt', ['LambdaExecutionRole', 'Arn']]
            ),
            {'isPrimary': {True}}
        )
        self.assertEqual(
            template.get_conditions_from_path(
                template.template,
                ['Resources', 'InstanceProfile', 'Properties', 'Roles', 0, 'Ref', 'LambdaExecutionRole']
            ),
            {'isPrimaryAndProduction': {True}}
        )

    def test_failure_get_conditions_from_path(self):
        """ Test get conditions from path when things arne't formatted correctly """
        filename = 'test/fixtures/templates/bad/core/conditions.yaml'
        template = self.load_template(filename)
        template = Template(filename, template)
        # Gets no condition names when it isn't a valid list
        self.assertEqual(
            template.get_conditions_from_path(
                template.template,
                ['Resources', 'AMIIDLookup', 'Properties', 'Role', 'Fn::If', 1, 'Fn::GetAtt', ['LambdaExecutionRole', 'Arn']]
            ),
            {}
        )
        # Gets no condition names when it isn't really a list
        self.assertEqual(
            template.get_conditions_from_path(
                template.template,
                ['Resources', 'myInstance4', 'Properties', 'InstanceType', 'Fn::If', 'Fn::If', 0]
            ),
            {}
        )

    def test_get_conditions_scenarios_from_object(self):
        """ Test Getting condition names in an object/list """
        filename = 'test/fixtures/templates/good/core/conditions.yaml'
        template = self.load_template(filename)
        template = Template(filename, template)
        # includes nested IFs
        self.assertEqualListOfDicts(
            template.get_conditions_scenarios_from_object(
                template.template.get('Resources', {}).get('myInstance4', {}).get('Properties', {})
            ),
            [
                {'isPrimary': True, 'isProduction': True, 'isPrimaryAndProduction': True},
                {'isPrimary': True, 'isProduction': False, 'isPrimaryAndProduction': False},
                {'isPrimary': False, 'isProduction': True, 'isPrimaryAndProduction': False},
                {'isPrimary': False, 'isProduction': False, 'isPrimaryAndProduction': False}
            ]
        )
        self.assertEqualListOfDicts(
            template.get_conditions_scenarios_from_object(
                template.template.get('Resources', {}).get('myInstance3', {}).get('Properties', {})
            ),
            [
                {'isPrimaryAndProduction': True, 'isDevelopment': False},
                {'isPrimaryAndProduction': False, 'isDevelopment': True},
                {'isPrimaryAndProduction': False, 'isDevelopment': False},
            ]
        )
