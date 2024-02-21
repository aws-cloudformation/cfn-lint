"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from typing import Any

from cfnlint.helpers import REGEX_DYN_REF
from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules import CloudFormationLintRule

_all = {
    "items": [
        {"type": "string", "const": "resolve"},
        {"type": "string", "enum": ["ssm", "ssm-secure", "secretsmanager"]},
    ],
    "minItems": 3,
}

_ssm = {
    "items": [
        {"type": "string", "const": "resolve"},
        {"type": "string", "enum": ["ssm", "ssm-secure"]},
        {"type": "string", "pattern": "[a-zA-Z0-9_.-/]+"},
        {"type": "string", "pattern": "\\d+"},
    ],
    "maxItems": 4,
    "type": "array",
}

_secrets_manager = {
    "items": [
        {"type": "string", "const": "resolve"},
        {"type": "string", "const": "secretsmanager"},
        {"type": "string", "pattern": "[ -~]*"},  # secret-id
        {"type": "string", "enum": ["SecretString", ""]},  # secret-string
        {"type": "string"},  # json-key
        {"type": "string"},  # version-stage or version-id
    ],
    "maxItems": 6,
    "type": "array",
}

_secrets_manager_arn = {
    "items": [
        {"type": "string", "const": "resolve"},
        {"type": "string", "const": "secretsmanager"},
        {"type": "string", "const": "arn"},  # arn
        {"type": "string"},  # partition
        {"type": "string"},  # service
        {"type": "string"},  # region
        {"type": "string"},  # account ID
        {"type": "string", "const": "secret"},  # secret
        {"type": "string"},  # secret
        {"type": "string", "enum": ["SecretString", ""]},  # secret-string
        {"type": "string"},  # json-key
        {"type": "string"},  # version-stage or version-id
    ],
    "maxItems": 12,
    "type": "array",
}


class DynamicReference(CloudFormationLintRule):
    """
    Check if Dynamic Reference Secure Strings are
    only used in the correct locations
    """

    id = "E1050"
    shortdesc = "Check dynamic references secure strings are in supported locations"
    description = (
        "Dynamic References Secure Strings are only supported for a small set of"
        " resource properties.  Validate that they are being used in the correct"
        " location when checking values and Fn::Sub in resource properties. Currently"
        " doesn't check outputs, maps, conditions, parameters, and descriptions."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html"
    tags = ["functions", "dynamic reference"]

    def _clean_errors(self, err: ValidationError) -> ValidationError:
        err.rule = self
        err.path = deque([])
        err.schema_path = deque([])
        return err

    def dynamicReference(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ):
        if not validator.is_type(instance, "string"):
            return

        for v in REGEX_DYN_REF.findall(instance):
            parts = v.split(":")

            evolved = validator.evolve(schema=_all)
            found = False
            for err in evolved.iter_errors(parts):
                yield self._clean_errors(err)
                found = True

            if found:
                return

            if parts[1] in ["ssm", "ssm-secure"]:
                evolved = validator.evolve(schema=_ssm)
            elif parts[2] == "arn":
                evolved = validator.evolve(schema=_secrets_manager_arn)
            else:
                evolved = validator.evolve(schema=_secrets_manager)

            for err in evolved.iter_errors(parts):
                yield self._clean_errors(err)
