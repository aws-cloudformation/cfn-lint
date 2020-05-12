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
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/cfn-resource-specification.md#required'
    tags = ['resources']

    cfn = {}

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

    def propertycheck(self, text, proptype, parenttype, resourcename, tree, root):
        """Check individual properties"""

        matches = []
        if root:
            specs = self.resourcetypes
            resourcetype = parenttype
        else:
            specs = self.propertytypes
            resourcetype = str.format('{0}.{1}', parenttype, proptype)
            # handle tags
            if resourcetype not in specs:
                if proptype in specs:
                    resourcetype = proptype
                else:
                    resourcetype = str.format('{0}.{1}', parenttype, proptype)
            else:
                resourcetype = str.format('{0}.{1}', parenttype, proptype)

        resourcespec = specs[resourcetype].get('Properties')
        if not resourcespec:
            if specs[resourcetype].get('Type') == 'List':
                if isinstance(text, list):
                    property_type = specs[resourcetype].get('ItemType')
                    for index, item in enumerate(text):
                        matches.extend(
                            self.propertycheck(
                                item, property_type, parenttype, resourcename,
                                tree[:] + [index], root))
            else:
                # this isn't a standard type in the CloudFormation spec so we
                # can't check required so skip
                return matches

        if not isinstance(text, dict):
            # Covered with Properties not with Required
            return matches

        # Return empty matches if we run into a function that is being used to get an object
        # Selects could be used to return an object when used with a FindInMap
        if text.is_function_returning_object():
            return matches

        # Check if all required properties are specified
        resource_objects = []
        base_object_properties = {}
        for key, value in text.items():
            if key not in cfnlint.helpers.CONDITION_FUNCTIONS:
                base_object_properties[key] = value
        condition_found = False
        for key, value in text.items():
            if key in cfnlint.helpers.CONDITION_FUNCTIONS:
                condition_found = True
                cond_values = self.cfn.get_condition_values(value)
                for cond_value in cond_values:
                    if isinstance(cond_value['Value'], dict):
                        append_object = {}
                        append_object['Path'] = tree[:] + [key] + cond_value['Path']
                        append_object['Value'] = {}
                        for sub_key, sub_value in cond_value['Value'].items():
                            append_object['Value'][sub_key] = sub_value

                        append_object['Value'].update(base_object_properties)
                        resource_objects.append(append_object)

        if not condition_found:
            resource_objects.append({
                'Path': tree[:],
                'Value': base_object_properties
            })

        for resource_object in resource_objects:
            path = resource_object.get('Path')
            value = resource_object.get('Value')
            for prop in resourcespec:
                if resourcespec[prop]['Required']:
                    if prop not in value:
                        message = 'Property {0} missing at {1}'
                        matches.append(RuleMatch(path, message.format(
                            prop, '/'.join(map(str, path)))))

            # For all specified properties, check all nested properties
            for prop in value:
                proptree = path[:]
                proptree.append(prop)
                if prop in resourcespec:
                    if 'Type' in resourcespec[prop]:
                        if resourcespec[prop]['Type'] == 'List':
                            if 'PrimitiveItemType' not in resourcespec[prop]:
                                if isinstance(value[prop], list):
                                    for index, item in enumerate(value[prop]):
                                        arrproptree = proptree[:]
                                        arrproptree.append(index)
                                        matches.extend(self.propertycheck(
                                            item, resourcespec[prop]['ItemType'],
                                            parenttype, resourcename, arrproptree, False))
                        else:
                            if resourcespec[prop]['Type'] not in ['Map']:
                                matches.extend(self.propertycheck(
                                    value[prop], resourcespec[prop]['Type'],
                                    parenttype, resourcename, proptree, False))

        return matches

    def match(self, cfn):
        """Check CloudFormation Properties"""
        matches = []

        self.cfn = cfn

        for resourcename, resourcevalue in cfn.get_resources().items():
            if 'Properties' in resourcevalue and 'Type' in resourcevalue:
                resourcetype = resourcevalue['Type']
                if resourcetype.startswith('Custom::') and resourcetype not in self.resourcetypes:
                    resourcetype = 'AWS::CloudFormation::CustomResource'
                if resourcetype in self.resourcetypes:
                    tree = ['Resources', resourcename, 'Properties']
                    matches.extend(self.propertycheck(
                        resourcevalue['Properties'], '',
                        resourcetype, resourcename, tree, True))

        return matches
