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


class Functions(CloudFormationTransform):
    """Check Base Template Settings"""
    type = 'AWS::Serverless-2016-10-31'

    def resource_transform(self, cfn):
        """
            Add resources based on the criteria inside
            https://awslabs.github.io/serverless-application-model/internals/generated_resources.html
        """
        for resource_name, resource_values in cfn.get_resources(resource_type='AWS::Serverless::Function').items():
            resource_properties = resource_values.get('Properties', {})
            transforms.add_resource(
                cfn, '%sRole' % resource_name,
                {
                    'Type': 'AWS::IAM::Role',
                    'Properties': {
                        'AssumeRolePolicyDocument': {
                            'Version': '2012-10-17',
                            'Statement': [{
                                'Effect': 'Allow',
                                'Principal': {
                                    'Service': ['lambda.amazonaws.com']
                                },
                                'Action': ['sts:AssumeRole']
                            }]
                        }
                    }
                }
            )
            if resource_properties:
                key_value = resource_properties.get('AutoPublishAlias')
                if key_value:
                    # Need to figure out SHA256 hashing
                    transforms.add_resource(
                        cfn, '%sVersion%s' % (resource_name, key_value),
                        {
                            'Type': 'AWS::Lambda::Version',
                            'Properties': {
                                'FunctionName': resource_name
                            }
                        }
                    )
                    transforms.add_resource(
                        cfn, '%sAlias%s' % (resource_name, key_value),
                        {
                            'Type': 'AWS::Lambda::Alias',
                            'Properties': {
                                'FunctionName': resource_name,
                                'FunctionVersion': 'latest',
                                'Name': key_value
                            }
                        }
                    )

                key_value = resource_properties.get('DeploymentPreference', {})
                if key_value:
                    transforms.add_resource(
                        cfn, 'ServerlessDeploymentApplication',
                        {
                            'Type': 'AWS::CodeDeploy::Application',
                            'Properties': {}
                        }
                    )
                    transforms.add_resource(
                        cfn, '%sDeploymentGroup' % resource_name,
                        {
                            'Type': 'AWS::CodeDeploy::DeploymentGroup',
                            'Properties': {
                                'ApplicationName': {
                                    'Ref': resource_name
                                },
                                'ServiceRoleArn': {
                                    'Ref': 'CodeDeployServiceRole'
                                }
                            }
                        }
                    )
                    transforms.add_resource(
                        cfn, 'CodeDeployServiceRole',
                        {
                            'Type': 'AWS::IAM::Role',
                            'Properties': {
                                'AssumeRolePolicyDocument': {
                                    'Version': '2012-10-17',
                                    'Statement': [{
                                        'Effect': 'Allow',
                                        'Principal': {
                                            'Service': ['codedeploy.amazonaws.com']
                                        },
                                        'Action': ['sts:AssumeRole']
                                    }]
                                }
                            }
                        }
                    )

                events = resource_properties.get('Events', {})
                for event_name, event_value in events.items():
                    event_type = event_value.get('Type', None)
                    if event_type == 'Api':
                        rest_api_id = event_value.get('Properties', {}).get('RestApidId')
                        if not rest_api_id:
                            transforms.add_resource(
                                cfn, 'ServerlessRestApi',
                                {
                                    'Type': 'AWS::ApiGateway::RestApi',
                                    'Properties': {}
                                }
                            )
                            transforms.add_resource(
                                cfn, 'ServerlessRestApi%sStage' % 'Prod',
                                {
                                    'Type': 'AWS::ApiGateway::Stage',
                                    'Properties': {
                                        'RestApiId': {
                                            'Ref': 'ServerlessRestApi'
                                        }
                                    }
                                }
                            )
                            transforms.add_resource(
                                cfn, 'ServerlessRestApiDeployment%s' % ('SHA'),
                                {
                                    'Type': 'AWS::ApiGateway::Deployment',
                                    'Properties': {
                                        'RestApiId': {
                                            'Ref': 'ServerlessRestApi'
                                        }
                                    }
                                }
                            )

                        transforms.add_resource(
                            cfn, '%s%sPermission%s' % (resource_name, event_name, 'Prod'),
                            {
                                'Type': 'AWS::Lambda::Permission',
                                'Properties': {
                                    'Principal': 'apigateway.amazonaws.com',
                                    'Action': 'lambda:InvokeFunction',
                                    'FunctionName': {
                                        'Fn::GetAtt': [
                                            resource_name,
                                            'Arn'
                                        ]
                                    }
                                }
                            }
                        )
                    elif event_type == 'S3':
                        transforms.add_resource(
                            cfn, '%s%sPermission' % (resource_name, event_name),
                            {
                                'Type': 'AWS::Lambda::Permission',
                                'Properties': {
                                    'Principal': 's3.amazonaws.com',
                                    'Action': 'lambda:InvokeFunction',
                                    'FunctionName': {
                                        'Fn::GetAtt': [
                                            resource_name,
                                            'Arn'
                                        ]
                                    }
                                }
                            }
                        )
                    elif event_type == 'SNS':
                        transforms.add_resource(
                            cfn, '%s%sPermission' % (resource_name, event_name),
                            {
                                'Type': 'AWS::Lambda::Permission',
                                'Properties': {
                                    'Principal': 'sns.amazonaws.com',
                                    'Action': 'lambda:InvokeFunction',
                                    'FunctionName': {
                                        'Fn::GetAtt': [
                                            resource_name,
                                            'Arn'
                                        ]
                                    }
                                }
                            }
                        )
                        transforms.add_resource(
                            cfn, '%s%s' % (resource_name, event_name),
                            {
                                'Type': 'AWS::SNS::Subscription',
                                'Properties': {}
                            }
                        )
                    elif event_type == 'Kinesis':
                        transforms.add_resource(
                            cfn, '%s%sPermission' % (resource_name, event_name),
                            {
                                'Type': 'AWS::Lambda::Permission',
                                'Properties': {
                                    'Principal': 'kinesis.amazonaws.com',
                                    'Action': 'lambda:InvokeFunction',
                                    'FunctionName': {
                                        'Fn::GetAtt': [
                                            resource_name,
                                            'Arn'
                                        ]
                                    }
                                }
                            }
                        )
                        transforms.add_resource(
                            cfn, '%s%s' % (resource_name, event_name),
                            {
                                'Type': 'AWS::Lambda::EventSourceMapping',
                                'Properties': {
                                    'FunctionName': {
                                        'Ref': resource_name
                                    },
                                    'EventSourceArn': 'anArn',
                                    'StartingPosition': '1'
                                }
                            }
                        )
                    elif event_type == 'DynamoDb':
                        transforms.add_resource(
                            cfn, '%s%sPermission' % (resource_name, event_name),
                            {
                                'Type': 'AWS::Lambda::Permission',
                                'Properties': {
                                    'Principal': 'dynamodb.amazonaws.com',
                                    'Action': 'lambda:InvokeFunction',
                                    'FunctionName': {
                                        'Fn::GetAtt': [
                                            resource_name,
                                            'Arn'
                                        ]
                                    }
                                }
                            }
                        )
                        transforms.add_resource(
                            cfn, '%s%s' % (resource_name, event_name),
                            {
                                'Type': 'AWS::Lambda::EventSourceMapping',
                                'Properties': {
                                    'FunctionName': {
                                        'Ref': resource_name
                                    },
                                    'EventSourceArn': 'anArn',
                                    'StartingPosition': '1'
                                }
                            }
                        )
                    elif event_type == 'Schedule':
                        transforms.add_resource(
                            cfn, '%s%sPermission' % (resource_name, event_name),
                            {
                                'Type': 'AWS::Lambda::Permission',
                                'Properties': {
                                    'Principal': 'events.amazonaws.com',
                                    'Action': 'lambda:InvokeFunction',
                                    'FunctionName': {
                                        'Fn::GetAtt': [
                                            resource_name,
                                            'Arn'
                                        ]
                                    }
                                }
                            }
                        )
                        transforms.add_resource(
                            cfn, '%s%s' % (resource_name, event_name),
                            {
                                'Type': 'AWS::Events::Rule',
                                'Properties': {}
                            }
                        )
                    elif event_type == 'CloudWatchEvent':
                        transforms.add_resource(
                            cfn, '%s%sPermission' % (resource_name, event_name),
                            {
                                'Type': 'AWS::Lambda::Permission',
                                'Properties': {
                                    'Principal': 'events.amazonaws.com',
                                    'Action': 'lambda:InvokeFunction',
                                    'FunctionName': {
                                        'Fn::GetAtt': [
                                            resource_name,
                                            'Arn'
                                        ]
                                    }
                                }
                            }
                        )
                        transforms.add_resource(
                            cfn, '%s%s' % (resource_name, event_name),
                            {
                                'Type': 'AWS::Events::Rule',
                                'Properties': {}
                            }
                        )
