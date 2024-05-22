"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

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

    def match(self, cfn: Template) -> RuleMatches:
        matches = []
        required_properties = [
            "Handler",
            "Runtime",
        ]  # required if package is a .zip file

        resources = cfn.get_resources(["AWS::Lambda::Function"])

        for resource_name, resource in resources.items():
            properties = resource.get("Properties")
            if not isinstance(properties, dict):
                continue

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
                elif isinstance(code, dict) and (
                    code.get("ZipFile") or code.get("S3Key")
                ):
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
