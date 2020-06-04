"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Configuration(CloudFormationLintRule):
    """Check if Conditions are configured correctly"""
    id = 'E8001'
    shortdesc = 'Conditions have appropriate properties'
    description = 'Check if Conditions are properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/conditions-section-structure.html'
    tags = ['conditions']

    condition_keys = [
        'Condition',
        'Fn::And',
        'Fn::Equals',
        'Fn::Not',
        'Fn::Or',
    ]

    def match(self, cfn):
        matches = []

        conditions = cfn.template.get('Conditions', {})
        if conditions:
            for condname, condobj in conditions.items():
                if not isinstance(condobj, dict):
                    message = 'Condition {0} has invalid property'
                    matches.append(RuleMatch(
                        ['Conditions', condname],
                        message.format(condname)
                    ))
                else:
                    if len(condobj) != 1:
                        message = 'Condition {0} has too many intrinsic conditions'
                        matches.append(RuleMatch(
                            ['Conditions', condname],
                            message.format(condname)
                        ))
                    else:
                        for k, _ in condobj.items():
                            if k not in self.condition_keys:
                                message = 'Condition {0} has invalid property {1}'
                                matches.append(RuleMatch(
                                    ['Conditions', condname] + [k],
                                    message.format(condname, k)
                                ))

        return matches
