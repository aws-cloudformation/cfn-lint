"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re

import cfnlint.helpers
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class DynamicReferenceSecureString(CloudFormationLintRule):
    """Check if Dynamic Reference Secure Strings are only used in the correct locations"""

    id = "E1027"
    shortdesc = "Check dynamic references secure strings are in supported locations"
    description = (
        "Dynamic References Secure Strings are only supported for a small set of resource properties.  "
        "Validate that they are being used in the correct location when checking values "
        "and Fn::Sub in resource properties. Currently doesn't check outputs, maps, conditions, "
        "parameters, and descriptions."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html"
    tags = ["functions", "dynamic reference"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.property_specs = []
        self.resource_specs = []
        self.exceptions = {
            "AWS::DirectoryService::MicrosoftAD": "Password",
            "AWS::DirectoryService::SimpleAD": "Password",
            "AWS::ElastiCache::ReplicationGroup": "AuthToken",
            "AWS::IAM::User": {
                "LoginProfile": "Password",
            },
            "AWS::KinesisFirehose::DeliveryStream": {
                "RedshiftDestinationConfiguration": "Password",
            },
            "AWS::OpsWorks::App": {
                "AppSource": "Password",
            },
            "AWS::OpsWorks::Stack": {
                "RdsDbInstances": "DbPassword",
                "CustomCookbooksSource": "Password",
            },
            "AWS::RDS::DBCluster": "MasterUserPassword",
            "AWS::RDS::DBInstance": "MasterUserPassword",
            "AWS::Redshift::Cluster": "MasterUserPassword",
        }

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
                for variable in re.findall(
                    cfnlint.helpers.REGEX_DYN_REF_SSM_SECURE, cfnelem
                ):
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

    def _test_list(self, parent_list, child_list):
        result = False
        for idx in range(len(parent_list) - len(child_list) + 1):
            if parent_list[idx : idx + len(child_list)] == child_list:
                result = True
                break

        return result

    def match(self, cfn):
        matches = []
        paths = self.match_values(cfn)

        for path in paths:
            message = (
                "Dynamic reference secure strings are not supported at this location"
            )
            if path[0] == "Resources":
                resource_type = (
                    cfn.template.get("Resources", {}).get(path[1]).get("Type")
                )
                exception = self.exceptions.get(resource_type)
                if not exception:
                    matches.append(RuleMatch(path[:-1], message=message))
                    continue

                if isinstance(exception, dict):
                    matched = False
                    for k, v in exception.items():
                        if self._test_list(path, ["Properties", k]):
                            if v in path:
                                matched = True
                    if not matched:
                        matches.append(RuleMatch(path[:-1], message=message))
                    continue
                if not self._test_list(path, ["Properties", exception]):
                    matches.append(RuleMatch(path[:-1], message=message))

            else:
                matches.append(RuleMatch(path[:-1], message=message))

        return matches
