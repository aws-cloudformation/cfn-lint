"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import re
from typing import Dict, Any

import jsonschema
from jsonschema.exceptions import best_match

from cfnlint.helpers import (
    FN_PREFIX,
    PSEUDOPARAMS,
    REGEX_DYN_REF,
    REGION_PRIMARY,
    REGISTRY_SCHEMAS,
    UNCONVERTED_SUFFIXES,
    load_resource,
)
from cfnlint.jsonschema import ValidationError
from cfnlint.jsonschema.validator import create as create_validator
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER, ResourceNotFoundError
from cfnlint.template.template import Template

LOGGER = logging.getLogger("cfnlint.rules.resources.properties.JsonSchema")


class BaseJsonSchema(CloudFormationLintRule):
    """The base JSON schema package"""

    def __init__(self):
        """Init"""
        super().__init__()
        self.validator = None
        self.rules: Dict[str, str] = {}
        self.rule_set: Dict[str, str] = {}
        self.region: str = None
        self.validators: Dict[str, Any] = {}

    def json_schema_validate(self, validator, properties, path):
        matches = []
        for e in validator.iter_errors(properties):
            kwargs = {}
            if hasattr(e, "extra_args"):
                kwargs = getattr(e, "extra_args")
            e_path = path + list(e.path)
            if len(e.path) > 0:
                e_path_override = getattr(e, "path_override", None)
                if e_path_override:
                    e_path = list(e.path_override)
                else:
                    key = e.path[-1]
                    if hasattr(key, "start_mark"):
                        kwargs["location"] = (
                            key.start_mark.line,
                            key.start_mark.column,
                            key.end_mark.line,
                            key.end_mark.column,
                        )

            e_rule = None
            if hasattr(e, "rule"):
                if e.rule:
                    e_rule = e.rule
            if not e_rule:
                e_rule = self.rules.get(e.validator, self)

            matches.append(
                RuleMatch(
                    e_path,
                    e.message,
                    rule=e_rule,
                    **kwargs,
                )
            )

        return matches

    def setup_validator(self, cfn: Template):
        for name, rule_id in self.rule_set.items():
            self.rules[name] = self.child_rules.get(rule_id)

        self.validator = create_validator(
            validators=self.validators,
            cfn=cfn,
            rules=self.rules,
        )
