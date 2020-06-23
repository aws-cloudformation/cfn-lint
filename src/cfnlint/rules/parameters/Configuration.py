"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Configuration(CloudFormationLintRule):
    """Check if Parameters are configured correctly"""
    id = 'E2001'
    shortdesc = 'Parameters have appropriate properties'
    description = 'Making sure the parameters are properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html'
    tags = ['parameters']

    valid_keys = {
        'AllowedPattern': {
            'Type': 'String'
        },
        'AllowedValues': {
            'Type': 'List',
            'ItemType': 'String',
        },
        'ConstraintDescription': {
            'Type': 'String'
        },
        'Default': {
            'Type': 'String'
        },
        'Description': {
            'Type': 'String'
        },
        'MaxLength': {
            'Type': 'Integer',
            'ValidForTypes': ['String']
        },
        'MaxValue': {
            'Type': 'Integer',
            'ValidForTypes': ['Number']
        },
        'MinLength': {
            'Type': 'Integer',
            'ValidForTypes': ['String']
        },
        'MinValue': {
            'Type': 'Integer',
            'ValidForTypes': ['Number']
        },
        'NoEcho': {
            'Type': 'Boolean'
        },
        'Type': {
            'Type': 'String'
        }
    }

    required_keys = [
        'Type'
    ]

    def check_type(self, value, path, props):
        """ Check the type and handle recursion with lists """
        results = []
        prop_type = props.get('Type')
        try:
            if prop_type in ['List']:
                if isinstance(value, list):
                    for i, item in enumerate(value):
                        results.extend(self.check_type(item, path[:] + [i], {
                            'Type': props.get('ItemType')
                        }))
                else:
                    message = 'Property %s should be of type %s' % (
                        '/'.join(map(str, path)), prop_type)
                    results.append(RuleMatch(path, message))
            if prop_type in ['String']:
                if isinstance(value, (dict, list)):
                    message = 'Property %s should be of type %s' % (
                        '/'.join(map(str, path)), prop_type)
                    results.append(RuleMatch(path, message))
                str(value)
            elif prop_type in ['Boolean']:
                if not isinstance(value, bool):
                    if value not in ['True', 'true', 'False', 'false']:
                        message = 'Property %s should be of type %s' % (
                            '/'.join(map(str, path)), prop_type)
                        results.append(RuleMatch(path, message))
            elif prop_type in ['Integer']:
                if isinstance(value, bool):
                    message = 'Property %s should be of type %s' % (
                        '/'.join(map(str, path)), prop_type)
                    results.append(RuleMatch(path, message))
                else:  # has to be a Double
                    int(value)
        except Exception:  # pylint: disable=W0703
            message = 'Property %s should be of type %s' % (
                '/'.join(map(str, path)), prop_type)
            results.append(RuleMatch(path, message,))

        return results

    def match(self, cfn):
        matches = []

        for paramname, paramvalue in cfn.get_parameters().items():
            for propname, propvalue in paramvalue.items():
                if propname not in self.valid_keys:
                    message = 'Parameter {0} has invalid property {1}'
                    matches.append(RuleMatch(
                        ['Parameters', paramname, propname],
                        message.format(paramname, propname)
                    ))
                else:
                    props = self.valid_keys.get(propname)
                    prop_path = ['Parameters', paramname, propname]
                    matches.extend(self.check_type(
                        propvalue, prop_path, props))
                    # Check that the property is needed for the current type
                    valid_for = props.get('ValidForTypes')
                    if valid_for is not None and paramvalue.get('Type'):
                        if paramvalue.get('Type') not in valid_for:
                            message = 'Parameter {0} has property {1} which is only valid for {2}'
                            matches.append(RuleMatch(
                                ['Parameters', paramname, propname],
                                message.format(paramname, propname, valid_for)
                            ))

            for reqname in self.required_keys:
                if reqname not in paramvalue.keys():
                    message = 'Parameter {0} is missing required property {1}'
                    matches.append(RuleMatch(
                        ['Parameters', paramname],
                        message.format(paramname, reqname)
                    ))

        return matches
