"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule, RuleMatch


class ServiceTimeout(CloudFormationLintRule):
    """Check a ServiceTimeout property is specified for custom resources"""

    id = "W3046"
    shortdesc = "Ensure a service timeout is specified"
    description = """
      Custom resources should have a ServiceTimeout property specified.
      The default service timeout is 60 minutes.
      Specify a short timeout to reduce waiting if the custom resource fails
    """
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-customresource.html#cfn-cloudformation-customresource-servicetimeout"
    tags = [
        "resources",
        "cloudformation",
        "custom resource",
    ]

    def match(self, cfn):
        """Basic Rule Matching"""

        matches = []

        resources = self._get_custom_resources(cfn)

        for resource_name, attributes in resources.items():
            properties = attributes.get("Properties", {})
            resource_type = attributes.get("Type", None)

            if "ServiceTimeout" not in properties:
                message = f"Missing ServiceTimeout property in {resource_type}"
                matches.append(RuleMatch(["Resources", resource_name], message))

        return matches

    def _get_custom_resources(self, cfn):
        resources = cfn.template.get("Resources", {})
        if not isinstance(resources, dict):
            return {}

        results = {}
        for k, v in resources.items():
            if isinstance(v, dict):
                if (v.get("Type", None) == "AWS::CloudFormation::CustomResource") or (
                    v.get("Type", None).startswith("Custom::")
                ):
                    results[k] = v

        return results
