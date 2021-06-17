"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
import cfnlint.helpers


class Properties(CloudFormationLintRule):
    """Check Base Resource Configuration"""
    id = 'E3002'
    shortdesc = 'Resource properties are valid'
    description = 'Making sure that resources properties are properly configured'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#properties'
    tags = ['resources']

    def __init__(self):
        """Init"""
        super(Properties, self).__init__()
        self.cfn = {}
        self.resourcetypes = {}
        self.propertytypes = {}
        self.parameternames = {}
        self.intrinsictypes = {}

    def primitivetypecheck(self, value, primtype, proppath):
        """
            Check primitive types.
            Only check that a primitive type is actual a primitive type:
            - If its JSON let it go
            - If its Conditions check each sub path of the condition
            - If its a object make sure its a valid function and function
            - If its a list raise an error

        """

        matches = []
        if isinstance(value, list) or value == {'Ref': 'AWS::NotificationARNs'}:
            message = 'Property should be of type %s not List at %s' % (
                primtype, '/'.join(map(str, proppath)))
            matches.append(RuleMatch(proppath, message))
        if isinstance(value, dict) and primtype == 'Json':
            return matches
        if isinstance(value, dict):
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
                                         'Fn::If', 'Fn::Contains', 'Fn::Sub', 'Fn::Cidr', 'Fn::Transform']:
                        message = 'Property %s has an illegal function %s' % (
                            '/'.join(map(str, proppath)), sub_key)
                        matches.append(RuleMatch(proppath, message))
            else:
                message = 'Property is an object instead of %s at %s' % (
                    primtype, '/'.join(map(str, proppath)))
                matches.append(RuleMatch(proppath, message))

        return matches

    def _check_list_for_condition(self, text, prop, parenttype, resourcename, propspec, path):
        """ Loop for conditions """
        matches = []
        if len(text) == 3:
            for if_i, if_v in enumerate(text[1:]):
                condition_path = path[:] + [if_i + 1]
                if isinstance(if_v, list):
                    for index, item in enumerate(if_v):
                        arrproppath = condition_path[:]

                        arrproppath.append(index)
                        matches.extend(self.propertycheck(
                            item, propspec['ItemType'],
                            parenttype, resourcename, arrproppath, False))
                elif isinstance(if_v, dict):
                    if len(if_v) == 1:
                        for d_k, d_v in if_v.items():
                            if d_k != 'Ref' or d_v != 'AWS::NoValue':
                                if d_k == 'Fn::GetAtt':
                                    resource_name = None
                                    if isinstance(d_v, list):
                                        resource_name = d_v[0]
                                    elif isinstance(d_v, six.string_types):
                                        resource_name = d_v.split('.')[0]
                                    if resource_name:
                                        resource_type = self.cfn.template.get(
                                            'Resources', {}).get(resource_name, {}).get('Type')
                                        if not (resource_type.startswith('Custom::')):
                                            message = 'Property {0} should be of type List for resource {1} at {2}'
                                            matches.append(
                                                RuleMatch(
                                                    condition_path,
                                                    message.format(prop, resourcename, ('/'.join(str(x) for x in condition_path)))))
                                elif d_k == 'Fn::If':
                                    matches.extend(
                                        self._check_list_for_condition(
                                            d_v, prop, parenttype, resourcename, propspec, condition_path)
                                    )
                                else:
                                    message = 'Property {0} should be of type List for resource {1} at {2}'
                                    matches.append(
                                        RuleMatch(
                                            condition_path,
                                            message.format(prop, resourcename, ('/'.join(str(x) for x in condition_path)))))
                    else:
                        message = 'Property {0} should be of type List for resource {1} at {2}'
                        matches.append(
                            RuleMatch(
                                condition_path,
                                message.format(prop, resourcename, ('/'.join(str(x) for x in condition_path)))))
                else:
                    message = 'Property {0} should be of type List for resource {1} at {2}'
                    matches.append(
                        RuleMatch(
                            condition_path,
                            message.format(prop, resourcename, ('/'.join(str(x) for x in condition_path)))))

        else:
            message = 'Invalid !If condition specified at %s' % (
                '/'.join(map(str, path)))
            matches.append(RuleMatch(path, message))

        return matches

    def check_list_for_condition(self, text, prop, parenttype, resourcename, propspec, path):
        """Checks lists that are a dict for conditions"""
        matches = []
        if len(text[prop]) == 1:  # pylint: disable=R1702
            for sub_key, sub_value in text[prop].items():
                if sub_key in cfnlint.helpers.CONDITION_FUNCTIONS:
                    matches.extend(self._check_list_for_condition(
                        sub_value, prop, parenttype, resourcename, propspec, path + [sub_key]
                    ))
                else:
                    # FindInMaps can be lists of objects so skip checking those
                    if sub_key != 'Fn::FindInMap':
                        # if its a GetAtt to a custom resource that custom resource
                        # can return a list of objects so skip.
                        if sub_key == 'Fn::GetAtt':
                            resource_name = None
                            if isinstance(sub_value, list):
                                resource_name = sub_value[0]
                            elif isinstance(sub_value, six.string_types):
                                resource_name = sub_value.split('.')[0]
                            if resource_name:
                                resource_type = self.cfn.template.get(
                                    'Resources', {}).get(resource_name, {}).get('Type')
                                if not (resource_type == 'AWS::CloudFormation::CustomResource' or resource_type.startswith('Custom::')):
                                    message = 'Property is an object instead of List at %s' % (
                                        '/'.join(map(str, path)))
                                    matches.append(RuleMatch(path, message))
                        elif not (sub_key == 'Ref' and sub_value == 'AWS::NoValue'):
                            message = 'Property is an object instead of List at %s' % (
                                '/'.join(map(str, path)))
                            matches.append(RuleMatch(path, message))
                    else:
                        self.logger.debug(
                            'Too much logic to handle whats actually in the map "%s" so skipping any more validation.', sub_value)
        else:
            message = 'Property is an object instead of List at %s' % ('/'.join(map(str, path)))
            matches.append(RuleMatch(path, message))

        return matches

    def check_exceptions(self, parenttype, proptype, text):
        """
            Checks for exceptions to the spec
            - Start with handling exceptions for templated code.
        """
        templated_exceptions = {
            'AWS::ApiGateway::RestApi': ['S3Location'],
            'AWS::Lambda::Function': ['Code'],
            'AWS::Lambda::LayerVersion': ['Content'],
            'AWS::ElasticBeanstalk::ApplicationVersion': ['SourceBundle'],
            'AWS::StepFunctions::StateMachine': ['S3Location'],
        }

        exceptions = templated_exceptions.get(parenttype, [])
        if proptype in exceptions:
            if isinstance(text, six.string_types):
                return True

        return False

    def propertycheck(self, text, proptype, parenttype, resourcename, path, root):
        """Check individual properties"""

        parameternames = self.parameternames
        matches = []
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
        if not resourcespec:
            if specs[resourcetype].get('Type') == 'List':
                if isinstance(text, list):
                    property_type = specs[resourcetype].get('ItemType')
                    for index, item in enumerate(text):
                        matches.extend(
                            self.propertycheck(
                                item, property_type, parenttype, resourcename,
                                path[:] + [index], root))

            return matches
        supports_additional_properties = specs[resourcetype].get('AdditionalProperties', False)

        if text == 'AWS::NoValue':
            return matches
        if not isinstance(text, dict):
            if not self.check_exceptions(parenttype, proptype, text):
                message = 'Expecting an object at %s' % ('/'.join(map(str, path)))
                matches.append(RuleMatch(path, message))
            return matches

        # You can put in functions directly in place of objects as long as that is
        # the only thing there (conditions, select) could all (possibly)
        # return objects.  FindInMap cannot directly return an object.
        len_of_text = len(text)

        #pylint: disable=too-many-nested-blocks
        for prop in text:
            proppath = path[:]
            proppath.append(prop)
            if prop not in resourcespec:
                if prop in cfnlint.helpers.CONDITION_FUNCTIONS and len_of_text == 1:
                    cond_values = self.cfn.get_condition_values(text[prop])
                    for cond_value in cond_values:
                        if isinstance(cond_value['Value'], dict):
                            matches.extend(self.propertycheck(
                                cond_value['Value'], proptype, parenttype, resourcename,
                                proppath + cond_value['Path'], root))
                        elif isinstance(cond_value['Value'], list):
                            for index, item in enumerate(cond_value['Value']):
                                matches.extend(
                                    self.propertycheck(
                                        item, proptype, parenttype, resourcename,
                                        proppath + cond_value['Path'] + [index], root)
                                )
                elif text.is_function_returning_object():
                    self.logger.debug('Ran into function "%s".  Skipping remaining checks', prop)
                elif len(text) == 1 and prop in 'Ref' and text.get(prop) == 'AWS::NoValue':
                    pass
                elif not supports_additional_properties:
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
                                    matches.extend(self.primitivetypecheck(
                                        item, primtype, arrproppath))
                            elif isinstance(text[prop], dict):
                                if 'Ref' in text[prop]:
                                    ref = text[prop]['Ref']
                                    if ref == 'AWS::NotificationARNs':
                                        continue
                                    if ref in parameternames:
                                        param_type = self.cfn.template['Parameters'][ref]['Type']
                                        if param_type:
                                            if 'List<' not in param_type and '<List' not in param_type and not param_type == 'CommaDelimitedList':
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
                                    if len(text[prop]) == 1:
                                        for k in text[prop].keys():
                                            def_intrinsic_type = self.intrinsictypes.get(k, {})
                                            if def_intrinsic_type:
                                                if len(def_intrinsic_type.get('ReturnTypes')) == 1 and def_intrinsic_type.get('ReturnTypes')[0] == 'Singular':
                                                    message = 'Property {0} is using {1} when a List is needed for resource {2}'
                                                    matches.append(
                                                        RuleMatch(
                                                            proppath,
                                                            message.format(prop, k, resourcename)))
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
        matches = []
        self.cfn = cfn

        resourcespecs = cfnlint.helpers.RESOURCE_SPECS[cfn.regions[0]]
        self.resourcetypes = resourcespecs['ResourceTypes']
        self.propertytypes = resourcespecs['PropertyTypes']
        self.intrinsictypes = resourcespecs['IntrinsicTypes']
        self.parameternames = self.cfn.get_parameter_names()
        for resourcename, resourcevalue in cfn.get_resources().items():
            if 'Properties' in resourcevalue and 'Type' in resourcevalue:
                resourcetype = resourcevalue.get('Type', None)
                if resourcetype.startswith('Custom::') and resourcetype not in self.resourcetypes:
                    resourcetype = 'AWS::CloudFormation::CustomResource'
                if resourcetype in self.resourcetypes:
                    path = ['Resources', resourcename, 'Properties']
                    matches.extend(self.propertycheck(
                        resourcevalue.get('Properties', {}), '',
                        resourcetype, resourcename, path, True))

        return matches
