"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import regex as re

from cfnlint._typing import RuleMatches
from cfnlint.helpers import REGEX_DYN_REF, REGEX_DYN_REF_SSM
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class Password(CloudFormationLintRule):
    """Check if Password Properties are properly configured"""

    id = "W2501"
    shortdesc = "Check if Password Properties are correctly configured"
    description = (
        "Password properties should not be strings and if parameter using NoEcho"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#creds"
    tags = ["parameters", "passwords", "security", "dynamic reference"]

    def match(self, cfn: Template) -> RuleMatches:
        """Check CloudFormation Password Parameters"""

        matches = []
        password_properties = [
            "AccountPassword",
            "AdminPassword",
            "ADDomainJoinPassword",
            "CrossRealmTrustPrincipalPassword",
            "KdcAdminPassword",
            "Password",
            "DbPassword",
            "MasterUserPassword",
            "PasswordParam",
        ]

        parameters = list(cfn.template.get("Parameters", {}).keys())
        fix_params = []
        for password_property in password_properties:
            # Build the list of refs
            refs = cfn.search_deep_keys(password_property)
            trees = []
            for tree in refs:
                if len(tree) > 2:
                    if tree[0] == "Resources" and tree[2] == "Properties":
                        trees.append(tree)

            for tree in trees:
                obj = tree[-1]
                if isinstance(obj, (str)):
                    if re.match(REGEX_DYN_REF, obj):
                        if re.match(REGEX_DYN_REF_SSM, obj):
                            message = (
                                "Password should use a secure dynamic reference for"
                                f" {'/'.join(map(str, tree[:-1]))}"
                            )
                            matches.append(RuleMatch(tree[:-1], message))
                    else:
                        message = (
                            "Password shouldn't be hardcoded for"
                            f" {'/'.join(map(str, tree[:-1]))}"
                        )
                        matches.append(RuleMatch(tree[:-1], message))
                elif isinstance(obj, dict):
                    if len(obj) == 1:
                        for key, value in obj.items():
                            if key == "Ref":
                                if value in parameters:
                                    param = cfn.template["Parameters"][value]
                                    if "NoEcho" in param:
                                        if not param["NoEcho"]:
                                            fix_params.append(
                                                {
                                                    "Name": value,
                                                    "Use": password_property,
                                                }
                                            )
                                    else:
                                        fix_params.append(
                                            {"Name": value, "Use": password_property}
                                        )
                    else:
                        message = (
                            "Inappropriate map found for password on"
                            f" {'/'.join(map(str, tree[:-1]))}"
                        )
                        matches.append(RuleMatch(tree[:-1], message))

        for paramname in fix_params:
            message = (
                f"Parameter {paramname['Name']} used as {paramname['Use']}, therefore"
                " NoEcho should be True"
            )
            tree = ["Parameters", paramname["Name"]]
            matches.append(RuleMatch(tree, message))
        return matches
