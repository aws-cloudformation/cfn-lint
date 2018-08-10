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
from cfnlint import Template  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


class TestTemplate(BaseTestCase):
    """Test Template Class in cfnlint """
    def setUp(self):
        """ SetUp template object"""
        filename = 'fixtures/templates/good/generic.yaml'
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
