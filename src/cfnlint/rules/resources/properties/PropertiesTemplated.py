"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.helpers import FUNCTIONS, TEMPLATED_PROPERTY_CFN_PATHS
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class PropertiesTemplated(CfnLintKeyword):
    """Check Base Resource Configuration"""

    id = "W3002"
    shortdesc = (
        "Warn when properties are configured to only work with the package command"
    )
    description = (
        "Some properties can be configured to only work with the CloudFormation"
        "package command. Warn when this is the case so user is aware."
    )
    source_url = (
        "https://docs.aws.amazon.com/cli/latest/reference/cloudformation/package.html"
    )
    tags = ["resources"]

    def __init__(self):
        """Init"""
        super().__init__(TEMPLATED_PROPERTY_CFN_PATHS)
        # self.resource_property_types.extend(self.templated_exceptions.keys())

    def validate(self, validator, keywords, instance, schema):
        if not isinstance(instance, str):
            return

        if validator.cfn.has_serverless_transform():
            return []

        if validator.context.path[-1] in FUNCTIONS:
            return

        if not instance.startswith("s3://") and not instance.startswith("https://"):
            yield ValidationError("This code may only work with 'package' cli command")
