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
    shortdesc = "RecordSet HostedZoneName is a superdomain of Name"
    description = (
        "In a RecordSet, the HostedZoneName must be a superdomain of the Name being"
        " validated"
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
                if hz_name[-1] != ".":
                    yield ValidationError(
                        f"{hz_name!r} must end in a dot",
                        path=deque(["HostedZoneName"]),
                        instance=props.get("HostedZoneName"),
                    )

                if hz_name[-1] == ".":
                    hz_name = hz_name[:-1]
                hz_name = f".{hz_name}"
                if name[-1] == ".":
                    name = name[:-1]

                if hz_name not in [name, name[-len(hz_name) :]]:
                    yield ValidationError(
                        (
                            f"{props.get('Name')!r} must be a subdomain "
                            f"of {props.get('HostedZoneName')!r}"
                        ),
                        path=deque(["Name"]),
                        instance=props.get("Name"),
                    )
