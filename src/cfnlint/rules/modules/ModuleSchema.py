"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
import json
from jsonschema import validate, ValidationError, SchemaError
from cfnlint.helpers import REGEX_DYN_REF, PSEUDOPARAMS, FN_PREFIX, UNCONVERTED_SUFFIXES, REGISTRY_SCHEMAS
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch

class ModuleSchema(object):
    id = 'E3000'
    shortdesc = 'Module schema'
    description = 'CloudFormation Registry module schema validation'
    source_url = 'https://github.com/aws-cloudformation/aws-cloudformation-resource-schema/'
    tags = ['resources']

    def __init__(self, template, path):
        self.path = path
        self.template = template

    def match(self):
        matches = []
        f = open(self.path + '/schema.json', 'r')
        schema = json.loads(json.loads(f.read())['Schema'])
        name = schema['typeName']
        for resource_name, resource_values in self.template.get_resources([name]).items():
            properties = resource_values.get('Properties', {})
            parameters = schema['properties']['Parameters']
            try:
                validate(properties, parameters)
            except ValidationError as e:
                matches.append(RuleMatch(['Modules', resource_name, 'Properties'], e.message))
                raise e
        return matches
