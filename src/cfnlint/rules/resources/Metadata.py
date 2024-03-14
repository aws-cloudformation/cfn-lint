"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import cfnlint.helpers
from cfnlint.data.schemas.other import resources
from cfnlint.jsonschema import Validator
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class Metadata(BaseJsonSchema):
    """Check Base Resource Configuration"""

    id = "E3028"
    shortdesc = "Basic CloudFormation Resource Check"
    description = (
        "Making sure the basic CloudFormation resources are properly configured"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["resources"]

    def __init__(self):
        super().__init__()
        self._schema = cfnlint.helpers.load_resource(resources, "metadata.json")

    @property
    def schema(self):
        return self._schema

    # pylint: disable=unused-argument
    def cfnresourcemetadata(self, validator: Validator, _, instance: Any, schema):
        validator = self.extend_validator(
            validator,
            self.schema,
            context=validator.context.evolve(
                functions=cfnlint.helpers.FUNCTIONS,
            ),
        )
        for err in validator.iter_errors(instance):
            if err.rule is None:
                if not err.validator.startswith("fn") and err.validator != "ref":
                    err.rule = self
            yield err
