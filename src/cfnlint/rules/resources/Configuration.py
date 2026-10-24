"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import cfnlint.data.schemas.other.resources
import cfnlint.helpers
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.jsonschema._keywords import patternProperties
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class ServerlessAdditionalProperties(CloudFormationLintRule):
    """Warn when SAM resource attributes are ignored"""

    id = "W3001"
    shortdesc = "SAM resource-level properties are ignored"
    description = (
        "Unknown resource-level properties on AWS::Serverless resources are ignored "
        "by the SAM transform. Move supported resource properties under Properties."
    )
    source_url = (
        "https://docs.aws.amazon.com/serverless-application-model/latest/"
        "developerguide/sam-specification.html"
    )
    tags = ["resources", "serverless"]

    def __init__(self) -> None:
        super().__init__()
        self.parent_rules = ["E3001"]


class Configuration(CfnLintJsonSchema):
    """Check Base Resource Configuration"""

    id = "E3001"
    shortdesc = "Basic CloudFormation Resource Check"
    description = (
        "Making sure the basic CloudFormation resources are properly configured"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["resources"]

    def __init__(self):
        super().__init__(
            keywords=["Resources"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.resources, "configuration.json"
            ),
            all_matches=True,
        )
        self.validators = {
            "maxProperties": None,
            "propertyNames": None,
            "patternProperties": self._pattern_properties,
        }
        self.rule_set = {
            "maxProperties": "E3010",
            "propertyNames": "E3011",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self.child_rules["W3001"] = ServerlessAdditionalProperties()

    def _pattern_properties(
        self, validator: Validator, aP: Any, instance: Any, schema: Any
    ):
        # We have to rework pattern properties
        # to re-add the keyword or we will have an
        # infinite loop
        validator = validator.evolve(
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=True,
            )
        )

        yield from patternProperties(validator, aP, instance, schema)

    def _is_serverless_additional_property(self, err: Any) -> bool:
        if err.validator != "additionalProperties":
            return False

        if len(err.path) < 2:
            return False

        if not isinstance(err.instance, dict):
            return False

        resource_type = err.instance.get("Type")
        return isinstance(resource_type, str) and resource_type.startswith(
            "AWS::Serverless::"
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        cfn_validator = self.extend_validator(
            validator=validator,
            schema=self._schema,
            context=validator.context.evolve(),
        )

        for err in self._iter_errors(cfn_validator, instance):
            if self._is_serverless_additional_property(err):
                err.message = err.message.replace(
                    "Additional properties are not allowed",
                    "Additional resource properties are ignored by the SAM transform",
                )
                err.rule = self.child_rules["W3001"]
            yield err
