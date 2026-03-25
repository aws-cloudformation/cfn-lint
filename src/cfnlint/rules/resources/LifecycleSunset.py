"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class ResourceLifecycleSunset(CloudFormationLintRule):
    id = "W3696"
    shortdesc = "Resource type is from a service that is sunsetting"
    description = (
        "Checks if a resource type belongs to an AWS service that is "
        "in the sunset phase and will be shut down"
    )
    source_url = "https://docs.aws.amazon.com/general/latest/gr/sunset_services.html"
    tags = ["resources", "lifecycle"]
