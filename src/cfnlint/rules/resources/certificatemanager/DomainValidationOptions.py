"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class DomainValidationOptions(CfnLintKeyword):
    """Check if a certificate's domain validation options are set up correctly"""

    id = "E3503"
    shortdesc = "ValidationDomain is superdomain of DomainName"
    description = (
        "In ValidationDomainOptions, the ValidationDomain must be a superdomain of the"
        " DomainName being validated"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-certificatemanager-certificate-domainvalidationoption.html#cfn-certificatemanager-certificate-domainvalidationoption-validationdomain"
    tags = [
        "certificate",
        "certificatemanager",
        "domainvalidationoptions",
        "validationdomain",
    ]

    def __init__(self):
        """Init"""
        super().__init__(
            [
                "Resources/AWS::CertificateManager::Certificate/Properties/DomainValidationOptions/*"
            ]
        )

    def validate(
        self, validator: Validator, _, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not isinstance(instance, dict):
            return

        property_sets = validator.cfn.get_object_without_conditions(instance)
        for property_set in property_sets:
            properties = property_set.get("Object")
            domain_name = properties.get("DomainName", None)
            validation_domain = properties.get("ValidationDomain", None)
            if isinstance(domain_name, str) and isinstance(validation_domain, str):
                if domain_name == validation_domain:
                    continue

                if not domain_name.endswith("." + validation_domain):
                    yield ValidationError(
                        (
                            f"{validation_domain!r} must be a "
                            f"superdomain of {domain_name!r}"
                        ),
                        path=deque(["DomainName"]),
                        instance=domain_name,
                    )
