"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import defaultdict
from typing import Any

import cfnlint.helpers
from cfnlint._typing import Path, RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class RouteTableAssociation(CloudFormationLintRule):
    """Check only one route table association defined per subnet"""

    id = "E3022"
    shortdesc = "Resource SubnetRouteTableAssociation Properties"
    description = "Validate there is only one SubnetRouteTableAssociation per subnet"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html"
    tags = ["resources", "ec2", "subnet", "route table"]

    def __init__(self) -> None:
        super().__init__()
        self.resource_values: dict[str, list[str]] = {}
        self.associated_resources: defaultdict[Any, list[str]] = defaultdict(list)

    def initialize(self, cfn: Template) -> None:
        self.resource_values = {}
        self.associated_resources = defaultdict(list)

    def get_values(self, subnetid, resource_condition, property_condition):
        """Get string literal(s) from value of SubnetId"""
        values = []
        if isinstance(subnetid, dict):
            if len(subnetid) == 1:
                for key, value in subnetid.items():
                    if key == cfnlint.helpers.FUNCTION_IF:
                        if isinstance(value, list):
                            if len(value) == 3:
                                property_condition = value[0]
                                values.extend(
                                    self.get_values(
                                        value[1], resource_condition, property_condition
                                    )
                                )
                                values.extend(
                                    self.get_values(
                                        value[2], resource_condition, property_condition
                                    )
                                )
                    if key == "Ref":
                        values.extend(
                            self.get_values(
                                value, resource_condition, property_condition
                            )
                        )
                    if key == "Fn::GetAtt":
                        if isinstance(value[1], (str)):
                            sub_value = ".".join(value)
                            values.append(
                                (resource_condition, property_condition, sub_value)
                            )
        else:
            values.append((resource_condition, property_condition, subnetid))
        return values

    def check_values(self, subnetid, resource_condition, resource_name):
        """Check subnet value is not associated with other route tables"""
        property_condition = None
        values = self.get_values(subnetid, resource_condition, property_condition)
        self.resource_values[resource_name] = values
        for value in values:
            self.associated_resources[value].append(resource_name)

    def match(self, cfn: Template) -> RuleMatches:
        """Check SubnetRouteTableAssociation Resource Properties"""

        matches = []
        resources = cfn.get_resources(["AWS::EC2::SubnetRouteTableAssociation"])
        for resource_name, resource in resources.items():
            properties = resource.get("Properties")
            if properties:
                resource_condition = resource.get("Condition")
                subnetid = properties.get("SubnetId")
                self.check_values(subnetid, resource_condition, resource_name)
        for resource_name, resource_values in self.resource_values.items():
            for value in resource_values:
                bare_value = (None, None, value[2])
                other_resources: list[str] = []

                if len(self.associated_resources[value]) > 1:
                    for associated_name in self.associated_resources[value]:
                        if associated_name != resource_name:
                            other_resources.append(associated_name)

                if value != bare_value and self.associated_resources[bare_value]:
                    other_resources.extend(self.associated_resources[bare_value])

                if other_resources:
                    path: Path = ["Resources", resource_name, "Properties", "SubnetId"]
                    message = "SubnetId in {0} is also associated with {1}"
                    matches.append(
                        RuleMatch(
                            path,
                            message.format(resource_name, ", ".join(other_resources)),
                        )
                    )

        return matches
