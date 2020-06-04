"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class ServerlessTransform(CloudFormationLintRule):
    """Check if Serverless Resources exist without the Serverless Transform"""

    id = 'E3038'
    shortdesc = 'Check if Serverless Resources have Serverless Transform'
    description = (
        'Check that a template with Serverless Resources also includes the Serverless Transform'
    )
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['resources', 'transform']

    def match(self, cfn):
        matches = []

        transforms = cfn.template.get('Transform', [])
        if not isinstance(transforms, list):
            transforms = [transforms]
        has_serverless_transform = any(
            transform == 'AWS::Serverless-2016-10-31' for transform in transforms
        )
        if has_serverless_transform:
            return matches

        for resource_name, resource_values in cfn.get_resources().items():
            resource_type = resource_values['Type']
            if resource_type.startswith('AWS::Serverless::'):
                message = 'Serverless Transform required for Type {0} for resource {1}'
                matches.append(
                    RuleMatch(['Transform'], message.format(resource_type, resource_name))
                )
                break
        return matches
