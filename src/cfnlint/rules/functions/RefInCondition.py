"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class RefInCondition(CloudFormationLintRule):
    """Check if Ref value is a string"""
    id = 'E1026'
    shortdesc = 'Cannot reference resources in the Conditions block of the template'
    description = 'Check that any Refs in the Conditions block uses no resources'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#w2ab2c21c28c21c45'
    tags = ['conditions', 'functions', 'ref']

    def match(self, cfn):
        matches = []

        ref_objs = cfn.search_deep_keys('Ref')
        resource_names = cfn.get_resource_names()

        for ref_obj in ref_objs:
            if ref_obj[0] == 'Conditions':
                value = ref_obj[-1]
                if isinstance(value, (str, int)):
                    if value in resource_names:
                        message = 'Cannot reference resource {0} in the Conditions block of the template at {1}'
                        matches.append(
                            RuleMatch(ref_obj[:-1], message.format(value, '/'.join(map(str, ref_obj[:-1])))))

        return matches
