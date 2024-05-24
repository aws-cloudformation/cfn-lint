"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
from collections import deque
from typing import Any

from cfnlint.helpers import FUNCTIONS, REGION_PRIMARY
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER, ResourceNotFoundError

LOGGER = logging.getLogger(__name__)


class Properties(CfnLintJsonSchema):
    """Check Base Resource Configuration"""

    id = "E3002"
    shortdesc = "Resource properties are invalid"
    description = "Making sure that resources properties are properly configured"
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#properties"
    tags = ["resources"]

    def __init__(self):
        """Init"""
        super().__init__(
            keywords=["Resources/*"],
            all_matches=True,
        )
        self.rule_set = {
            "additionalProperties": "E3002",
            "anyOf": "E3017",
            "properties": "E3002",
            "dependentExcluded": "E3020",
            "dependentRequired": "E3021",
            "required": "E3003",
            "requiredXor": "E3014",
            "enum": "E3030",
            "type": "E3012",
            "minLength": "E3033",
            "maxLength": "E3033",
            "uniqueItems": "E3037",
            "maximum": "E3034",
            "minimum": "E3034",
            "exclusiveMaximum": "E3034",
            "exclusiveMinimum": "E3034",
            "maxItems": "E3032",
            "minItems": "E3032",
            "pattern": "E3031",
            "prefixItems": "E3008",
            "oneOf": "E3018",
            "cfnLint": "E1101",
            "tagging": "E3024",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))

    def _validate_resource(self, validator: Validator, _, instance: Any, schema):
        validator = self.extend_validator(validator, schema, validator.context.evolve())
        yield from self._validate(validator, instance)

    def validate(
        self, validator: Validator, _, instance: Any, schema: Any
    ) -> ValidationResult:
        validator = validator.evolve(
            context=validator.context.evolve(
                functions=list(FUNCTIONS),
                strict_types=False,
            ),
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=True,
            ),
        )

        t = instance.get("Type")
        if not validator.is_type(t, "string"):
            return

        if t.startswith("Custom::"):
            t = "AWS::CloudFormation::CustomResource"

        properties = instance.get("Properties", {})
        cached_regions = []
        cached_schema = None
        for region in validator.context.regions:
            schema = {}
            try:
                schema = PROVIDER_SCHEMA_MANAGER.get_resource_schema(region, t)
            except ResourceNotFoundError as e:
                LOGGER.info(e)
                continue
            if schema:
                if schema.json_schema:
                    if not schema.is_cached and region != REGION_PRIMARY:
                        region_validator = validator.evolve(
                            context=validator.context.evolve(
                                regions=[region],
                                path=validator.context.path.evolve(
                                    cfn_path=deque(["Resources", t, "Properties"]),
                                ).descend(path="Properties"),
                            )
                        )
                        for err in self._validate_resource(
                            region_validator, t, properties, schema.json_schema
                        ):
                            err.path.appendleft("Properties")
                            yield err

                    else:
                        if not cached_schema:
                            cached_schema = schema
                        cached_regions.append(region)

        if cached_regions and cached_schema:
            region_validator = validator.evolve(
                context=validator.context.evolve(
                    regions=cached_regions,
                    path=validator.context.path.evolve(
                        cfn_path=deque(["Resources", t, "Properties"]),
                    ).descend(path="Properties"),
                )
            )

            for err in self._validate_resource(
                region_validator, t, properties, cached_schema.json_schema
            ):
                err.path.appendleft("Properties")
                yield err
