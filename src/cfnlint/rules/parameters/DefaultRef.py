"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class DefaultRef(CloudFormationLintRule):
    """Check if Parameter defaults don't use Refs"""
    id = 'E2014'
    shortdesc = 'Default value cannot use Refs'
    description = 'Check if Refs are not used in Parameter Defaults'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html'
    tags = ['parameters', 'ref']

    def match(self, cfn):
        matches = []

        ref_objs = cfn.search_deep_keys('Ref')

        # Filter out the Parameters
        parameter_refs = [x for x in ref_objs if x[0] == 'Parameters']

        for parameter_ref in parameter_refs:
            message = 'Invalid value ({}), Ref cannot be used in Parameters'
            matches.append(RuleMatch(parameter_ref, message.format(parameter_ref[-1])))

        return matches
