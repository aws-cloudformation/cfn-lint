"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import cfnlint.helpers
from cfnlint.data.schemas.extensions import resource
from cfnlint.jsonschema import ValidationError
from cfnlint.jsonschema import create as create_validator
from cfnlint.jsonschema._validators import type as validator_type
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER


class Configuration(CloudFormationLintRule):
    """Check Base Resource Configuration"""

    id = "E3001"
    shortdesc = "Basic CloudFormation Resource Check"
    description = (
        "Making sure the basic CloudFormation resources are properly configured"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["resources"]

    def __init__(self):
        super().__init__()
        schema = cfnlint.helpers.load_resource(resource, "configuration.json")
        self.regions = []
        self.validator = create_validator(
            validators={
                "awsType": self._awsType,
                "type": validator_type,
            },
            cfn=None,
            rules=None,
        )(schema=schema)
        self.cfn = None

    def initialize(self, cfn):
        super().initialize(cfn)
        self.regions = cfn.regions
        self.cfn = cfn

    # pylint: disable=unused-argument
    def _awsType(self, validator, iT, instance, schema):
        resource_type = instance.get("Type")
        if not validator.is_type(resource_type, "string"):
            return

        resource_condition = instance.get("Condition")

        for region in self.regions:
            if validator.is_type(resource_condition, "string"):
                if False in self.cfn.conditions.build_scenerios_on_region(
                    resource_condition, region
                ):
                    continue
            if resource_type in PROVIDER_SCHEMA_MANAGER.get_resource_types(
                region=region
            ):
                continue
            if not resource_type.startswith(
                ("Custom::", "AWS::Serverless::")
            ) and not resource_type.endswith("::MODULE"):
                yield ValidationError(
                    f"Resource type `{resource_type}` does not exist in '{region}'"
                )

    # pylint: disable=unused-argument
    def _check_resource(self, resource_name, resource_values):
        """Check Resource"""
        matches = []

        for e in self.validator.iter_errors(instance=resource_values):
            kwargs = {}
            e_path = ["Resources", resource_name] + list(e.path)
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

            matches.append(
                RuleMatch(
                    e_path,
                    e.message,
                    **kwargs,
                )
            )

        return matches

    def match(self, cfn):
        matches = []

        resources = cfn.template.get("Resources", {})
        if not isinstance(resources, dict):
            message = "Resource not properly configured"
            matches.append(RuleMatch(["Resources"], message))
        else:
            for resource_name, resource_values in cfn.template.get(
                "Resources", {}
            ).items():
                self.logger.debug(
                    "Validating resource %s base configuration", resource_name
                )
                matches.extend(self._check_resource(resource_name, resource_values))

        return matches
