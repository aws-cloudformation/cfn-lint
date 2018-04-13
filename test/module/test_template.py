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
        filename = 'templates/good/generic.yaml'
        template = self.load_template(filename)
        self.template = Template(template)
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
        resources = self.template.get_resources()
        assert len(resources) == 8

    def test_get_resource_names(self):
        """ Test Resource Names"""
        resource_names = self.template.get_resource_names()
        assert bool(set(resource_names).intersection(self.resource_names))

    def test_get_parameters(self):
        """ Test Get Parameters"""
        parameters = self.template.get_parameters()
        assert len(parameters) == 4

    def test_get_parameter_names(self):
        """Test Get Parameter Names"""
        parameters = self.template.get_parameter_names()
        assert bool(set(parameters).intersection(self.parameter_names))

    def test_get_valid_refs(self):
        """ Get Valid REFs"""
        refs = self.template.get_valid_refs()
        assert len(refs) == 20
