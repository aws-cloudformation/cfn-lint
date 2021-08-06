"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import MODULE_SCHEMAS, RESOURCE_SPECS


class GetAttModule(CloudFormationLintRule):
    id = 'E5003'
    shortdesc = 'Check if GetAtts to modules exists'
    description = 'Making sure the GetAtts to modules exist'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html'
    tags = ['functions', 'getatt', 'modules']

    def match(self, cfn):
        matches = []
        # Build the list of getAtts
        getatts = cfn.search_deep_keys('Fn::GetAtt')
        valid_getatts = cfn.get_valid_getatts()
        modules_keys = cfn.get_modules().keys()

        # start with the basic getatt calls
        for getatt in getatts:
            # JSON template
            if isinstance(getatt[-1], six.string_types):
                resname, restype = getatt[-1].split('.', 1)
            else:
                resname = None
                restype = None
                # YAML template
                if isinstance(getatt[-1][1], six.string_types):
                    resname = getatt[-1][0]
                    restype = '.'.join(getatt[-1][1:])
            # if it's a module
            if any(resname.startswith(s) for s in valid_getatts) and any(resname.startswith(m) for m in
                                                                         modules_keys):
                for module in modules_keys:
                    if resname.startswith(module):
                        for path in MODULE_SCHEMAS:
                            if path.endswith(cfn.get_resources()[module]['Type'].replace(':', '-')) and \
                                    any(x in str(path) for x in cfn.regions):
                                self.validate_attributes(path, matches, resname, module, cfn, restype, getatt)
        return matches

    def validate_attributes(self, path, matches, resname, module, cfn, restype, getatt):
        with open(path + '/schema.json', 'r') as f:
            schema = json.loads(json.loads(f.read())['Schema'])
            resources = schema['properties']['Resources']
            resource_logical_id = resname.split(module)[-1]
            valid_resources = resources['properties'].keys()
            if resource_logical_id in valid_resources:
                for region in cfn.regions:
                    resource = resources['properties'][resource_logical_id] \
                        ['properties']['Type']['const']
                    resourcetypes = RESOURCE_SPECS[region].get('ResourceTypes')
                    if resource in resourcetypes:
                        if 'Attributes' in resourcetypes[resource]:
                            if not any(restype == attname for attname in
                                       resourcetypes[resource]['Attributes'].keys()):
                                message = 'GetAtt {0}.{1} is invalid: {1} is not a valid ' \
                                          'attribute of {2}'
                                matches.append(RuleMatch(
                                    getatt, message.format(resname, restype,
                                                           resource)))
                        else:
                            message = 'GetAtt {0}.{1} is invalid: {2} doesn\'t ' \
                                      'have attributes'
                            matches.append(RuleMatch(
                                getatt, message.format(resname, restype,
                                                       resource)))
                    else:
                        message = 'GetAtt {0} is invalid: {1} is not a valid ' \
                                  'resource'
                        matches.append(RuleMatch(
                            getatt, message.format(resname,
                                                   resource)))
            else:
                message = 'GetAtt {0}.{3} is invalid: {1} is not a valid ' \
                          'resource logical id of the module {2}'
                matches.append(RuleMatch(
                    getatt, message.format(resname, resource_logical_id,
                                           module, restype)))
