"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.helpers import PSEUDOPARAMS
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class RelationshipConditions(CloudFormationLintRule):
    """Check if Ref/GetAtt values are available via conditions"""

    id = "W1001"
    shortdesc = "Ref/GetAtt to resource that is available when conditions are applied"
    description = (
        "Check the Conditions that affect a Ref/GetAtt to make sure "
        "the resource being related to is available when there is a resource "
        "condition."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html"
    tags = ["conditions", "resources", "relationships", "ref", "getatt", "sub"]

    def match(self, cfn):
        """Check CloudFormation Ref/GetAtt for Conditions"""

        matches = []

        # Start with Ref checks
        ref_objs = cfn.search_deep_keys(searchText="Ref", includeGlobals=False)
        for ref_obj in ref_objs:
            value = ref_obj[-1]
            if value not in PSEUDOPARAMS:
                scenarios = cfn.is_resource_available(ref_obj, value)
                for scenario in scenarios:
                    # pylint: disable=consider-using-f-string
                    scenario_text = " and ".join(
                        [
                            'when condition "%s" is %s' % (k, v)
                            for (k, v) in scenario.items()
                        ]
                    )
                    message = (
                        'Ref to resource "{0}" that may not be available {1} at {2}'
                    )
                    matches.append(
                        RuleMatch(
                            ref_obj[:-1],
                            message.format(
                                value, scenario_text, "/".join(map(str, ref_obj[:-1]))
                            ),
                        )
                    )

        # The do GetAtt
        getatt_objs = cfn.search_deep_keys(
            searchText="Fn::GetAtt", includeGlobals=False
        )
        for getatt_obj in getatt_objs:
            value_obj = getatt_obj[-1]
            value = None
            if isinstance(value_obj, list):
                value = value_obj[0]
            elif isinstance(value_obj, str):
                value = value_obj.split(".")[0]
            if value:
                if not isinstance(value, str):
                    continue
                if value not in PSEUDOPARAMS:
                    scenarios = cfn.is_resource_available(getatt_obj, value)
                    for scenario in scenarios:
                        scenario_text = " and ".join(
                            [
                                f'when condition "{k}" is {v}'
                                for (k, v) in scenario.items()
                            ]
                        )
                        message = 'GetAtt to resource "{0}" that may not be available {1} at {2}'
                        matches.append(
                            RuleMatch(
                                getatt_obj[:-1],
                                message.format(
                                    value,
                                    scenario_text,
                                    "/".join(map(str, getatt_obj[:-1])),
                                ),
                            )
                        )

        # The do Sub
        sub_objs = cfn.search_deep_keys(searchText="Fn::Sub", includeGlobals=False)
        for sub_obj in sub_objs:
            sub_string = sub_obj[-1]
            # Filter out bad types of sub_strings.
            # Lists have two be two items and it can be just a string
            if not isinstance(sub_string, (list, str)):
                continue
            if isinstance(sub_string, str):
                sub_string = [sub_string, {}]
            if len(sub_string) != 2:
                continue
            sub_params = sub_string[1]
            string_params = cfn.get_sub_parameters(sub_string[0])

            for string_param in string_params:
                if string_param not in sub_params:
                    # deal with GetAtts by dropping everything after the .
                    string_param = string_param.split(".")[0]
                    if string_param in cfn.template.get("Resources", {}):
                        scenarios = cfn.is_resource_available(
                            sub_obj[:-1], string_param
                        )
                        for scenario in scenarios:
                            scenario_text = " and ".join(
                                [
                                    f'when condition "{k}" is {v}'
                                    for (k, v) in scenario.items()
                                ]
                            )
                            message = 'Fn::Sub to resource "{0}" that may not be available {1} at {2}'
                            matches.append(
                                RuleMatch(
                                    sub_obj[:-1],
                                    message.format(
                                        string_param,
                                        scenario_text,
                                        "/".join(map(str, sub_obj[:-1])),
                                    ),
                                )
                            )

        return matches
