"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
import cfnlint.helpers
from cfnlint.data import AdditionalSpecs


class UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes(CloudFormationLintRule):
    """Check for UpdateReplacePolicy / DeletionPolicy"""
    id = 'I3011'
    shortdesc = 'Check stateful resources have a set UpdateReplacePolicy/DeletionPolicy'
    description = 'The default action when replacing/removing a resource is to ' \
                  'delete it. This check requires you to explicitly set policies'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html'
    tags = ['resources', 'updatereplacepolicy', 'deletionpolicy']

    def __init__(self):
        """Init"""
        super(UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes, self).__init__()

        spec = cfnlint.helpers.load_resource(AdditionalSpecs, 'StatefulResources.json')

        self.likely_stateful_resource_types = [
            resource_type
            for resource_type, descr in spec['ResourceTypes'].items()

            # Resources that won't be deleted if they're not empty (ex: S3)
            # don't need to be checked for policies, as chance of mistakes are low.
            if not descr.get('DeleteRequiresEmptyResource', False)]

    def match(self, cfn):
        """Check for UpdateReplacePolicy / DeletionPolicy"""
        matches = []

        resources = cfn.get_resources()
        for r_name, r_values in resources.items():
            if r_values.get('Type') in self.likely_stateful_resource_types:
                if not r_values.get('DeletionPolicy') or not r_values.get('UpdateReplacePolicy'):
                    path = ['Resources', r_name]
                    message = 'The default action when replacing/removing a resource is to delete it. Set explicit values for UpdateReplacePolicy / DeletionPolicy on potentially stateful resource: %s' \
                    % '/'.join(path)
                    matches.append(RuleMatch(path, message))

        return matches
