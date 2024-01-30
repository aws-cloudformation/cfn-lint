"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import cfnlint.helpers
from cfnlint.data.schemas.other import resources
from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import Validator
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class Configuration(BaseJsonSchema):
    """Check Update Policy Configuration"""

    id = "E3016"
    shortdesc = "Check the configuration of a resources UpdatePolicy"
    description = "Make sure a resources UpdatePolicy is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-updatepolicy.html"
    tags = ["resources", "updatepolicy"]

    def __init__(self) -> None:
        super().__init__()
        self._schema = cfnlint.helpers.load_resource(resources, "update_policy.json")

    @property
    def schema(self):
        return self._schema

    # pylint: disable=unused-argument
    def cfnresourceupdatepolicy(self, validator: Validator, uP, instance: Any, schema):
        validator = validator.evolve(
            context=validator.context.evolve(functions=FUNCTIONS)
        )
        yield from self.validate(validator, uP, instance, schema)
