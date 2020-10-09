"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
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
        for resource_name, resource_values in cfn.get_resources(['AWS::Logs::LogGroup']).items():
            properties = resource_values.get('Properties', {})
            try:
                validate(properties, load_resource(CloudformationSchema, 'aws-logs-loggroup.json'))
            except ValidationError as e:
                matches.append(RuleMatch(['Resources', resource_name], e.message))
        return matches
