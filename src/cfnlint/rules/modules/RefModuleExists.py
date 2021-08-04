"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import MODULE_SCHEMAS


class RefModuleExist(CloudFormationLintRule):
    id = 'E5002'
    shortdesc = 'Check if Refs to modules exist'
    description = 'Making sure the refs to modules exist'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html'
    tags = ['functions', 'ref', 'modules']

    def match(self, cfn):
        matches = []

        # Build the list of refs
        reftrees = cfn.search_deep_keys('Ref')
        valid_refs = cfn.get_valid_refs()

        # start with the basic ref calls
        for reftree in reftrees:
            ref = reftree[-1]
            if isinstance(ref, (six.string_types, six.text_type, int)):
                if ref in valid_refs:
                    # puts the dict's values in a list, finds the position of the value and gets the
                    # key at that position
                    if valid_refs[ref]['Type'] == 'MODULE':
                        valid_ref = list(valid_refs.keys())[list(valid_refs.values()).index(valid_refs[ref])]
                        module_logical_resource_id = valid_ref.split('.*')[0]
                        for path in MODULE_SCHEMAS:
                            self.validate_refs(path, cfn, valid_ref, ref, module_logical_resource_id, matches, reftree)
        return matches

    def validate_refs(self, path, cfn, valid_ref, ref, module_logical_resource_id, matches, reftree):
        if path.endswith(cfn.get_resources()[valid_ref.split('.*')[0]]['Type'].replace(':', '-')) \
                and any(x in str(path) for x in cfn.regions):
            with open(path + '/schema.json', 'r') as f:
                schema = json.loads(json.loads(f.read())['Schema'])
                resources = schema['properties']['Resources']
                resource_logical_id = ref.split(module_logical_resource_id)[-1].replace('.', '')
                valid_resources = resources['properties'].keys()
                if resource_logical_id not in valid_resources:
                    message = 'Ref {0} is not a valid module resource reference, {1} is not a valid ' \
                              'resource logical id of the module {2}'
                    matches.append(RuleMatch(
                        reftree[:-2], message.format(ref, resource_logical_id,
                                                     module_logical_resource_id)
                    ))
