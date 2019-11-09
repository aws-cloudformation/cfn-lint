"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Configuration(CloudFormationLintRule):
    """Check if Parameters are configured correctly"""
    id = 'E2001'
    shortdesc = 'Parameters have appropriate properties'
    description = 'Making sure the parameters are properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html'
    tags = ['parameters']

    valid_keys = [
        'AllowedPattern',
        'AllowedValues',
        'ConstraintDescription',
        'Default',
        'Description',
        'MaxLength',
        'MaxValue',
        'MinLength',
        'MinValue',
        'NoEcho',
        'Type',
    ]

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = []

        for paramname, paramvalue in cfn.get_parameters().items():
            for propname, _ in paramvalue.items():
                if propname not in self.valid_keys:
                    message = 'Parameter {0} has invalid property {1}'
                    matches.append(RuleMatch(
                        ['Parameters', paramname, propname],
                        message.format(paramname, propname)
                    ))

        return matches
