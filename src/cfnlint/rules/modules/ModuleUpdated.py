"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.helpers import MODULES_TO_UPDATE
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class ModuleUpdated(CloudFormationLintRule):
    id = 'W5001'
    shortdesc = 'Check that Module is the latest version'
    description = 'Check that Module is the latest version'
    source_url = 'https://github.com/aws-cloudformation/aws-cloudformation-resource-schema/'
    tags = ['resources', 'modules']

    def match(self, cfn):
        # pylint: disable=unused-argument
        matches = []
        for name in MODULES_TO_UPDATE:
            path = ['Resources', name, 'Type']
            matches.append(RuleMatch(path, 'a new version of your private registry type is available in the '
                                           'CloudFormation registry. Please use --update-registry-type-specs to access '
                                           'the latest version.'))
        return matches
