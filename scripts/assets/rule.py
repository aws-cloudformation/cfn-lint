"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class EventMappingEventSourceSqs(BaseCfnSchema):
    id = "{{ rule_id }}"
    shortdesc = "Add a short description"
    description = "Add the long description"
    tags = ["resources"]
    schema_path = "{{ schema_path }}"
