"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class Types(CloudFormationLintRule):
    """Check if Parameters are typed"""

    id = "E2002"
    shortdesc = "Parameters have appropriate type"
    description = "Making sure the parameters have a correct type"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#parmtypes"
    tags = ["parameters"]
