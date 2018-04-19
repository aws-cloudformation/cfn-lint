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
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch
import cfnlint.helpers


class Inclusive(CloudFormationLintRule):
    """Check Properties Resource Configuration"""
    id = 'E2521'
    shortdesc = 'Check Properties that are mutually exclusive'
    description = 'Making sure CloudFormation properties ' + \
                  'that are exclusive are not defined'
    tags = ['base', 'resources']

    def __init__(self):
        """Init"""
        inclusivespec = cfnlint.helpers.load_resources('data/ResourcePropertiesInclusive.json')
        self.resource_types_specs = inclusivespec['ResourceTypes']
        self.property_types_specs = inclusivespec['PropertyTypes']

    def propertycheck(self, text, proptype, parenttype, resourcename, path, root):
        """Check individual properties"""

        matches = list()
        if root:
            specs = self.resource_types_specs
            resourcetype = parenttype
        else:
            specs = self.property_types_specs
            resourcetype = str.format("{0}.{1}", parenttype, proptype)
            # Handle tags
            if resourcetype not in specs:
                if proptype in specs:
                    resourcetype = proptype
                else:
                    resourcetype = str.format("{0}.{1}", parenttype, proptype)
            else:
                resourcetype = str.format("{0}.{1}", parenttype, proptype)

        resourcespec = specs.get(resourcetype, {})
        if isinstance(text, (six.text_type, six.string_types, list, int)):
            return matches
        for prop in text:
            proppath = path[:]
            proppath.append(prop)
            if prop in resourcespec:
                for incl_property in resourcespec[prop]:
                    if incl_property not in text:
                        message = "Parameter {0} should exist with {1} for {2}"
                        matches.append(RuleMatch(
                            proppath,
                            message.format(incl_property, prop, resourcename)
                        ))
            if isinstance(text[prop], (dict)):
                matches.extend(self.propertycheck(
                    text[prop], prop,
                    resourcetype, resourcename, proppath, False))
            if isinstance(text[prop], (list)):
                for index, value in enumerate(text[prop]):
                    matches.extend(self.propertycheck(
                        value, prop,
                        resourcetype, resourcename, proppath + [index], False))

        return matches

    def match(self, cfn):
        """Check CloudFormation Properties"""
        matches = list()

        for resourcename, resourcevalue in cfn.get_resources().items():
            if 'Properties' in resourcevalue and 'Type' in resourcevalue:
                resourcetype = resourcevalue.get('Type', None)
                path = ['Resources', resourcename, 'Properties']
                matches.extend(self.propertycheck(
                    resourcevalue.get('Properties', {}), '',
                    resourcetype, resourcename, path, True))

        return matches
