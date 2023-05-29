"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import re
from typing import Dict, Union

from jsonschema import Draft7Validator
from jsonschema.exceptions import best_match
from jsonschema.validators import extend

from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template

LOGGER = logging.getLogger("cfnlint")


class GetAtt(CloudFormationLintRule):
    """Check if GetAtt values are correct"""

    id = "E1010"
    shortdesc = "GetAtt validation of parameters"
    description = (
        "Validates that GetAtt parameters are to valid resources and properties of"
        " those resources"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html"
    tags = ["functions", "getatt"]

    # pylint: disable=unused-argument
    def _enum(self, validator, enums, instance, schema):
        enums.sort()
        if instance not in enums:
            if validator.is_type(instance, "string"):
                for enum in enums:
                    _rex = re.compile(enum)
                    if _rex.fullmatch(instance):
                        return

            yield ValidationError(f"{instance!r} is not one of {enums!r}")

    def match(self, cfn: Template):
        matches = []
        getatts = cfn.search_deep_keys("Fn::GetAtt")
        valid_getatts = cfn.get_valid_getatts()

        for region in cfn.regions:
            schemas = valid_getatts.json_schema(region)
            for getatt in getatts:
                v = getatt[-1]
                err: Union[None, ValidationError] = None
                for schema in schemas.get("oneOf"):
                    validator_schema: Union[None, Dict] = None
                    if isinstance(v, list):
                        if schema.get("type") == "array":
                            validator_schema = schema
                    elif isinstance(v, str):
                        if schema.get("type") == "string":
                            validator_schema = schema
                    else:
                        matches.append(
                            RuleMatch(
                                path=getatt[:-1],
                                message="Fn::GetAtt should be a list or a string",
                            )
                        )

                    if validator_schema:
                        validator = extend(
                            validator=Draft7Validator,
                            validators={
                                "enum": self._enum,
                            },
                        )(schema=validator_schema)
                        err = best_match(validator.iter_errors(instance=v))

                if err:
                    matches.append(RuleMatch(path=getatt[:-1], message=err.message))

        return matches
