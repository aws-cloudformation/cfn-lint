"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Exists(CloudFormationLintRule):
    """Check if used Conditions are defined """
    id = 'E8002'
    shortdesc = 'Check if the referenced Conditions are defined'
    description = 'Making sure the used conditions are actually defined in the Conditions section'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/conditions-section-structure.html'
    tags = ['conditions']

    def match(self, cfn):
        matches = []
        ref_conditions = {}

        # Get all defined conditions
        conditions = cfn.template.get('Conditions', {})

        # Get all "If's" that reference a Condition
        iftrees = cfn.search_deep_keys('Fn::If')
        for iftree in iftrees:
            if isinstance(iftree[-1], list):
                if isinstance(iftree[-1][0], six.string_types):
                    ref_conditions[iftree[-1][0]] = iftree

        # Get resource's Conditions
        for resource_name, resource_values in cfn.get_resources().items():
            condition = resource_values.get('Condition')
            if isinstance(condition, six.string_types):  # make sure its a string
                path = ['Resources', resource_name, 'Condition']
                ref_conditions[condition] = path

        # Get conditions used by another condition
        condtrees = cfn.search_deep_keys('Condition')

        for condtree in condtrees:
            if condtree[0] == 'Conditions':
                if isinstance(condtree[-1], (str, six.text_type, six.string_types)):
                    path = ['Conditions', condtree[-1]]
                    ref_conditions[condtree[-1]] = path

        # Get Output Conditions
        for _, output_values in cfn.template.get('Outputs', {}).items():
            if 'Condition' in output_values:
                path = ['Outputs', output_values['Condition']]
                ref_conditions[output_values['Condition']] = path

        # Check if all the conditions are defined
        for ref_condition, ref_path in ref_conditions.items():
            if ref_condition not in conditions:
                message = 'Condition {0} is not defined.'
                matches.append(RuleMatch(
                    ref_path,
                    message.format(ref_condition)
                ))

        return matches
