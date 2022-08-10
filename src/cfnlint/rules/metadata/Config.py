"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Config(CloudFormationLintRule):
    """Check if Metadata configuration is properly configured"""
    id = 'E4002'
    shortdesc = 'Validate the configuration of the Metadata section'
    description = 'Validates that Metadata section is an object and has no null values'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/metadata-section-structure.html'
    tags = ['metadata']


    def _check_object(self, obj, path):
        results = []
        if isinstance(obj, (dict)):
            for k, v in obj.items():
                results.extend(self._check_object(v, path + [k]))
        if isinstance(obj, (list)):
            for i, v in enumerate(obj):
                results.extend(self._check_object(v, path + [i]))
        if obj is None:
            message = 'Metadata value cannot be null'
            results.append(RuleMatch(
                path,
                message.format(message)
            ))

        return results


    def match(self, cfn):
        """Check CloudFormation Metadata Interface Configuration"""

        matches = []

        metadata_obj = cfn.template.get('Metadata', {})
        if metadata_obj is None:
            message = 'Metadata value has to be an object'
            matches.append(RuleMatch(
                ['Metadata'],
                message.format(message)
            ))

        if metadata_obj:
            if isinstance(metadata_obj, dict):
                matches.extend(self._check_object(metadata_obj, ['Metadata']))

        return matches
