"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch
import cfnlint.helpers

class AllowedValues(CloudFormationLintRule):
    """Check Property Allowed Values Configuration"""
    id = 'E3030'
    shortdesc = 'Check property values against allowed values'
    description = 'If an array of "AllowedValues" is speficied for a property, ' \
                  'check the value of the property. PrimitiveType and Required is ' \
                  'handled in other rules, so those are not checked here.'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['resources', 'properties', 'allowedvalues']

    cfn = {}

    def __init__(self):
        """Init"""
        super(AllowedValues, self).__init__()
        allowed_values_spec = cfnlint.helpers.load_resources('data/AdditionalSpecs/AllowedValues.json')
        self.allowed_resourcetypes = allowed_values_spec['ResourceTypes']
        self.allowed_propertytypes = allowed_values_spec['PropertyTypes']
        # Grab the full resource spec for processing nested properties
        resourcespecs = cfnlint.helpers.RESOURCE_SPECS['us-east-1']
        self.resourcetypes = resourcespecs['ResourceTypes']
        self.propertytypes = resourcespecs['PropertyTypes']

    def propertycheck(self, text, proptype, parenttype, resourcename, tree, root):
        """Check individual properties"""

        matches = list()
        if root:
            allowed_specs = self.allowed_resourcetypes
            specs = self.resourcetypes
            resourcetype = parenttype
        else:
            allowed_specs = self.allowed_propertytypes
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

        resourcespec = specs[resourcetype]['Properties']
        allowed_resourcespec = {}
        if resourcetype in allowed_specs:
            allowed_resourcespec = allowed_specs[resourcetype]['Properties']

        if not isinstance(text, dict):
            # Covered with Properties
            return matches

        resource_objects = list()
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
                        for sub_key, sub_value in cond_value['Value'].items():
                            append_object[sub_key] = sub_value

                        append_object['Value'] = append_object
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

                if prop in allowed_resourcespec:
                    allowed_values = allowed_resourcespec[prop].get('AllowedValues')

                    # Check if there's a value at all. Required is handled by
                    # the required properties rule (E3003)
                    if prop in value:

                        if not isinstance(value[prop], dict):
                            if value[prop] not in allowed_values:
                                message = 'Invalid property value "{0}" specified for {1}. Allowed value(s): {2}'
                                spec_path = path + [prop]
                                matches.append(RuleMatch(spec_path, message.format(
                                    value[prop],
                                    '/'.join(map(str, spec_path)),
                                    ', '.join(map(str, allowed_values))
                                )))

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
        matches = list()

        self.cfn = cfn

        for resourcename, resourcevalue in cfn.get_resources().items():
            if 'Properties' in resourcevalue and 'Type' in resourcevalue:
                resourcetype = resourcevalue['Type']
                if resourcetype in self.allowed_resourcetypes:
                    tree = ['Resources', resourcename, 'Properties']
                    matches.extend(self.propertycheck(
                        resourcevalue['Properties'], '',
                        resourcetype, resourcename, tree, True))

        return matches
