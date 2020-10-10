"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import os
from glob import glob
from jsonschema import validate, ValidationError
from cfnlint.helpers import load_resource
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.data import CloudformationSchema

class ResourceSchema(CloudFormationLintRule):
    id = 'E3000'
    shortdesc = ''
    description = ''
    source_url = ''
    tags = []

    def match(self, cfn):
        matches = []
        for file in [os.path.basename(f) for f in glob('src/cfnlint/data/CloudformationSchema/*.json')]:
            resource_type = load_resource(CloudformationSchema, file)['typeName']
            for resource_name, resource_values in cfn.get_resources([resource_type]).items():
                properties = resource_values.get('Properties', {})
                try:
                    validate(properties, load_resource(CloudformationSchema, file))
                except ValidationError as e:
                    matches.append(RuleMatch(['Resources', resource_name], e.message))
        return matches
