"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
import cfnlint.helpers
from cfnlint.data import AdditionalSpecs


class AtLeastOne(CloudFormationLintRule):
    """Check Properties Resource Configuration"""
    id = 'E2522'
    shortdesc = 'Check Properties that need at least one of a list of properties'
    description = 'Making sure CloudFormation properties ' + \
                  'that require at least one property from a list. ' + \
                  'More than one can be included.'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['resources']

    def __init__(self):
        """Init"""
        super(AtLeastOne, self).__init__()
        atleastonespec = cfnlint.helpers.load_resource(AdditionalSpecs, 'AtLeastOne.json')
        self.resource_types_specs = atleastonespec['ResourceTypes']
        self.property_types_specs = atleastonespec['PropertyTypes']
        for resource_type_spec in self.resource_types_specs:
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in self.property_types_specs:
            self.resource_sub_property_types.append(property_type_spec)

    def check(self, properties, atleastoneprops, path, cfn):
        """Check itself"""
        matches = []

        for atleastoneprop in atleastoneprops:
            for (safe_properties, safe_path) in properties.items_safe(path):
                property_sets = cfn.get_object_without_conditions(safe_properties, atleastoneprop)
                for property_set in property_sets:
                    count = 0
                    for prop in atleastoneprop:
                        if prop in property_set['Object']:
                            count += 1

                    if count == 0:
                        if property_set['Scenario'] is None:
                            message = 'At least one of [{0}] should be specified for {1}'
                            matches.append(RuleMatch(
                                path,
                                message.format(', '.join(map(str, atleastoneprop)),
                                               '/'.join(map(str, safe_path)))
                            ))
                        else:
                            scenario_text = ' and '.join(['when condition "%s" is %s' % (
                                k, v) for (k, v) in property_set['Scenario'].items()])
                            message = 'At least one of [{0}] should be specified {1} at {2}'
                            matches.append(RuleMatch(
                                path,
                                message.format(', '.join(map(str, atleastoneprop)),
                                               scenario_text, '/'.join(map(str, safe_path)))
                            ))

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = []

        atleastoneprops = self.property_types_specs.get(property_type, {})
        matches.extend(self.check(properties, atleastoneprops, path, cfn))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        atleastoneprops = self.resource_types_specs.get(resource_type, {})
        matches.extend(self.check(properties, atleastoneprops, path, cfn))

        return matches
