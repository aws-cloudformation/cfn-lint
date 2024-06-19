"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import os

from cfnlint._typing import RuleMatches
from cfnlint.decode import decode
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template.template import Template


class NestedStackParameters(CloudFormationLintRule):
    """Check that nested stack parameters are specified as needed"""

    id = "E3043"
    shortdesc = "Validate parameters for in a nested stack"
    description = (
        "Evalute if parameters for a nested stack are specified and "
        "if parameters are specified for a nested stack that aren't required."
    )
    source_url = "https://github.com/awslabs/cfn-lint"
    tags = ["resources", "cloudformation"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.resource_property_types.append("AWS::CloudFormation::Stack")

    def __get_template_parameters(self, filename):
        try:
            (tmp, matches) = decode(filename)
        except:  # noqa: E722
            return None
        if matches:
            return None

        return tmp.get("Parameters", {})

    def __compare_objects(self, template_parameters, nested_parameters, scenario, path):
        matches = []
        for key in set(template_parameters.keys()) - set(nested_parameters.keys()):
            if scenario is None:
                message = (
                    'Specified parameter "{0}" doesn\'t exist in nested stack template'
                    " at {1}"
                )
                matches.append(
                    RuleMatch(
                        path + [key],
                        message.format(key, "/".join(map(str, path + [key]))),
                    )
                )
            else:
                message = (
                    'Specified parameter "{0}" doesn\'t exist in nested stack'
                    " template {1}"
                )
                scenario_text = " and ".join(
                    [f'when condition "{k}" is {v}' for (k, v) in scenario.items()]
                )
                matches.append(RuleMatch(path, message.format(key, scenario_text)))
        for key in set(nested_parameters.keys()) - set(template_parameters.keys()):
            if nested_parameters.get(key).get("Default") is None:
                if scenario is None:
                    message = (
                        'Nested stack template parameter "{0}" is not specified at {1}'
                    )
                    matches.append(
                        RuleMatch(path, message.format(key, "/".join(map(str, path))))
                    )
                else:
                    message = (
                        'Nested stack template parameter "{0}" is not specified {1}'
                    )
                    scenario_text = " and ".join(
                        [f'when condition "{k}" is {v}' for (k, v) in scenario.items()]
                    )
                    matches.append(RuleMatch(path, message.format(key, scenario_text)))

        return matches

    def match(self, cfn: Template) -> RuleMatches:
        """Check CloudFormation Properties"""
        matches = []
        resources = cfn.get_resources("AWS::CloudFormation::Stack")
        for resource_name, attributes in resources.items():
            properties = attributes.get("Properties", {})
            # when template is passed via cat (or equivalent filename is none)
            if cfn.filename:
                base_dir = os.path.dirname(os.path.abspath(cfn.filename))

                parameter_groups = cfn.get_object_without_conditions(
                    obj=properties, property_names=["TemplateURL", "Parameters"]
                )

                for parameter_group in parameter_groups:
                    obj = parameter_group.get("Object")
                    template_url = obj.get("TemplateURL")
                    if isinstance(template_url, str):
                        if not (
                            template_url.startswith("http://")
                            or template_url.startswith("https://")
                            or template_url.startswith("s3://")
                        ):
                            template_path = os.path.normpath(
                                os.path.join(base_dir, template_url)
                            )
                            nested_parameters = self.__get_template_parameters(
                                template_path
                            )
                            template_parameters = obj.get("Parameters")
                            if isinstance(nested_parameters, dict) and isinstance(
                                template_parameters, dict
                            ):
                                matches.extend(
                                    self.__compare_objects(
                                        template_parameters=template_parameters,
                                        nested_parameters=nested_parameters,
                                        path=[
                                            "Resources",
                                            resource_name,
                                            "Properties",
                                            "Parameters",
                                        ],
                                        scenario=parameter_group.get("Scenario"),
                                    )
                                )

        return matches
