"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import cfnlint.data.schemas.other.resources
from cfnlint.helpers import FUNCTIONS, is_function
from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails
from cfnlint.schema.resolver import RefResolver


class Configuration(CfnLintJsonSchema):
    """Check Update Policy Configuration"""

    id = "E3016"
    shortdesc = "Check the configuration of a resources UpdatePolicy"
    description = "Make sure a resources UpdatePolicy is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-updatepolicy.html"
    tags = ["resources", "updatepolicy"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/*"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.other.resources,
                filename="update_policy.json",
            ),
            all_matches=True,
        )

    def validate(self, validator: Validator, keywords: Any, instance: Any, schema: Any):
        update_policy = instance.get("UpdatePolicy")
        function, _ = is_function(update_policy)
        if (
            function == "Fn::Select"
            and not validator.context.transforms.has_language_extensions_transform()
        ):
            yield ValidationError(
                f"{update_policy!r} is not of type 'object'",
                path=["UpdatePolicy"],
                rule=self,
                instance=update_policy,
                validator="type",
                validator_value="object",
                schema_path=[
                    "allOf",
                    0,
                    "then",
                    "properties",
                    "UpdatePolicy",
                    "type",
                ],
            )
            return

        validator = validator.evolve(
            context=validator.context.evolve(
                functions=list(FUNCTIONS),
                strict_types=False,
            ),
            schema=self._schema,
            resolver=RefResolver.from_schema(
                self._schema,
            ),
        )

        yield from super()._iter_errors(validator, instance)
