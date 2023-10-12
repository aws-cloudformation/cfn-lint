"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule, RuleMatch


class AccessControlObsolete(CloudFormationLintRule):
    """Check if the S3 Bucket Access Controls are configured"""

    id = "W3045"
    shortdesc = "Controlling access to an S3 bucket should be done with bucket policies"
    description = (
        "Nearly all access control configurations can be more successfully achieved with "
        "bucket policies. Consider using bucket policies instead of access control."
    )
    source_url = "https://docs.aws.amazon.com/AmazonS3/latest/userguide/about-object-ownership.html"
    tags = ["resources", "s3"]

    def __init__(self):
        super().__init__()
        self.resource_property_types.append("AWS::S3::Bucket")

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        for scenario in cfn.get_object_without_conditions(
            properties, ["AccessControl"]
        ):
            props = scenario.get("Object")

            access_control = props.get("AccessControl")
            if access_control:
                matches.append(
                    RuleMatch(
                        path + ["AccessControl"],
                        "Consider using AWS::S3::BucketPolicy instead of AccessControl",
                    )
                )

        return matches
