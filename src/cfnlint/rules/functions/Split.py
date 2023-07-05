"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json

import regex as re

from cfnlint.helpers import REGEX_DYN_REF_SSM
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class Split(CloudFormationLintRule):
    """Check if Split values are correct"""

    id = "E1018"
    shortdesc = "Split validation of parameters"
    description = "Making sure the split function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-split.html"
    tags = ["functions", "split"]
    supported_functions = [
        "Fn::Base64",
        "Fn::FindInMap",
        "Fn::GetAZs",
        "Fn::GetAtt",
        "Fn::If",
        "Fn::ImportValue",
        "Fn::Join",
        "Fn::Select",
        "Fn::Sub",
        "Ref",
        "Fn::ToJsonString",
    ]

    def _test_delimiter(self, delimiter, path):
        matches = []
        if not isinstance(delimiter, str):
            message = "Split delimiter has to be of type string for {0}"
            matches.append(RuleMatch(path, message.format("/".join(map(str, path)))))
        return matches

    def _check_dyn_ref_value(self, value, path):
        """Chec item type"""
        matches = []
        if isinstance(value, str):
            if re.match(REGEX_DYN_REF_SSM, value):
                message = f'Fn::Split does not support dynamic references at {"/".join(map(str, path[:]))}'
                matches.append(RuleMatch(path[:], message))

        return matches

    def _test_string(self, s, path):
        matches = []
        matches.extend(self._check_dyn_ref_value(json.dumps(s), path[:]))
        if isinstance(s, dict):
            if len(s) == 1:
                for key, _ in s.items():
                    if key not in self.supported_functions:
                        message = "Fn::Split doesn't support the function {0} at {1}"
                        matches.append(
                            RuleMatch(
                                path + [key],
                                message.format(key, "/".join(map(str, path))),
                            )
                        )
            else:
                message = "Split list of singular function or string for {0}"
                matches.append(
                    RuleMatch(path, message.format("/".join(map(str, path))))
                )
        elif not isinstance(s, str):
            message = "Split has to be of type string or valid function for {0}"
            matches.append(RuleMatch(path, message.format("/".join(map(str, path)))))
        return matches

    def _test_split(self, split_obj, path):
        matches = []
        if not isinstance(split_obj, list):
            message = "Split should be an array of 2 for {0}"
            matches.append(RuleMatch(path, message.format("/".join(map(str, path)))))
            return matches

        if len(split_obj) != 2:
            message = "Split should be an array of 2 for {0}"
            matches.append(RuleMatch(path, message.format("/".join(map(str, path)))))
            return matches

        split_delimiter = split_obj[0]
        split_string = split_obj[1]
        matches.extend(self._test_delimiter(split_delimiter, path[:] + [0]))
        matches.extend(self._test_string(split_string, path[:] + [1]))

        return matches

    def match(self, cfn):
        matches = []

        split_objs = cfn.search_deep_keys("Fn::Split")

        for split_obj in split_objs:
            split_value_obj = split_obj[-1]
            tree = split_obj[:-1]
            matches.extend(self._test_split(split_value_obj, tree[:]))

        return matches
