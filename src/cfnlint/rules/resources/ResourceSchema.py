"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import regex as re
from jsonschema import ValidationError, validate

from cfnlint.helpers import (
    FN_PREFIX,
    PSEUDOPARAMS,
    REGEX_DYN_REF,
    REGISTRY_SCHEMAS,
    UNCONVERTED_SUFFIXES,
)
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class ResourceSchema(CloudFormationLintRule):
    id = "E3000"
    shortdesc = "Resource schema"
    description = "CloudFormation Registry resource schema validation"
    source_url = (
        "https://github.com/aws-cloudformation/aws-cloudformation-resource-schema/"
    )
    tags = ["resources"]

    def match(self, cfn):
        matches = []
        for schema in REGISTRY_SCHEMAS:
            resource_type = schema["typeName"]
            for resource_name, resource_values in cfn.get_resources(
                [resource_type]
            ).items():
                properties = resource_values.get("Properties", {})
                # ignoring resources with CloudFormation template syntax in Properties
                if (
                    not re.match(REGEX_DYN_REF, str(properties))
                    and not any(
                        x in str(properties)
                        for x in PSEUDOPARAMS + UNCONVERTED_SUFFIXES
                    )
                    and FN_PREFIX not in str(properties)
                ):
                    try:
                        validate(properties, schema)
                    except ValidationError as e:
                        matches.append(
                            RuleMatch(
                                ["Resources", resource_name, "Properties"], e.message
                            )
                        )
        return matches
