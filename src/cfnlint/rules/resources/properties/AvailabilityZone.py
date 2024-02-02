"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import ValidationError
from cfnlint.jsonschema._utils import ensure_list
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class AvailabilityZone(CfnLintKeyword):
    """Check Availibility Zone parameter checks"""

    id = "W3010"
    shortdesc = "Availability zone properties should not be hardcoded"
    description = "Check if an Availability Zone property is hardcoded."
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["parameters", "availabilityzone"]

    def __init__(self):
        """Init"""
        super().__init__(
            keywords=[
                "AWS::AutoScaling::AutoScalingGroup/Properties/AvailabilityZones",
                "AWS::DAX::Cluster/Properties/AvailabilityZones",
                "AWS::DMS::ReplicationInstance/Properties/AvailabilityZone",
                "AWS::EC2::Host/Properties/AvailabilityZone",
                "AWS::EC2::Instance/Properties/AvailabilityZone",
                "AWS::EC2::LaunchTemplate/LaunchTemplateData/Placement/AvailabilityZone",
                "AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/Placement/AvailabilityZone",
                "AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchTemplateConfigs/Overrides/AvailabilityZone",
                "AWS::EC2::Subnet/Properties/AvailabilityZone",
                "AWS::EC2::Volume/Properties/AvailabilityZone",
                "AWS::ElasticLoadBalancing::LoadBalancer/Properties/AvailabilityZones",
                "AWS::ElasticLoadBalancingV2::TargetGroup/Properties/Targets/AvailabilityZone",
                "AWS::EMR::Cluster/Properties/Instances/Placement/AvailabilityZone",
                "AWS::Glue::Connection/Properties/ConnectionInput/PhysicalConnectionRequirements/AvailabilityZone",
                "AWS::OpsWorks::Instance/Properties/AvailabilityZone",
                "AWS::RDS::DBCluster/Properties/AvailabilityZones",
                "AWS::RDS::DBInstance/Properties/AvailabilityZone",
            ]
        )
        self.exceptions = ["all"]

    def validate(self, validator, keywords, zones, schema):
        if not isinstance(zones, (str, list)):
            return
        
        # Skip rule if CDK
        if validator.template.is_cdk_template():
            return

        zones = ensure_list(zones)

        for zone in zones:
            if not validator.is_type(zone, "string"):
                continue

            if zone in self.exceptions:
                continue

            if any(fn in validator.context.path for fn in FUNCTIONS):
                continue

            yield ValidationError(
                f"Avoid hardcoding availability zones {zone!r}",
                rule=self,
            )
