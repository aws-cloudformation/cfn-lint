"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import copy
from functools import reduce  # pylint: disable=redefined-builtin

import regex as re

from cfnlint._typing import RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class SubNeeded(CloudFormationLintRule):
    """Check if a substitution string exists without a substitution function"""

    id = "E1029"
    shortdesc = "Sub is required if a variable is used in a string"
    description = (
        "If a substitution variable exists in a string but isn't wrapped with the"
        " Fn::Sub function the deployment will fail."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html"
    tags = ["functions", "sub"]

    exceptions = ["TemplateBody"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.config_definition = {"custom_excludes": {"default": "", "type": "string"}}
        self.configure()
        self.subParameterRegex = re.compile(r"(\$\{[A-Za-z0-9_:\.]+\})")

    def _match_values(self, cfnelem, path):
        """Recursively search for values matching the searchRegex"""
        values = []
        if isinstance(cfnelem, dict):
            for key in cfnelem:
                pathprop = path[:]
                pathprop.append(key)
                values.extend(self._match_values(cfnelem[key], pathprop))
        elif isinstance(cfnelem, list):
            for index, item in enumerate(cfnelem):
                pathprop = path[:]
                pathprop.append(index)
                values.extend(self._match_values(item, pathprop))
        else:
            # Leaf node
            if isinstance(cfnelem, str):  # and re.match(searchRegex, cfnelem):
                for variable in re.findall(self.subParameterRegex, cfnelem):
                    values.append(path + [variable])

        return values

    def match_values(self, cfn):
        """
        Search for values in all parts of the templates that match the searchRegex
        """
        results = []
        results.extend(self._match_values(cfn.template, []))
        # Globals are removed during a transform.  They need to be checked manually
        results.extend(self._match_values(cfn.template.get("Globals", {}), []))
        return results

    def _api_exceptions(self, value):
        """Key value exceptions"""
        parameter_search = re.compile(r"^\$\{stageVariables\..*\}$")
        return re.match(parameter_search, value)

    def _variable_custom_excluded(self, value):
        """User-defined exceptions for variables, anywhere in the file"""
        custom_excludes = self.config["custom_excludes"]
        if custom_excludes:
            custom_search = re.compile(custom_excludes)
            return re.match(custom_search, value)
        return False

    def match(self, cfn: Template) -> RuleMatches:
        matches = []

        refs = cfn.get_valid_refs()
        getatts = cfn.get_valid_getatts()

        # Get a list of paths to every leaf node
        # string containing at least one ${parameter}
        parameter_string_paths = self.match_values(cfn)
        # We want to search all of the paths to check if each
        # one contains an 'Fn::Sub'
        for parameter_string_path in parameter_string_paths:
            # Get variable
            var = parameter_string_path[-1]

            # Step Function State Machine has a Definition Substitution
            # that allows usage of special variables outside of a !Sub
            # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-definitionsubstitutions.html

            if "DefinitionString" in parameter_string_path:
                modified_parameter_string_path = copy.copy(parameter_string_path)
                index = parameter_string_path.index("DefinitionString")
                modified_parameter_string_path[index] = "DefinitionSubstitutions"
                modified_parameter_string_path = modified_parameter_string_path[
                    : index + 1
                ]
                modified_parameter_string_path.append(var[2:-1])
                if reduce(
                    lambda c, k: c.get(k, {}),
                    modified_parameter_string_path,
                    cfn.template,
                ):
                    continue

            # Exclude variables that match custom exclude filters, if configured
            # (for third-party tools that pre-process templates
            # before uploading them to AWS)
            if self._variable_custom_excluded(var):
                continue

            # Exclude literals (https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html)
            if var.startswith("${!"):
                continue

            var_stripped = var[2:-1].strip()
            # If we didn't find an 'Fn::Sub' it means a string
            # containing a ${parameter} may not be evaluated correctly
            if (
                "Fn::Sub" not in parameter_string_path
                and parameter_string_path[-2] not in self.exceptions
            ):
                try:
                    if (
                        var_stripped in refs
                        or getatts.match(cfn.regions[0], var_stripped)
                    ) or "DefinitionString" in parameter_string_path:
                        # Remove the last item (the variable) to prevent
                        # multiple errors on 1 line errors
                        path = parameter_string_path[:-1]
                        message = (
                            f'Found an embedded parameter "{var}" outside of an'
                            f' "Fn::Sub" at {"/".join(map(str, path))}'
                        )
                        matches.append(RuleMatch(path, message))
                except (ValueError, TypeError):
                    if "DefinitionString" in parameter_string_path:
                        path = parameter_string_path[:-1]
                        message = (
                            f'Found an embedded parameter "{var}" outside of an'
                            f' "Fn::Sub" at {"/".join(map(str, path))}'
                        )
                        matches.append(RuleMatch(path, message))

        return matches
