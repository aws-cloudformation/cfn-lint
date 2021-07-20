"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
import re
from jsonschema import validate, ValidationError
from cfnlint.helpers import REGEX_DYN_REF, PSEUDOPARAMS, FN_PREFIX, UNCONVERTED_SUFFIXES, MODULE_SCHEMAS
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch

class ModuleSchema(CloudFormationLintRule):
    id = 'E5002'
    shortdesc = 'Check that Module properties are valid'
    description = 'CloudFormation Registry module schema validation'
    source_url = 'https://github.com/aws-cloudformation/aws-cloudformation-resource-schema/'
    tags = ['resources', 'modules']

    def match(self, cfn):
        matches = []
        for path in MODULE_SCHEMAS:
            with open(path + '/schema.json', 'r') as f:
                schema = json.loads(json.loads(f.read())['Schema'])
                name = schema['typeName']
                for resource_name, resource_values in cfn.get_resources([name]).items():
                    properties = resource_values.get('Properties', {})
                    parameters = schema['properties']['Parameters']
                    # ignoring modules with CloudFormation template syntax in PropertiesAdd
                    for name, value in properties.items():
                        if not re.match(REGEX_DYN_REF, str(value)) and not any(x in str(value) for x in PSEUDOPARAMS + UNCONVERTED_SUFFIXES) and FN_PREFIX not in str(value):
                            try:
                                validate({name: value}, parameters)
                            except ValidationError as e:
                                path = ['Resources', resource_name, 'Properties']
                                for element in e.path:
                                    path.append(element)
                                matches.append(RuleMatch(path, e.message))
            return matches
