"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any, Dict, List

from cfnlint._typing import Path, RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class ZipPackageRequiredProperties(CloudFormationLintRule):
    id = "W2533"
    shortdesc = (
        "Check required properties for Lambda if the deployment package is a .zip file"
    )
    description = (
        "When the package type is Zip, "
        "you must also specify the `handler` and `runtime` properties."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html"
    tags = ["resources", "lambda"]

    def _check_lambda_function(
        self,
        cfn: Template,
        resource_name: str,
        properties: Dict[str, Any],
        required_properties: List[str],
    ) -> RuleMatches:
        """Check AWS::Lambda::Function for missing required properties."""
        matches: RuleMatches = []

        for scenario in cfn.get_object_without_conditions(
            properties, ["PackageType", "Code", "Handler", "Runtime"]
        ):
            props = scenario.get("Object")
            path: Path = ["Resources", resource_name, "Properties"]

            # check is zip deployment
            is_zip_deployment = True
            code = props.get("Code")

            if props.get("PackageType") == "Zip":
                path.append("PackageType")
            elif isinstance(code, dict) and (code.get("ZipFile") or code.get("S3Key")):
                path.append("Code")
            else:
                is_zip_deployment = False

            if not is_zip_deployment:
                continue

            # check required properties for zip deployment
            missing_properties = []
            for p in required_properties:
                if props.get(p) is None:
                    missing_properties.append(p)

            if len(missing_properties) > 0:
                message = "Properties {0} missing for zip file deployment at {1}"
                matches.append(
                    RuleMatch(
                        path,
                        message.format(
                            missing_properties,
                            "/".join(
                                map(str, ["Resources", resource_name, "Properties"])
                            ),
                        ),
                    )
                )

        return matches

    def _check_serverless_function(
        self,
        cfn: Template,
        resource_name: str,
        properties: Dict[str, Any],
        required_properties: List[str],
    ) -> RuleMatches:
        """Check AWS::Serverless::Function for missing required properties."""
        matches: RuleMatches = []

        for scenario in cfn.get_object_without_conditions(
            properties,
            [
                "PackageType",
                "CodeUri",
                "InlineCode",
                "ImageUri",
                "Handler",
                "Runtime",
            ],
        ):
            props = scenario.get("Object")
            path: Path = ["Resources", resource_name, "Properties"]

            # check is zip deployment for SAM
            # SAM functions are Zip by default unless PackageType is "Image"
            # PackageType is authoritative - check it first before inferring
            # from other properties
            is_zip_deployment = True

            if props.get("PackageType") == "Image":
                is_zip_deployment = False
            elif props.get("PackageType") == "Zip":
                # Explicit Zip package type (authoritative, even if ImageUri present)
                path.append("PackageType")
            elif props.get("ImageUri") is not None:
                # ImageUri implies Image package type (when PackageType not set)
                is_zip_deployment = False
            elif props.get("CodeUri") is not None:
                # CodeUri indicates Zip deployment
                path.append("CodeUri")
            elif props.get("InlineCode") is not None:
                # InlineCode indicates Zip deployment
                path.append("InlineCode")
            else:
                # Default is Zip package type for SAM functions
                # (no CodeUri/InlineCode/ImageUri means code will be
                # provided at deployment time as zip)
                pass

            if not is_zip_deployment:
                continue

            # check required properties for zip deployment
            missing_properties = []
            for p in required_properties:
                if props.get(p) is None:
                    missing_properties.append(p)

            if len(missing_properties) > 0:
                message = "Properties {0} missing for zip file deployment at {1}"
                matches.append(
                    RuleMatch(
                        path,
                        message.format(
                            missing_properties,
                            "/".join(
                                map(str, ["Resources", resource_name, "Properties"])
                            ),
                        ),
                    )
                )

        return matches

    def match(self, cfn: Template) -> RuleMatches:
        matches: RuleMatches = []
        required_properties = [
            "Handler",
            "Runtime",
        ]  # required if package is a .zip file

        # Check AWS::Lambda::Function resources
        resources = cfn.get_resources(["AWS::Lambda::Function"])
        for resource_name, resource in resources.items():
            properties = resource.get("Properties")
            if not isinstance(properties, dict):
                continue
            matches.extend(
                self._check_lambda_function(
                    cfn,
                    resource_name,
                    properties,
                    required_properties,
                )
            )

        # Check AWS::Serverless::Function resources
        sam_resources = cfn.get_resources(["AWS::Serverless::Function"])
        for resource_name, resource in sam_resources.items():
            properties = resource.get("Properties")
            if not isinstance(properties, dict):
                continue
            matches.extend(
                self._check_serverless_function(
                    cfn,
                    resource_name,
                    properties,
                    required_properties,
                )
            )

        return matches
