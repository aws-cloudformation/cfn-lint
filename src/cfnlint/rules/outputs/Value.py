"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.schema import ResourceNotFoundError
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER
from cfnlint.template.template import Template


class Value(CloudFormationLintRule):
    """Check if Outputs have string values"""

    id = "E6003"
    shortdesc = "Outputs have values of strings"
    description = "Making sure the outputs have strings as values"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"
    tags = ["outputs"]

    def match(self, cfn: Template):
        matches = []

        template = cfn.template

        getatts = cfn.search_deep_keys("Fn::GetAtt")
        refs = cfn.search_deep_keys("Ref")
        # If using a getatt make sure the attribute of the resource
        # is not of Type List
        for getatt in getatts:
            if getatt[0] == "Outputs":
                if getatt[2] == "Value":
                    obj = getatt[-1]
                    if isinstance(obj, list):
                        objtype = (
                            template.get("Resources", {}).get(obj[0], {}).get("Type")
                        )
                        if objtype:
                            try:
                                res_schema = (
                                    PROVIDER_SCHEMA_MANAGER.get_resource_schema(
                                        cfn.regions[0], objtype
                                    )
                                )
                            except ResourceNotFoundError:
                                continue
                            attribute = res_schema.get_atts().get(obj[1])
                            # Bad schema or bad attribute.  Skip if either is true
                            if attribute:
                                if attribute.type == "array":
                                    if getatt[-4] != "Fn::Join" and getatt[-3] != 1:
                                        message = "Output {0} value {1} is of type list"
                                        matches.append(
                                            RuleMatch(
                                                getatt,
                                                message.format(
                                                    getatt[1], "/".join(obj)
                                                ),
                                            )
                                        )

        # If using a ref for an output make sure it isn't a
        # Parameter of Type List
        for ref in refs:
            if ref[0] == "Outputs":
                if ref[2] == "Value":
                    obj = ref[-1]
                    if isinstance(obj, str):
                        param = template.get("Parameters", {}).get(obj)
                        if param:
                            paramtype = param.get("Type")
                            if paramtype:
                                if paramtype.startswith("List<"):
                                    if ref[-4] != "Fn::Join" and ref[-3] != 1:
                                        message = "Output {0} value {1} is of type list"
                                        matches.append(
                                            RuleMatch(ref, message.format(ref[1], obj))
                                        )

        return matches
