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
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class PropertiesTemplated(CloudFormationLintRule):
    """Check Base Resource Configuration"""
    id = 'W3002'
    shortdesc = 'Warn when properties are configured to only work with the package command'
    description = 'Some properties can be configured to only work with the CloudFormation' \
                  'package command. Warn when this is the case so user is aware.'
    source_url = 'https://docs.aws.amazon.com/cli/latest/reference/cloudformation/package.html'
    tags = ['resources']

    def __init__(self):
        self.resource_property_types.extend([
            'AWS::ApiGateway::RestApi',
            'AWS::Lambda::Function',
            'AWS::ElasticBeanstalk::ApplicationVersion',
        ])

    def check_value(self, value, path):
        """ Check the value """
        matches = []
        if isinstance(value, six.string_types):
            message = 'This code may only work with `package` cli command as the property (%s) is a string' % ('/'.join(map(str, path)))
            matches.append(RuleMatch(path, message))

        return matches

    def match_resource_properties(self, properties, resourcetype, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        templated_exceptions = {
            'AWS::ApiGateway::RestApi': ['BodyS3Location'],
            'AWS::Lambda::Function': ['Code'],
            'AWS::ElasticBeanstalk::ApplicationVersion': ['SourceBundle'],
        }

        for key in templated_exceptions.get(resourcetype, []):
            matches.extend(
                cfn.check_value(
                    obj=properties, key=key,
                    path=path[:],
                    check_value=self.check_value
                ))

        return matches
