"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Union

from cfnlint.helpers import VALID_PARAMETER_TYPES_LIST
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import GetAtts, Template


class Join(CloudFormationLintRule):
    """Check if Join values are correct"""

    id = "E1022"
    shortdesc = "Join validation of parameters"
    description = "Making sure the join function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-join.html"
    tags = ["functions", "join"]

    _intrinsic_types = {
        "Fn::Base64": {
            "ReturnTypes": ["Singular"],
        },
        "Fn::Cidr": {
            "ReturnTypes": ["List"],
        },
        "Fn::FindInMap": {
            "ReturnTypes": ["Singular", "List"],
        },
        "Fn::GetAZs": {
            "ReturnTypes": ["List"],
        },
        "Fn::GetAtt": {
            "ReturnTypes": ["Singular", "List"],
        },
        "Fn::If": {
            "ReturnTypes": ["Singular", "List"],
        },
        "Fn::ImportValue": {
            "ReturnTypes": ["Singular"],
        },
        "Fn::Join": {
            "ReturnTypes": ["Singular"],
        },
        "Fn::Select": {
            "ReturnTypes": ["Singular", "List"],
        },
        "Fn::Split": {
            "ReturnTypes": ["List"],
        },
        "Fn::Sub": {
            "ReturnTypes": ["Singular"],
        },
        "Fn::Transform": {
            "ReturnTypes": [],
        },
        "Ref": {
            "ReturnTypes": ["Singular", "List"],
        },
    }

    def __init__(self):
        """Initialize the rule"""
        super().__init__()
        self.list_supported_functions = []
        self.singular_supported_functions = []
        for intrinsic_type, intrinsic_value in self._intrinsic_types.items():
            if "List" in intrinsic_value.get("ReturnTypes", []):
                self.list_supported_functions.append(intrinsic_type)
            if "Singular" in intrinsic_value.get("ReturnTypes", []):
                self.singular_supported_functions.append(intrinsic_type)

    def _get_parameters(self, cfn):
        """Get all Parameter Names"""
        results = {}
        parameters = cfn.template.get("Parameters", {})
        if isinstance(parameters, dict):
            for param_name, param_values in parameters.items():
                # This rule isn't here to check the Types but we need
                # something valid if it doesn't exist
                results[param_name] = param_values.get("Type", "String")

        return results

    def _normalize_getatt(self, getatt):
        """Normalize getatt into an array"""
        if isinstance(getatt, str):
            return getatt.split(".", 1)
        return getatt

    def _is_ref_a_list(self, parameter, template_parameters):
        """Is a Ref a list"""
        list_params = [
            "AWS::NotificationARNs",
        ]

        if parameter in template_parameters:
            if template_parameters.get(parameter) in VALID_PARAMETER_TYPES_LIST:
                return True
        if parameter in list_params:
            return True
        return False

    def _is_getatt_a_list(self, parameter, get_atts: GetAtts) -> Union[bool, None]:
        """Is a GetAtt a List"""
        try:
            getatt = get_atts.match("us-east-1", parameter)
            if getatt.type == "array" or getatt.type is None:
                return True
            return False
        except:  # ruff: noqa: E722
            # this means we can't match the get_att.  This is
            # covered by another rule
            return None

    def _match_string_objs(self, join_string_objs, cfn: Template, path):
        """Check join list"""

        matches = []

        template_parameters = self._get_parameters(cfn)
        get_atts = cfn.get_valid_getatts()

        if isinstance(join_string_objs, dict):
            if len(join_string_objs) == 1:
                for key, value in join_string_objs.items():
                    if key not in self.list_supported_functions:
                        message = "Fn::Join unsupported function for {0}"
                        matches.append(
                            RuleMatch(path, message.format("/".join(map(str, path))))
                        )
                    elif key in ["Ref"]:
                        if not self._is_ref_a_list(value, template_parameters):
                            message = "Fn::Join must use a list at {0}"
                            matches.append(
                                RuleMatch(
                                    path, message.format("/".join(map(str, path)))
                                )
                            )
                    elif key in ["Fn::GetAtt"]:
                        is_a_list = self._is_getatt_a_list(
                            self._normalize_getatt(value), get_atts
                        )
                        if is_a_list is not None and not is_a_list:
                            message = "Fn::Join must use a list at {0}"
                            matches.append(
                                RuleMatch(
                                    path, message.format("/".join(map(str, path)))
                                )
                            )
            else:
                message = "Join list of values should be singular for {0}"
                matches.append(
                    RuleMatch(path, message.format("/".join(map(str, path))))
                )
        elif not isinstance(join_string_objs, list):
            message = "Join list of values for {0}"
            matches.append(RuleMatch(path, message.format("/".join(map(str, path)))))
        else:
            for string_obj in join_string_objs:
                if isinstance(string_obj, dict):
                    if len(string_obj) == 1:
                        for key, value in string_obj.items():
                            if key not in self.singular_supported_functions:
                                message = "Join unsupported function for {0}"
                                matches.append(
                                    RuleMatch(
                                        path, message.format("/".join(map(str, path)))
                                    )
                                )
                            elif key in ["Ref"]:
                                if self._is_ref_a_list(value, template_parameters):
                                    message = "Fn::Join must not be a list at {0}"
                                    matches.append(
                                        RuleMatch(
                                            path,
                                            message.format("/".join(map(str, path))),
                                        )
                                    )
                            elif key in ["Fn::GetAtt"]:
                                is_a_list = self._is_getatt_a_list(
                                    self._normalize_getatt(value), get_atts
                                )
                                if is_a_list is not None and is_a_list:
                                    message = "Fn::Join must not be a list at {0}"
                                    matches.append(
                                        RuleMatch(
                                            path,
                                            message.format("/".join(map(str, path))),
                                        )
                                    )
                    else:
                        message = "Join list of values should be singular for {0}"
                        matches.append(
                            RuleMatch(path, message.format("/".join(map(str, path))))
                        )
                elif not isinstance(string_obj, str):
                    message = "Join list of singular function or string for {0}"
                    matches.append(
                        RuleMatch(path, message.format("/".join(map(str, path))))
                    )

        return matches

    def match(self, cfn: Template):
        matches = []

        join_objs = cfn.search_deep_keys("Fn::Join")

        for join_obj in join_objs:
            join_value_obj = join_obj[-1]
            path = join_obj[:-1]
            if isinstance(join_value_obj, list):
                if len(join_value_obj) == 2:
                    join_string = join_value_obj[0]
                    join_string_objs = join_value_obj[1]
                    if not isinstance(join_string, str):
                        message = "Join string has to be of type string for {0}"
                        matches.append(
                            RuleMatch(path, message.format("/".join(map(str, path))))
                        )
                    matches.extend(self._match_string_objs(join_string_objs, cfn, path))
                else:
                    message = "Join should be an array of 2 for {0}"
                    matches.append(
                        RuleMatch(path, message.format("/".join(map(str, path))))
                    )
            else:
                message = "Join should be an array of 2 for {0}"
                matches.append(
                    RuleMatch(path, message.format("/".join(map(str, path))))
                )

        return matches
