"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class Select(CloudFormationLintRule):
    """Check if Select values are correct"""

    id = "E1017"
    shortdesc = "Select validation of parameters"
    description = "Making sure the Select function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-select.html"
    tags = ["functions", "select"]
    supported_functions = [
        "Fn::FindInMap",
        "Fn::GetAtt",
        "Fn::GetAZs",
        "Fn::If",
        "Fn::Split",
        "Fn::Cidr",
        "Ref",
    ]

    def _test_index_obj(self, index_obj, path):
        matches = []
        if isinstance(index_obj, dict):
            if len(index_obj) == 1:
                for index_key, _ in index_obj.items():
                    if index_key not in [
                        "Ref",
                        "Fn::FindInMap",
                        "Fn::Select",
                    ]:
                        message = "Select index should be an Integer or a function Ref, Fn::FindInMap, or Fn::Select for {0}"
                        matches.append(
                            RuleMatch(
                                path,
                                message.format("/".join(map(str, path))),
                            )
                        )
            else:
                message = "Select index should be an Integer or a function Ref, Fn::FindInMap, or Fn::Select for {0}"
                matches.append(
                    RuleMatch(
                        path,
                        message.format("/".join(map(str, path))),
                    )
                )
        elif not isinstance(index_obj, int):
            try:
                int(index_obj)
            except (ValueError, TypeError):
                message = "Select index should be an Integer or a function of Ref, Fn::FindInMap, or Fn::Select for {0}"
                matches.append(
                    RuleMatch(path, message.format("/".join(map(str, path))))
                )

        return matches

    def _test_list_obj(self, list_obj, path):
        matches = []
        if isinstance(list_obj, dict):
            if len(list_obj) == 1:
                for key, _ in list_obj.items():
                    if key not in self.supported_functions:
                        message = "Select should use a supported function of {0}"
                        matches.append(
                            RuleMatch(
                                path,
                                message.format(
                                    ", ".join(map(str, self.supported_functions))
                                ),
                            )
                        )
            else:
                message = "Select should use a supported function of {0}"
                matches.append(
                    RuleMatch(
                        path,
                        message.format(", ".join(map(str, self.supported_functions))),
                    )
                )
        elif not isinstance(list_obj, list):
            message = "Select should be an array of values for {0}"
            matches.append(RuleMatch(path, message.format("/".join(map(str, path)))))

        return matches

    def _test_select_obj(self, select_obj, path):
        matches = []
        if not isinstance(select_obj, list):
            message = "Select should be a list of 2 elements for {0}"
            matches.append(RuleMatch(path, message.format("/".join(map(str, path)))))
            return matches
        if len(select_obj) != 2:
            message = "Select should be a list of 2 elements for {0}"
            matches.append(RuleMatch(path, message.format("/".join(map(str, path)))))
            return matches

        index_obj = select_obj[0]
        list_of_objs = select_obj[1]
        matches.extend(self._test_index_obj(index_obj, path[:] + [0]))
        matches.extend(self._test_list_obj(list_of_objs, path[:] + [1]))

        return matches

    def match(self, cfn):
        matches = []

        select_objs = cfn.search_deep_keys("Fn::Select")

        for select_obj in select_objs:
            select_value_obj = select_obj[-1]
            tree = select_obj[:-1]
            matches.extend(self._test_select_obj(select_value_obj, tree[:]))

        return matches
