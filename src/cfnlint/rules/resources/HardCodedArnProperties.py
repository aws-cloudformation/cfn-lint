"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
import json
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class HardCodedArnProperties(CloudFormationLintRule):
    """Checks Resources if ARNs use correctly placed Pseudo Parameters instead of hardcoded Partition, Region, and Account Number"""
    id = 'W3042'
    shortdesc = 'ARNs should use correctly placed Pseudo Parameters'
    description = 'Checks Resources if ARNs use correctly placed Pseudo Parameters instead of hardcoded Partition, Region, and Account Number'
    source_url = ''
    tags = ['resources']

    def match(self, cfn):
        """Check CloudFormation Resources"""
        matches = []
        pattern = re.compile("arn:(\$\{[^:]*::[^:]*}|[^:]*):[^:]+:(\$\{[^:]*::[^:]*}|[^:]*):(\$\{[^:]*::[^:]*}|[^:]*)")
        resources = cfn.template.get('Resources', {})
        if resources:
            for resourcename, val  in resources.items():
                candidates = pattern.findall(str(val))
                for candidate in candidates:
                    if candidate[0] != "${AWS::Partition}" or candidate[1] not in ("${AWS::Region}","") or candidate[2] not in ("${AWS::AccountId}",""):
                        message = 'ARN in Resource {0} contains hardcoded Partition, Region, and/or Account Number in ARN or incorrectly placed Pseudo Parameters'
                        matches.append(RuleMatch(
                            ['Resources', resourcename],
                            message.format(resourcename)
                        ))
                        break
        return matches
