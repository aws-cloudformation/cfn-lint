"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.helpers
from cfnlint.context.context import create_context_for_resources
from cfnlint.data.schemas.other import resources
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules import RuleMatch
from cfnlint.rules.jsonschema.base import BaseJsonSchema
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER


class Configuration(BaseJsonSchema):
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
        self.schema = cfnlint.helpers.load_resource(resources, "configuration.json")
        self.regions = []
        self.cfn = None
        self.validators = {
            "awsType": self.awsType,
        }

    def initialize(self, cfn):
        super().initialize(cfn)
        self.regions = cfn.regions
        self.cfn = cfn

    # pylint: disable=unused-argument
    def awsType(self, validator, iT, instance, schema):
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
    def _check_resource(self, validator, resources):
        """Check Resource"""
        matches = []
        for e in validator.iter_errors(instance=resources):
            kwargs = {}
            e_path = ["Resources"] + list(e.path)
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
        validator = self.setup_validator(
            CfnTemplateValidator,
            self.schema,
            context=create_context_for_resources(cfn, cfn.regions[0]),
        )
        matches.extend(self._check_resource(validator, resources))

        return matches
