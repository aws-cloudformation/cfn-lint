"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule, RuleMatch


class AccessControlOwnership(CloudFormationLintRule):
    """Check if the S3 Bucket Access Controls are set with Ownership rules"""

    id = "E3045"
    shortdesc = "Validate AccessControl are set with OwnershipControls"
    description = (
        "When using AccessControl other than private you must also "
        "configure OwnershipControls. The default is bucket owner "
        "enforced which disables ACLs."
    )
    source_url = "https://docs.aws.amazon.com/AmazonS3/latest/userguide/about-object-ownership.html"
    tags = ["resources", "s3"]

    def __init__(self):
        super().__init__()
        self.resource_property_types.append("AWS::S3::Bucket")
        self.valid_access_controls = [
            "Private",
            "BucketOwnerFullControl",
            "BucketOwnerRead",
        ]

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        for scenario in cfn.get_object_without_conditions(
            properties, ["AccessControl", "OwnershipControls"]
        ):
            props = scenario.get("Object")

            access_controls = props.get("AccessControl")
            if not access_controls or access_controls in self.valid_access_controls:
                continue

            ownership_controls = props.get("OwnershipControls")
            if ownership_controls:
                rules = ownership_controls.get("Rules", [])
                if not isinstance(rules, list):
                    continue
                if len(ownership_controls.get("Rules", [])) > 0:
                    continue

            matches.append(
                RuleMatch(
                    path + ["AccessControl"],
                    "A bucket with AccessControl set should also have OwnershipControl configured",
                )
            )

        return matches
