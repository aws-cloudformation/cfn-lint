"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
import cfnlint.helpers
from cfnlint.data import AdditionalSpecs


class Exclusive(CloudFormationLintRule):
    """Check Properties Resource Configuration"""
    id = 'E2520'
    shortdesc = 'Check Properties that are mutually exclusive'
    description = 'Making sure CloudFormation properties that are exclusive are not defined'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['resources']

    def __init__(self):
        """Init"""
        super(Exclusive, self).__init__()
        exclusivespec = cfnlint.helpers.load_resource(AdditionalSpecs, 'Exclusive.json')
        self.resource_types_specs = exclusivespec['ResourceTypes']
        self.property_types_specs = exclusivespec['PropertyTypes']
        for resource_type_spec in self.resource_types_specs:
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in self.property_types_specs:
            self.resource_sub_property_types.append(property_type_spec)

    def check(self, properties, exclusions, path, cfn):
        """Check itself"""
        matches = []

        property_sets = cfn.get_object_without_conditions(properties)
        for property_set in property_sets:
            obj = property_set['Object'].clean()
            for prop in obj:
                if prop in exclusions:
                    for excl_property in exclusions[prop]:
                        if excl_property in obj:
                            if property_set['Scenario'] is None:
                                message = 'Property {0} should NOT exist with {1} for {2}'
                                matches.append(RuleMatch(
                                    path + [prop],
                                    message.format(excl_property, prop, '/'.join(map(str, path)))
                                ))
                            else:
                                scenario_text = ' and '.join(['when condition "%s" is %s' % (
                                    k, v) for (k, v) in property_set['Scenario'].items()])
                                message = 'Property {0} should NOT exist with {1} {2} for {3}'
                                matches.append(RuleMatch(
                                    path + [prop],
                                    message.format(excl_property, prop, scenario_text,
                                                   '/'.join(map(str, path)))
                                ))

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = []

        exclusions = self.property_types_specs.get(property_type, {})
        matches.extend(self.check(properties, exclusions, path, cfn))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        exclusions = self.resource_types_specs.get(resource_type, {})
        matches.extend(self.check(properties, exclusions, path, cfn))

        return matches
