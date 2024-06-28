"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from typing import Any

from cfnlint.helpers import REGEX_DYN_REF
from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules.functions._BaseFn import BaseFn

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
        {"type": "string"},  # version-stage or version-id
    ],
    "minItems": 3,
    "maxItems": 7,
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
        {"type": "string"},  # version-stage or version-id
    ],
    "minItems": 9,
    "maxItems": 13,
    "type": "array",
}


class DynamicReference(BaseFn):
    id = "E1050"
    shortdesc = "Validate the structure of a dynamic reference"
    description = "Make sure dynamic reference strings have the correct syntax"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html"
    tags = ["functions", "dynamic reference"]

    def __init__(self) -> None:
        super().__init__()
        self.child_rules = {
            "E1051": None,
            "E1027": None,
        }

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

        # SSM parameters can be used in Resources and Outputs and Parameters
        # SSM secrets are only used in a small number of locations
        # Secrets manager can be used only in resource properties
        validator = validator.evolve(
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=False,
            ),
        )

        for v in REGEX_DYN_REF.findall(instance):
            parts = v.split(":")

            found = False
            evolved = validator.evolve(schema=_all)
            for err in evolved.iter_errors(parts):
                yield self._clean_errors(err)
                found = True

            if found:
                continue

            if parts[1] == "ssm":
                evolved = validator.evolve(schema=_ssm)
            elif parts[1] == "ssm-secure":
                evolved = validator.evolve(schema=_ssm)
                rule = self.child_rules["E1027"]
                if rule and hasattr(rule, "validate"):
                    yield from rule.validate(validator, {}, v, schema)
            else:
                if parts[2] == "arn":
                    evolved = validator.evolve(schema=_secrets_manager_arn)
                else:  # this is secrets manager
                    evolved = validator.evolve(schema=_secrets_manager)
                rule = self.child_rules["E1051"]
                if rule and hasattr(rule, "validate"):
                    yield from rule.validate(validator, {}, v, schema)

            for err in evolved.iter_errors(parts):
                yield self._clean_errors(err)
