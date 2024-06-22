"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class RecordSetName(CfnLintKeyword):
    """Check if a Route53 Resoruce Records Name is valid with a HostedZoneName"""

    id = "E3041"
    shortdesc = "RecordSet HostedZoneName is a superdomain of or equal to Name"
    description = (
        "In a RecordSet, the HostedZoneName must be a superdomain of or equal to"
        " the Name being validated"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-name"
    tags = ["resource", "properties", "route53"]

    def __init__(self):
        """Init"""
        super().__init__(["Resources/AWS::Route53::RecordSet/Properties"])

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        property_sets = validator.cfn.get_object_without_conditions(
            instance, ["Name", "HostedZoneName"]
        )
        for property_set in property_sets:
            props = property_set.get("Object")
            name = props.get("Name", None)
            hz_name = props.get("HostedZoneName", None)
            if isinstance(name, str) and isinstance(hz_name, str):
                if not hz_name.endswith("."):
                    yield ValidationError(
                        f"{hz_name!r} must end in a dot",
                        path=deque(["HostedZoneName"]),
                        instance=props.get("HostedZoneName"),
                    )
                    hz_name = f"{hz_name}."

                if not name.endswith("."):
                    name = f"{name}."

                if name != hz_name and not name.endswith(f".{hz_name}"):
                    yield ValidationError(
                        (
                            f"{props.get('Name')!r} must be a subdomain "
                            f"of or equal to {props.get('HostedZoneName')!r}"
                        ),
                        path=deque(["Name"]),
                        instance=props.get("Name"),
                    )
