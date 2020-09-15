"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class UniqueNames(CloudFormationLintRule):
    id = 'E3007'
    shortdesc = 'Unique resource and parameter names'
    description = 'All resources and parameters must have unique names'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resources-section-structure.html'
    tags = ['parameters', 'resources']

    def match(self, cfn):
        matches = []
        for resource in cfn.get_resources():
            if resource in cfn.template.get('Parameters', {}):
                matches.append(RuleMatch(['Resources', resource], 'Resources and Parameters must not share name: ' + resource))
        return matches
