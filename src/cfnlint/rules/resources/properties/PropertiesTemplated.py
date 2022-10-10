"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class PropertiesTemplated(CloudFormationLintRule):
    """Check Base Resource Configuration"""

    id = 'W3002'
    shortdesc = (
        'Warn when properties are configured to only work with the package command'
    )
    description = (
        'Some properties can be configured to only work with the CloudFormation'
        'package command. Warn when this is the case so user is aware.'
    )
    source_url = (
        'https://docs.aws.amazon.com/cli/latest/reference/cloudformation/package.html'
    )
    tags = ['resources']

    templated_exceptions = {
        'AWS::ApiGateway::RestApi': ['BodyS3Location'],
        'AWS::Lambda::Function': ['Code'],
        'AWS::Lambda::LayerVersion': ['Content'],
        'AWS::ElasticBeanstalk::ApplicationVersion': ['SourceBundle'],
        'AWS::StepFunctions::StateMachine': ['DefinitionS3Location'],
        'AWS::AppSync::GraphQLSchema': ['DefinitionS3Location'],
        'AWS::AppSync::Resolver': [
            'RequestMappingTemplateS3Location',
            'ResponseMappingTemplateS3Location',
        ],
        'AWS::AppSync::FunctionConfiguration': [
            'RequestMappingTemplateS3Location',
            'ResponseMappingTemplateS3Location',
        ],
        'AWS::CloudFormation::Stack': ['TemplateURL'],
        'AWS::CodeCommit::Repository': ['S3'],
    }

    def __init__(self):
        """Init"""
        super().__init__()
        self.resource_property_types.extend(self.templated_exceptions.keys())

    def check_value(self, value, path):
        """Check the value"""
        matches = []
        if isinstance(value, str):
            if not value.startswith('s3://') and not value.startswith('https://'):
                message = f'This code may only work with `package` cli command as the property ({"/".join(map(str, path))}) is a string'
                matches.append(RuleMatch(path, message))

        return matches

    def match_resource_properties(self, properties, resourcetype, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        for key in self.templated_exceptions.get(resourcetype, []):
            matches.extend(
                cfn.check_value(
                    obj=properties, key=key, path=path[:], check_value=self.check_value
                )
            )

        return matches
