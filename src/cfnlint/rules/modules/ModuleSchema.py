"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from jsonschema import validate, ValidationError
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import MODULE_SCHEMAS

class ModuleSchema(CloudFormationLintRule):
    id = 'E5002'
    shortdesc = 'Check that Module properties are valid'
    description = 'CloudFormation Registry module schema validation'
    source_url = 'https://github.com/aws-cloudformation/aws-cloudformation-resource-schema/'
    tags = ['resources', 'modules']

    def match(self, cfn):
        matches = []
        for path in MODULE_SCHEMAS:
            f = open(path + '/schema.json', 'r')
            schema = json.loads(json.loads(f.read())['Schema'])
            name = schema['typeName']
            for resource_name, resource_values in cfn.get_resources([name]).items():
                properties = resource_values.get('Properties', {})
                parameters = schema['properties']['Parameters']
                try:
                    validate(properties, parameters)
                except ValidationError as e:
                    path = ['Resources', resource_name, 'Properties']
                    for element in e.path:
                        path.append(element)
                    matches.append(RuleMatch(path, e.message))
            return matches
