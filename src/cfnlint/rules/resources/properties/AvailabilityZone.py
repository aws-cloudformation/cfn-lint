"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.helpers import FUNCTIONS, ensure_list
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class AvailabilityZone(CfnLintKeyword):
    """Check Availibility Zone parameter checks"""

    id = "W3010"
    shortdesc = "Availability zone properties should not be hardcoded"
    description = "Check if an Availability Zone property is hardcoded."
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["parameters", "availabilityzone"]

    def __init__(self):
        """Init"""
        super().__init__(
            keywords=[
                "Resources/AWS::AutoScaling::AutoScalingGroup/Properties/AvailabilityZones/*",
                "Resources/AWS::DAX::Cluster/Properties/AvailabilityZones/*",
                "Resources/AWS::DMS::ReplicationInstance/Properties/AvailabilityZone",
                "Resources/AWS::EC2::Host/Properties/AvailabilityZone",
                "Resources/AWS::EC2::Instance/Properties/AvailabilityZone",
                "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/Placement/AvailabilityZone",
                "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/*/Placement/AvailabilityZone",
                "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchTemplateConfigs/*/Overrides/*/AvailabilityZone",
                "Resources/AWS::EC2::Subnet/Properties/AvailabilityZone",
                "Resources/AWS::EC2::Volume/Properties/AvailabilityZone",
                "Resources/AWS::ElasticLoadBalancing::LoadBalancer/Properties/AvailabilityZones/*",
                "Resources/AWS::ElasticLoadBalancingV2::TargetGroup/Properties/Targets/*/AvailabilityZone",
                "Resources/AWS::EMR::Cluster/Properties/Instances/Placement/AvailabilityZone",
                "Resources/AWS::Glue::Connection/Properties/ConnectionInput/PhysicalConnectionRequirements/AvailabilityZone",
                "Resources/AWS::OpsWorks::Instance/Properties/AvailabilityZone",
                "Resources/AWS::RDS::DBCluster/Properties/AvailabilityZones/*",
                "Resources/AWS::RDS::DBInstance/Properties/AvailabilityZone",
            ]
        )
        self.exceptions = ["all"]

    def validate(
        self, validator: Validator, keywords: Any, zones: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not isinstance(zones, (str, list)):
            return

        # Skip rule if CDK
        if validator.cfn.is_cdk_template():
            return

        zones = ensure_list(zones)

        for zone in zones:
            if not validator.is_type(zone, "string"):
                continue

            if zone in self.exceptions:
                continue

            if any(fn in validator.context.path.path for fn in FUNCTIONS):
                continue

            yield ValidationError(
                f"Avoid hardcoding availability zones {zone!r}",
                rule=self,
            )
