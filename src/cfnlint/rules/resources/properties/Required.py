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


class Required(CloudFormationLintRule):
    """Check Required Resource Configuration"""
    id = 'E3003'
    shortdesc = 'Required Resource Parameters are missing'
    description = 'Making sure that Resources properties ' + \
                  'that are required exist'
    tags = ['base', 'resources']

    def __init__(self):
        resourcespecs = cfnlint.helpers.RESOURCE_SPECS['us-east-1']
        self.resourcetypes = resourcespecs['ResourceTypes']
        self.propertytypes = resourcespecs['PropertyTypes']

    def propertycheck(self, text, proptype, parenttype, resourcename, tree, root):
        """Check individual properties"""

        matches = list()
        if root:
            specs = self.resourcetypes
            resourcetype = parenttype
        else:
            specs = self.propertytypes
            resourcetype = str.format("{0}.{1}", parenttype, proptype)
            # handle tags
            if resourcetype not in specs:
                if proptype in specs:
                    resourcetype = proptype
                else:
                    resourcetype = str.format("{0}.{1}", parenttype, proptype)
            else:
                resourcetype = str.format("{0}.{1}", parenttype, proptype)

        resourcespec = specs[resourcetype]['Properties']
        if not isinstance(text, dict):
            # Covered with Properties not with Required
            return matches
        for prop in resourcespec:
            if resourcespec[prop]['Required']:
                if prop not in text:
                    proptree = tree[:]
                    proptree.pop()
                    skip = False
                    if 'PrimitiveType' in specs[resourcetype]['Properties'][prop]:
                        if specs[resourcetype]['Properties'][prop]['PrimitiveType'] == 'Json':
                            skip = True
                        else:
                            message = "Property {0} missing from resource {1}"
                            matches.append(RuleMatch(proptree, message.format(prop, resourcename)))
                    if isinstance(text, dict) and not skip:
                        if not text:
                            message = "Property {0} missing from resource {1}"
                            matches.append(RuleMatch(proptree, message.format(prop, resourcename)))
                        for key in text:
                            if key in resourcespec:
                                arrproptree = tree[:]
                                arrproptree.append(key)
                                if key in cfnlint.helpers.CONDITION_FUNCTIONS:
                                    matches.extend(self.propertycheck(
                                        text[key][1], proptype,
                                        parenttype, resourcename, arrproptree, False))
                                    matches.extend(self.propertycheck(
                                        text[key][2], proptype,
                                        parenttype, resourcename, arrproptree, False))
                    else:
                        message = "Property {0} missing from resource {1}"
                        matches.append(RuleMatch(proptree, message.format(prop, resourcename)))
        for prop in text:
            proptree = tree[:]
            proptree.append(prop)
            if prop in resourcespec:
                if 'Type' in resourcespec[prop]:
                    if resourcespec[prop]['Type'] == 'List':
                        if 'PrimitiveItemType' not in resourcespec[prop]:
                            if isinstance(text[prop], list):
                                for index, item in enumerate(text[prop]):
                                    arrproptree = proptree[:]
                                    arrproptree.append(index)
                                    matches.extend(self.propertycheck(
                                        item, resourcespec[prop]['ItemType'],
                                        parenttype, resourcename, arrproptree, False))
                    else:
                        if resourcespec[prop]['Type'] not in ['Map']:
                            matches.extend(self.propertycheck(
                                text[prop], resourcespec[prop]['Type'],
                                parenttype, resourcename, proptree, False))

        return matches

    def match(self, cfn):
        """Check CloudFormation Properties"""
        matches = list()

        for resourcename, resourcevalue in cfn.get_resources().items():
            if 'Properties' in resourcevalue and 'Type' in resourcevalue:
                resourcetype = resourcevalue['Type']
                if resourcetype in self.resourcetypes:
                    tree = ['Resources', resourcename, 'Properties']
                    matches.extend(self.propertycheck(
                        resourcevalue['Properties'], '',
                        resourcetype, resourcename, tree, True))

        return matches
