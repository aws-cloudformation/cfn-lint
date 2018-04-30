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
from cfnlint import CloudFormationTransform, transforms


class Api(CloudFormationTransform):
    """Conver Serverless API"""
    type = 'AWS::Serverless-2016-10-31'

    def resource_transform(self, cfn):
        """
            Add resources based on the criteria inside
            https://awslabs.github.io/serverless-application-model/internals/generated_resources.html
        """
        for resource_name, resource_values in cfn.get_resources(resource_type='AWS::Serverless::Api').items():
            resource_properties = resource_values.get('Properties', {})
            stage_name = resource_properties.get('StageName', 'Prod')
            transforms.add_resource(
                cfn, '%s%sStage' % (resource_name, stage_name),
                {
                    'Type': 'AWS::ApiGateway::Stage',
                    'Properties': {
                        'RestApiId': {
                            'Ref': resource_name
                        }
                    }
                }
            )
            transforms.add_resource(
                cfn, '%sDeployment%s' % (resource_name, 'SHA'),
                {
                    'Type': 'AWS::ApiGateway::Deployment',
                    'Properties': {
                        'RestApiId': {
                            'Ref': resource_name
                        }
                    }
                }
            )
