"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class PropertiesTemplated(CloudFormationLintRule):
    """Check Base Resource Configuration"""
    id = 'W3002'
    shortdesc = 'Warn when properties are configured to only work with the package command'
    description = 'Some properties can be configured to only work with the CloudFormation' \
                  'package command. Warn when this is the case so user is aware.'
    source_url = 'https://docs.aws.amazon.com/cli/latest/reference/cloudformation/package.html'
    tags = ['resources']

    def __init__(self):
        """Init"""
        super(PropertiesTemplated, self).__init__()
        self.resource_property_types.extend([
            'AWS::ApiGateway::RestApi',
            'AWS::Lambda::Function',
            'AWS::Lambda::LayerVersion',
            'AWS::ElasticBeanstalk::ApplicationVersion',
            'AWS::StepFunctions::StateMachine',
        ])

    def check_value(self, value, path):
        """ Check the value """
        matches = []
        if isinstance(value, str):
            message = 'This code may only work with `package` cli command as the property (%s) is a string' % (
                '/'.join(map(str, path)))
            matches.append(RuleMatch(path, message))

        return matches

    def match_resource_properties(self, properties, resourcetype, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        templated_exceptions = {
            'AWS::ApiGateway::RestApi': ['BodyS3Location'],
            'AWS::Lambda::Function': ['Code'],
            'AWS::Lambda::LayerVersion': ['Content'],
            'AWS::ElasticBeanstalk::ApplicationVersion': ['SourceBundle'],
            'AWS::StepFunctions::StateMachine': ['DefinitionS3Location'],
        }

        for key in templated_exceptions.get(resourcetype, []):
            matches.extend(
                cfn.check_value(
                    obj=properties, key=key,
                    path=path[:],
                    check_value=self.check_value
                ))

        return matches
