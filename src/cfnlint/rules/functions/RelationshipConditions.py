"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.helpers import PSEUDOPARAMS
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class RelationshipConditions(CloudFormationLintRule):
    """Check if Ref/GetAtt values are available via conditions"""
    id = 'W1001'
    shortdesc = 'Ref/GetAtt to resource that is available when conditions are applied'
    description = 'Check the Conditions that affect a Ref/GetAtt to make sure ' \
                  'the resource being related to is available when there is a resource ' \
                  'condition.'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html'
    tags = ['conditions', 'resources', 'relationships', 'ref', 'getatt']

    def match(self, cfn):
        """Check CloudFormation Ref/GetAtt for Conditions"""

        matches = []

        # Start with Ref checks
        ref_objs = cfn.search_deep_keys('Ref')
        for ref_obj in ref_objs:
            value = ref_obj[-1]
            if value not in PSEUDOPARAMS:
                scenarios = cfn.is_resource_available(ref_obj, value)
                for scenario in scenarios:
                    scenario_text = ' and '.join(
                        ['when condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
                    message = 'Ref to resource "{0}" that may not be available {1} at {2}'
                    matches.append(
                        RuleMatch(
                            ref_obj[:-1],
                            message.format(
                                value,
                                scenario_text,
                                '/'.join(map(str, ref_obj[:-1])))))

        # The do GetAtt
        getatt_objs = cfn.search_deep_keys('Fn::GetAtt')
        for getatt_obj in getatt_objs:
            value_obj = getatt_obj[-1]
            value = None
            if isinstance(value_obj, list):
                value = value_obj[0]
            elif isinstance(value_obj, six.string_types):
                value = value_obj.split('.')[0]
            if value:
                if value not in PSEUDOPARAMS:
                    scenarios = cfn.is_resource_available(getatt_obj, value)
                    for scenario in scenarios:
                        scenario_text = ' and '.join(
                            ['when condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
                        message = 'GetAtt to resource "{0}" that may not be available {1} at {2}'
                        matches.append(
                            RuleMatch(
                                getatt_obj[:-1],
                                message.format(
                                    value,
                                    scenario_text,
                                    '/'.join(map(str, getatt_obj[:-1])))))

        return matches
