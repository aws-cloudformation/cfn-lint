"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import regex as re

from cfnlint.helpers import RESOURCE_SPECS
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class AllowedPattern(CloudFormationLintRule):
    """Check if properties have a valid value"""

    id = "E3031"
    shortdesc = "Check if property values adhere to a specific pattern"
    description = "Check if properties have a valid value in case of a pattern (Regular Expression)"
    source_url = "https://github.com/awslabs/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedpattern"
    tags = ["resources", "property", "allowed pattern", "regex"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.config_definition = {
            "exceptions": {
                "default": [],
                "type": "list",
                "itemtype": "string",
            }
        }
        self.configure()

    def initialize(self, cfn):
        """Initialize the rule"""
        for resource_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get(
            "ResourceTypes"
        ):
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get(
            "PropertyTypes"
        ):
            self.resource_sub_property_types.append(property_type_spec)

    def check_value(self, value, path, property_name, **kwargs):
        """Check Value"""
        matches = []

        # Get the Allowed Pattern Regex
        value_pattern_regex = kwargs.get("value_specs", {}).get(
            "AllowedPatternRegex", {}
        )
        # Get the "Human Readable" version for the error message. Optional, if not specified,
        # the RegEx itself is used.
        value_pattern = kwargs.get("value_specs", {}).get(
            "AllowedPattern", value_pattern_regex
        )

        if isinstance(value, (int, float)):
            value = str(value)

        if isinstance(value, str):
            if value_pattern_regex:
                regex = re.compile(value_pattern_regex, re.ASCII)

                # Ignore values with dynamic references. Simple check to prevent false-positives
                # See: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html
                if "{{resolve:" not in value:
                    if not regex.match(value):
                        for exception in self.config.get("exceptions"):
                            exception_regex = re.compile(exception)
                            if exception_regex.match(value):
                                return matches
                        full_path = "/".join(str(x) for x in path)

                        message = "{} contains invalid characters (Pattern: {}) at {}"
                        matches.append(
                            RuleMatch(
                                path,
                                message.format(property_name, value_pattern, full_path),
                            )
                        )

        return matches

    def check(self, cfn, properties, property_specs, path):
        """Check itself"""
        matches = []
        for p_value, p_path in properties.items_safe(path[:]):
            for prop in p_value:
                if prop in property_specs:
                    value = property_specs.get(prop).get("Value", {})
                    if value:
                        value_type = value.get("ValueType", "")
                        property_type = property_specs.get(prop).get("Type")
                        value_specs = (
                            RESOURCE_SPECS.get(cfn.regions[0])
                            .get("ValueTypes")
                            .get(value_type, {})
                        )
                        if value_specs == "CACHED":
                            value_specs = (
                                RESOURCE_SPECS.get("us-east-1")
                                .get("ValueTypes")
                                .get(value_type, {})
                            )
                        matches.extend(
                            cfn.check_value(
                                p_value,
                                prop,
                                p_path,
                                check_value=self.check_value,
                                value_specs=value_specs,
                                cfn=cfn,
                                property_type=property_type,
                                property_name=prop,
                            )
                        )
        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = []

        specs = (
            RESOURCE_SPECS.get(cfn.regions[0])
            .get("PropertyTypes")
            .get(property_type, {})
            .get("Properties", {})
        )
        matches.extend(self.check(cfn, properties, specs, path))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        specs = (
            RESOURCE_SPECS.get(cfn.regions[0])
            .get("ResourceTypes")
            .get(resource_type, {})
            .get("Properties", {})
        )
        matches.extend(self.check(cfn, properties, specs, path))

        return matches
