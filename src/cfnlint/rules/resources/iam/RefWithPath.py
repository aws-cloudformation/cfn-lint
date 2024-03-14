"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule, RuleMatch


class RefWithPath(CloudFormationLintRule):
    """Check if IAM Policy Version is correct"""

    id = "E3050"
    shortdesc = "Check if REFing to a IAM resource with path set"
    description = (
        "Some resources don't support looking up the IAM resource by name. "
        "This check validates when a REF is being used and the Path is not '/'"
    )
    source_url = "https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html"
    tags = ["properties", "iam"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.resources_and_keys = {
            "AWS::CodeBuild::Project": "ServiceRole",
        }

        for resource_type in self.resources_and_keys:
            self.resource_property_types.append(resource_type)

    def check_ref(self, value, parameters, resources, path):  # pylint: disable=W0613
        """Check Ref"""
        matches = []

        iam_path = resources.get(value, {}).get("Properties", {}).get("Path")
        if not iam_path:
            return matches

        if iam_path != "/":
            message = (
                "When using a Ref to IAM resource the Path must be '/'.  Switch to"
                " GetAtt if the Path has to be '{}'."
            )
            matches.append(RuleMatch(path, message.format(iam_path)))

        return matches

    def match_resource_properties(self, properties, resourcetype, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        key = None
        if resourcetype in self.resources_and_keys:
            key = self.resources_and_keys.get(resourcetype)

        matches.extend(cfn.check_value(properties, key, path, check_ref=self.check_ref))

        return matches
