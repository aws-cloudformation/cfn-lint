"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import os
import re
from glob import glob
from jsonschema import validate, ValidationError
from cfnlint.helpers import load_resource, REGEX_DYN_REF, PSEUDOPARAMS, FN_PREFIX, UNCONVERTED_SUFFIXES
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
                if not re.match(REGEX_DYN_REF, str(properties)) and not any(x in str(properties) for x in PSEUDOPARAMS + UNCONVERTED_SUFFIXES) and FN_PREFIX not in str(properties):
                    try:
                        validate(properties, load_resource(CloudformationSchema, file))
                    except ValidationError as e:
                        matches.append(RuleMatch(['Resources', resource_name], e.message))
        return matches
