"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.helpers import VALID_PARAMETER_TYPES
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Types(CloudFormationLintRule):
    """Check if Parameters are typed"""
    id = 'E2002'
    shortdesc = 'Parameters have appropriate type'
    description = 'Making sure the parameters have a correct type'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#parmtypes'
    tags = ['parameters']

    def match(self, cfn):
        matches = []

        for paramname, paramvalue in cfn.get_parameters_valid().items():
            # If the type isn't found we create a valid one
            # this test isn't about missing required properties for a
            # parameter.
            paramtype = paramvalue.get('Type', 'String')
            if paramtype not in VALID_PARAMETER_TYPES:
                message = 'Parameter {0} has invalid type {1}'
                matches.append(RuleMatch(
                    ['Parameters', paramname, 'Type'],
                    message.format(paramname, paramtype)
                ))

        return matches
