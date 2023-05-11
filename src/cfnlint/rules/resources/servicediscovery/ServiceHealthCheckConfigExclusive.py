"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class ServiceHealthCheckConfigExclusive(BaseCfnSchema):
    id = "E3676"
    shortdesc = (
        "Validate service discover health check config properties cannot be "
        "used together"
    )
    description = (
        "When you specify 'HealthCheckConfig' do not specify 'HealthCheckCustomConfig'"
    )
    tags = ["resources"]
    schema_path = "aws_servicediscovery_service/healthcheckconfig_exclusive"
