"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from jsonschema import validate
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
        for resource in cfn.get_resources(['AWS::Logs::LogGroup']).values():
            properties = resource.get('Properties', {})
            validate(properties, load_resource(CloudformationSchema, 'aws-logs-loggroup.json'))
        return matches
