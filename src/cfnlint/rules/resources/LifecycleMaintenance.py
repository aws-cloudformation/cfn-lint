"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class ResourceLifecycleMaintenance(CloudFormationLintRule):
    id = "W3697"
    shortdesc = "Resource type is from a service in maintenance mode"
    description = (
        "Checks if a resource type belongs to an AWS service that is "
        "in maintenance mode with no new features"
    )
    source_url = (
        "https://docs.aws.amazon.com/general/latest/gr/maintenance_services.html"
    )
    tags = ["resources", "lifecycle"]
