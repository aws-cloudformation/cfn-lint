"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
import cfnlint.helpers

class Required(CloudFormationLintRule):
    """Check Required Resource Configuration"""
    id = 'E3003'
    shortdesc = 'Required Resource properties are missing'
    description = 'Making sure that Resources properties that are required exist'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#required'
    tags = ['resources']

    def __init__(self):
        """Init"""
        super(Required, self).__init__()
        self.resourcetypes = []
        self.propertytypes = []

    def initialize(self, cfn):
        """Initialize the rule"""
        resourcespecs = cfnlint.helpers.RESOURCE_SPECS[cfn.regions[0]]
        self.resourcetypes = resourcespecs['ResourceTypes']
        self.propertytypes = resourcespecs['PropertyTypes']
        self.resource_property_types = []
        self.resource_sub_property_types = []
        for resource_type_spec in self.resourcetypes.keys():
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in self.propertytypes.keys():
            self.resource_sub_property_types.append(property_type_spec)

    def _get_required_attrs_specs(self, resource_specs):
        reqr = []
        for k, v in resource_specs.get('Properties', {}).items():
            if v.get('Required', False):
                reqr.append(k)

        return reqr

    def check_obj(self, obj, required_attributes, path, _):
        matches = []

        for safe_obj, safe_path in obj.items_safe(path):
            for required_attribute in required_attributes:
                if required_attribute not in safe_obj:
                    message = 'Property {0} missing at {1}'
                    matches.append(RuleMatch(
                        safe_path,
                        message.format(required_attribute,
                                       '/'.join(map(str, safe_path)))
                    ))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        if properties is None:
            # covered under rule E3001.  If there are required properties properties is required first
            return matches

        matches.extend(
            self.check_obj(
                properties,
                self._get_required_attrs_specs(
                    self.resourcetypes.get(resource_type)),
                path, cfn)
        )

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []
        matches.extend(
            self.check_obj(
                properties,
                self._get_required_attrs_specs(
                    self.propertytypes.get(property_type)),
                path, cfn)
        )

        return matches

    def match(self, cfn):
        """Check CloudFormation Properties"""
        matches = []

        for resourcename, resourcevalue in cfn.get_resources().items():
            if 'Properties' in resourcevalue and 'Type' in resourcevalue:
                resource_type = resourcevalue['Type']
                if resource_type.startswith('Custom::') and resource_type not in self.resourcetypes:
                    resource_type = 'AWS::CloudFormation::CustomResource'
                    matches.extend(
                        self.check_obj(
                            resourcevalue['Properties'],
                            self._get_required_attrs_specs(
                                self.resourcetypes.get(resource_type)),
                            ['Resources', resourcename, 'Properties'], cfn)
                    )

        return matches
