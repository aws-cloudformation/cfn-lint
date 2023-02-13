"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class AvailabilityZone(CloudFormationLintRule):
    """Check Availibility Zone parameter checks"""

    id = "W3010"
    shortdesc = "Availability zone properties should not be hardcoded"
    description = "Check if an Availability Zone property is hardcoded."
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["parameters", "availabilityzone"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.exceptions = ["all"]

    def availabilityzone(self, validator, aZ, zone, schema):
        if not validator.is_type(zone, "string"):
            return

        if zone in self.exceptions:
            return

        yield ValidationError(
            f"Avoid hardcoding availability zones '{zone}'",
            rule=self,
        )

    def availabilityzones(self, validator, aZ, zones, schema):
        if not validator.is_type(zones, "array"):
            return

        for zone in zones:
            yield from self.availabilityzone(validator, aZ, zone, schema)
