"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


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

    def match(self, cfn):
        """Basic Rule Matching"""
        matches = []
        required_properties = [
            "Handler",
            "Runtime",
        ]  # required if package is a .zip file

        resources = cfn.get_resources(
            ["AWS::Lambda::Function", "AWS::Serverless::Function"]
        )
        for resource_name, resource in resources.items():
            properties = resource.get("Properties")
            if not properties:
                continue

            path = ["Resources", resource_name, "Properties"]

            is_zip_deployment = True
            if properties.get("PackageType") == "Zip":
                path.append("PackageType")
            elif properties.get("Code", {}).get("ZipFile") or properties.get(
                "Code", {}
            ).get("S3Key", "").endswith(".zip"):
                path.append("Code")
            else:
                is_zip_deployment = False

            if not is_zip_deployment:
                continue

            # check required properties for zip deployment
            missing_properties = []
            for p in required_properties:
                if properties.get(p) is None:
                    missing_properties.append(p)

            if len(missing_properties) > 0:
                message = (
                    "Missing required properties for Lambda zip file deployment: {0}"
                )
                matches.append(RuleMatch(path, message.format(missing_properties)))

        return matches
