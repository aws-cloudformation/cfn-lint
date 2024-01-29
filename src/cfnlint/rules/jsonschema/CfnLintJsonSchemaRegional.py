"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations
import pathlib
from typing import Any, Sequence
from cfnlint.jsonschema._utils import Unset

from cfnlint.helpers import load_plugins, load_resource
from cfnlint.jsonschema import ValidationError
from cfnlint.jsonschema._validators import type
from cfnlint.jsonschema.exceptions import best_match
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema
from cfnlint.jsonschema._utils import ensure_list
from cfnlint.rules import CloudFormationLintRule


class CfnLintJsonSchemaRegional(CfnLintJsonSchema):
    
    def _iter_errors(self, validator, keywords, instance, schema):
        for region in validator.context.regions:
            region_validator = validator.evolve(
                context=validator.context.evolve(regions=[region])
            )
            yield from super()._iter_errors(region_validator, keywords, instance, self.schema.get(region, True))
