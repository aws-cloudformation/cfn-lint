"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.helpers import INVALID_MODULES
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class ModuleInRegistry(CloudFormationLintRule):
    id = 'E5005'
    shortdesc = 'Check that Module exists in the CloudFormation registry'
    description = 'CloudFormation Registry module validation'
    source_url = 'https://github.com/aws-cloudformation/aws-cloudformation-resource-schema/'
    tags = ['resources', 'modules']

    def match(self, cfn):
        # pylint: disable=unused-argument
        matches = []
        for name in INVALID_MODULES:
            path = ['Resources', name, 'Type']
            matches.append(RuleMatch(path, INVALID_MODULES[name]))
        return matches
