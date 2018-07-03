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


class Properties(CloudFormationLintRule):
    """Check Base Resource Configuration"""
    id = 'E3002'
    shortdesc = 'Resource properties are valid'
    description = 'Making sure that resources properties ' + \
                  'are propery configured'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['resources']

    def __init__(self):
        self.cfn = {}
        self.resourcetypes = {}
        self.propertytypes = {}
        self.parameternames = {}

    def primitivetypecheck(self, value, primtype, proppath):
        """
            Check primitive types.
            Only check that a primitive type is actual a primitive type:
            - If its JSON let it go
            - If its Conditions check each sub path of the condition
            - If its a object make sure its a valid function and function
            - If its a list raise an error

        """

        matches = list()
        if isinstance(value, dict) and primtype == 'Json':
            return matches
        elif isinstance(value, dict):
            if len(value) == 1:
                for sub_key, sub_value in value.items():
                    if sub_key in cfnlint.helpers.CONDITION_FUNCTIONS:
                        # not erroring on bad Ifs but not need to account for it
                        # so the rule doesn't error out
                        if isinstance(sub_value, list):
                            if len(sub_value) == 3:
                                matches.extend(self.primitivetypecheck(
                                    sub_value[1], primtype, proppath + ['Fn::If', 1]))
                                matches.extend(self.primitivetypecheck(
                                    sub_value[2], primtype, proppath + ['Fn::If', 2]))
                    elif sub_key not in ['Fn::Base64', 'Fn::GetAtt', 'Fn::GetAZs', 'Fn::ImportValue',
                                         'Fn::Join', 'Fn::Split', 'Fn::FindInMap', 'Fn::Select', 'Ref',
                                         'Fn::If', 'Fn::Contains', 'Fn::Sub', 'Fn::Cidr']:
                        message = 'Property %s has an illegal function %s' % ('/'.join(map(str, proppath)), sub_key)
                        matches.append(RuleMatch(proppath, message))
            else:
                message = 'Property is an object instead of %s at %s' % (primtype, '/'.join(map(str, proppath)))
                matches.append(RuleMatch(proppath, message))
        elif isinstance(value, list):
            message = 'Property should be of type %s not List at %s' % (primtype, '/'.join(map(str, proppath)))
            matches.append(RuleMatch(proppath, message))

        return matches

    def check_list_for_condition(self, text, prop, parenttype, resourcename, propspec, path):
        """Checks lists that are a dict for conditions"""
        matches = list()
        if len(text[prop]) == 1:
            for sub_key, sub_value in text[prop].items():
                if sub_key in cfnlint.helpers.CONDITION_FUNCTIONS:
                    if len(sub_value) == 3:
                        if isinstance(sub_value[1], list):
                            for index, item in enumerate(sub_value[1]):
                                arrproppath = path[:]

                                arrproppath.append(index)
                                matches.extend(self.propertycheck(
                                    item, propspec['ItemType'],
                                    parenttype, resourcename, arrproppath, False))
                        else:
                            message = 'Property {0} should be of type List for resource {1}'
                            matches.append(
                                RuleMatch(
                                    path,
                                    message.format(prop, resourcename)))

                        if isinstance(sub_value[2], list):
                            for index, item in enumerate(sub_value[2]):
                                arrproppath = path[:]

                                arrproppath.append(index)
                                matches.extend(self.propertycheck(
                                    item, propspec['ItemType'],
                                    parenttype, resourcename, arrproppath, False))
                        else:
                            message = 'Property {0} should be of type List for resource {1} at {2}'
                            matches.append(
                                RuleMatch(
                                    path + [2],
                                    message.format(prop, resourcename, ('/'.join(str(x) for x in path)))))

                    else:
                        message = 'Invalid !If condition specified at %s' % ('/'.join(map(str, path)))
                        matches.append(RuleMatch(path, message))
                else:
                    message = 'Property is an object instead of List at %s' % ('/'.join(map(str, path)))
                    matches.append(RuleMatch(path, message))
        else:
            message = 'Property is an object instead of List at %s' % ('/'.join(map(str, path)))
            matches.append(RuleMatch(path, message))

        return matches

    def propertycheck(self, text, proptype, parenttype, resourcename, path, root):
        """Check individual properties"""

        parameternames = self.parameternames
        matches = list()
        if root:
            specs = self.resourcetypes
            resourcetype = parenttype
        else:
            specs = self.propertytypes
            resourcetype = str.format('{0}.{1}', parenttype, proptype)
            # Handle tags
            if resourcetype not in specs:
                if proptype in specs:
                    resourcetype = proptype
                else:
                    resourcetype = str.format('{0}.{1}', parenttype, proptype)
            else:
                resourcetype = str.format('{0}.{1}', parenttype, proptype)

        resourcespec = specs[resourcetype].get('Properties', {})
        if text == 'AWS::NoValue':
            return matches
        if not isinstance(text, dict):
            message = 'Expecting an object at %s' % ('/'.join(map(str, path)))
            matches.append(RuleMatch(path, message))
            return matches
        for prop in text:
            proppath = path[:]
            proppath.append(prop)
            if prop not in resourcespec:
                if prop in cfnlint.helpers.CONDITION_FUNCTIONS:
                    cond_values = self.cfn.get_condition_values(text[prop])
                    for cond_value in cond_values:
                        matches.extend(self.propertycheck(
                            cond_value['Value'], proptype, parenttype, resourcename,
                            proppath + cond_value['Path'], root))
                elif prop != 'Metadata':
                    message = 'Invalid Property %s' % ('/'.join(map(str, proppath)))
                    matches.append(RuleMatch(proppath, message))
            else:
                if 'Type' in resourcespec[prop]:
                    if resourcespec[prop]['Type'] == 'List':
                        if 'PrimitiveItemType' not in resourcespec[prop]:
                            if isinstance(text[prop], list):
                                for index, item in enumerate(text[prop]):
                                    arrproppath = proppath[:]
                                    arrproppath.append(index)
                                    matches.extend(self.propertycheck(
                                        item, resourcespec[prop]['ItemType'],
                                        parenttype, resourcename, arrproppath, False))
                            elif (isinstance(text[prop], dict)):
                                # A list can be be specific as a Conditional
                                matches.extend(
                                    self.check_list_for_condition(
                                        text, prop, parenttype, resourcename, resourcespec[prop], proppath)
                                )
                            else:
                                message = 'Property {0} should be of type List for resource {1}'
                                matches.append(
                                    RuleMatch(
                                        proppath,
                                        message.format(prop, resourcename)))
                        else:
                            if isinstance(text[prop], list):
                                primtype = resourcespec[prop]['PrimitiveItemType']
                                for index, item in enumerate(text[prop]):
                                    arrproppath = proppath[:]
                                    arrproppath.append(index)
                                    matches.extend(self.primitivetypecheck(item, primtype, arrproppath))
                            elif isinstance(text[prop], dict):
                                if 'Ref' in text[prop]:
                                    ref = text[prop]['Ref']
                                    if ref in parameternames:
                                        if 'Type' in self.cfn.template['Parameters'][ref]:
                                            if not self.cfn.template['Parameters'][ref]['Type'].startswith('List<'):
                                                message = 'Property {0} should be of type List or Parameter should ' \
                                                          'be a list for resource {1}'
                                                matches.append(
                                                    RuleMatch(
                                                        proppath,
                                                        message.format(prop, resourcename)))
                                    else:
                                        message = 'Property {0} should be of type List for resource {1}'
                                        matches.append(
                                            RuleMatch(
                                                proppath,
                                                message.format(prop, resourcename)))
                            else:
                                message = 'Property {0} should be of type List for resource {1}'
                                matches.append(
                                    RuleMatch(
                                        proppath,
                                        message.format(prop, resourcename)))
                    else:
                        if resourcespec[prop]['Type'] not in ['Map']:
                            matches.extend(self.propertycheck(
                                text[prop], resourcespec[prop]['Type'], parenttype,
                                resourcename, proppath, False))
                elif 'PrimitiveType' in resourcespec[prop]:
                    primtype = resourcespec[prop]['PrimitiveType']
                    matches.extend(self.primitivetypecheck(text[prop], primtype, proppath))

        return matches

    def match(self, cfn):
        """Check CloudFormation Properties"""
        matches = list()
        self.cfn = cfn

        resourcespecs = cfnlint.helpers.RESOURCE_SPECS[cfn.regions[0]]
        self.resourcetypes = resourcespecs['ResourceTypes']
        self.propertytypes = resourcespecs['PropertyTypes']
        self.parameternames = self.cfn.get_parameter_names()
        for resourcename, resourcevalue in cfn.get_resources().items():
            if 'Properties' in resourcevalue and 'Type' in resourcevalue:
                resourcetype = resourcevalue.get('Type', None)
                if resourcetype in self.resourcetypes:
                    path = ['Resources', resourcename, 'Properties']
                    matches.extend(self.propertycheck(
                        resourcevalue.get('Properties', {}), '',
                        resourcetype, resourcename, path, True))

        return matches
