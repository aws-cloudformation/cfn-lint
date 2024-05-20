"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import cfnlint.data.schemas.other.resources
import cfnlint.helpers
from cfnlint.jsonschema import Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class Metadata(CfnLintJsonSchema):
    """Check Base Resource Configuration"""

    id = "E3028"
    shortdesc = "Basic CloudFormation Resource Check"
    description = (
        "Making sure the basic CloudFormation resources are properly configured"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["resources"]

    def __init__(self):
        super().__init__(
            keywords=["Resources/*/Metadata"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.resources, "metadata.json"
            ),
            all_matches=True,
        )

    def validate(self, validator: Validator, keywords: Any, instance: Any, schema: Any):
        validator = validator.evolve(
            schema=self._schema,
            context=validator.context.evolve(
                functions=cfnlint.helpers.FUNCTIONS,
            ),
        )
        yield from self._iter_errors(validator, instance)
