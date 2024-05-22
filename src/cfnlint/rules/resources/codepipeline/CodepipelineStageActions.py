"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import regex as re

from cfnlint._typing import Path, RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class CodepipelineStageActions(CloudFormationLintRule):
    """Check if CodePipeline Stage Actions are set up properly."""

    id = "E2541"
    shortdesc = "CodePipeline Stage Actions"
    description = "See if CodePipeline stage actions are set correctly"
    source_url = "https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#pipeline-requirements"
    tags = ["resources", "codepipeline"]

    CONSTRAINTS = {
        "AWS": {
            "Source": {
                "S3": {
                    "InputArtifactRange": 0,
                    "OutputArtifactRange": 1,
                },
                "CodeCommit": {
                    "InputArtifactRange": 0,
                    "OutputArtifactRange": 1,
                },
                "ECR": {
                    "InputArtifactRange": 0,
                    "OutputArtifactRange": 1,
                },
            },
            "Test": {
                "CodeBuild": {
                    "InputArtifactRange": (1, 5),
                    "OutputArtifactRange": (0, 5),
                },
                "DeviceFarm": {
                    "InputArtifactRange": 1,
                    "OutputArtifactRange": 0,
                },
            },
            "Build": {
                "CodeBuild": {
                    "InputArtifactRange": (1, 5),
                    "OutputArtifactRange": (0, 5),
                }
            },
            "Approval": {
                "Manual": {
                    "InputArtifactRange": 0,
                    "OutputArtifactRange": 0,
                }
            },
            "Deploy": {
                "S3": {
                    "InputArtifactRange": 1,
                    "OutputArtifactRange": 0,
                },
                "CloudFormation": {
                    "InputArtifactRange": (0, 10),
                    "OutputArtifactRange": (0, 1),
                },
                "CodeDeploy": {
                    "InputArtifactRange": 1,
                    "OutputArtifactRange": 0,
                },
                "ElasticBeanstalk": {
                    "InputArtifactRange": 1,
                    "OutputArtifactRange": 0,
                },
                "OpsWorks": {
                    "InputArtifactRange": 1,
                    "OutputArtifactRange": 0,
                },
                "ECS": {
                    "InputArtifactRange": 1,
                    "OutputArtifactRange": 0,
                },
                "ServiceCatalog": {
                    "InputArtifactRange": 1,
                    "OutputArtifactRange": 0,
                },
            },
            "Invoke": {
                "Lambda": {
                    "InputArtifactRange": (0, 5),
                    "OutputArtifactRange": (0, 5),
                }
            },
        },
        "ThirdParty": {
            "Source": {
                "GitHub": {
                    "InputArtifactRange": 0,
                    "OutputArtifactRange": 1,
                }
            },
            "Deploy": {
                "AlexaSkillsKit": {
                    "InputArtifactRange": (0, 2),
                    "OutputArtifactRange": 0,
                },
            },
        },
        "Custom": {
            "Build": {
                "Jenkins": {
                    "InputArtifactRange": (0, 5),
                    "OutputArtifactRange": (0, 5),
                },
            },
            "Test": {
                "Jenkins": {
                    "InputArtifactRange": (0, 5),
                    "OutputArtifactRange": (0, 5),
                },
            },
        },
    }

    KEY_MAP = {
        "InputArtifacts": "InputArtifactRange",
        "OutputArtifacts": "OutputArtifactRange",
    }

    def check_artifact_counts(self, action, artifact_type, path, scenario):
        """Check that artifact counts are within valid ranges."""
        matches = []

        action_type_id = action.get("ActionTypeId")
        owner = action_type_id.get("Owner")
        category = action_type_id.get("Category")
        provider = action_type_id.get("Provider")

        if (
            isinstance(owner, dict)
            or isinstance(category, dict)
            or isinstance(provider, dict)
        ):
            self.logger.debug(
                "owner, category, provider need to be strings to validate. Skipping."
            )
            return matches

        constraints = (
            self.CONSTRAINTS.get(owner, {}).get(category, {}).get(provider, {})
        )
        if not constraints:
            return matches
        artifact_count = len(action.get(artifact_type, []))

        constraint_key = self.KEY_MAP[artifact_type]
        if isinstance(constraints[constraint_key], tuple):
            min_, max_ = constraints[constraint_key]
            if not min_ <= artifact_count <= max_:
                message = (
                    f'Action "{action["Name"]}" declares'
                    f" {artifact_count} {artifact_type} which is not in expected range"
                    f" [{min_}, {max_}]."
                )
                if scenario:
                    scenario_text = " and ".join(
                        [f'condition "{k}" is {v}' for (k, v) in scenario.items()]
                    )
                    message = message + " When " + scenario_text
                matches.append(RuleMatch(path + [artifact_type], message))
        else:
            if artifact_count != constraints[constraint_key]:
                message = (
                    f'Action "{action["Name"]}" declares'
                    f" {artifact_count} {artifact_type} which is not the expected"
                    f" number [{constraints[constraint_key]}]."
                )
                if scenario:
                    scenario_text = " and ".join(
                        [f'condition "{k}" is {v}' for (k, v) in scenario.items()]
                    )
                    message = message + " When " + scenario_text
                matches.append(RuleMatch(path + [artifact_type], message))

        return matches

    def check_version(self, action, path, scenario):
        """Check that action type version is valid."""
        matches = []

        REGEX_VERSION_STRING = re.compile(r"^[0-9A-Za-z_-]+$")
        LENGTH_MIN = 1
        LENGTH_MAX = 9

        version = action.get("ActionTypeId", {}).get("Version")
        if isinstance(version, dict):
            self.logger.debug(
                "Unable to validate version when an object is used.  Skipping"
            )
        elif isinstance(version, (str)):
            if not LENGTH_MIN <= len(version) <= LENGTH_MAX:
                message = (
                    "Version string ({0}) must be between {1} and {2} characters in"
                    " length."
                )
                if scenario:
                    scenario_text = " and ".join(
                        [f'condition "{k}" is {v}' for (k, v) in scenario.items()]
                    )
                    message = message + " When " + scenario_text
                matches.append(
                    RuleMatch(
                        path + ["ActionTypeId", "Version"],
                        message.format(version, LENGTH_MIN, LENGTH_MAX),
                    )
                )
            elif not re.match(REGEX_VERSION_STRING, version):
                message = "Version string must match the pattern [0-9A-Za-z_-]+."
                if scenario:
                    scenario_text = " and ".join(
                        [f'condition "{k}" is {v}' for (k, v) in scenario.items()]
                    )
                    message = message + " When " + scenario_text
                matches.append(RuleMatch(path + ["ActionTypeId", "Version"], message))
        return matches

    def check_names_unique(self, action, path, action_names, scenario):
        """Check that action names are unique."""
        matches = []

        action_name = action.get("Name")
        if isinstance(action_name, str):
            if action.get("Name") in action_names:
                message = (
                    "All action names within a stage must be unique"
                    f" ({action.get('Name')})."
                )
                if scenario:
                    scenario_text = " and ".join(
                        [f'condition "{k}" is {v}' for (k, v) in scenario.items()]
                    )
                    message = message + " When " + scenario_text
                matches.append(RuleMatch(path + ["Name"], message))
            action_names.add(action.get("Name"))

        return matches

    def check_artifact_names(self, action, path, artifact_names, scenario):
        """
        Check that output artifact names are unique and
        inputs are from previous stage outputs.
        """
        matches = []

        input_artifacts = action.get("InputArtifacts")
        if isinstance(input_artifacts, list):
            for input_artifact in input_artifacts:
                artifact_name = input_artifact.get("Name")
                if isinstance(artifact_name, str):
                    if artifact_name not in artifact_names:
                        message = (
                            "Every input artifact for an action must match the output"
                            " artifact of an action earlier in the pipeline"
                            f" ({artifact_name})."
                        )
                        if scenario:
                            scenario_text = " and ".join(
                                [
                                    f'condition "{k}" is {v}'
                                    for (k, v) in scenario.items()
                                ]
                            )
                            message = message + " When " + scenario_text
                        matches.append(
                            RuleMatch(path + ["InputArtifacts", "Name"], message)
                        )

        output_artifacts = action.get("OutputArtifacts")
        if isinstance(output_artifacts, list):
            for output_artifact in output_artifacts:
                artifact_name = output_artifact.get("Name")
                if isinstance(artifact_name, str):
                    if artifact_name in artifact_names:
                        message = (
                            "Every output artifact in the pipeline must have a unique"
                            f" name. ({artifact_name})"
                        )
                        matches.append(
                            RuleMatch(path + ["OutputArtifacts", "Name"], message)
                        )
                    artifact_names.add(artifact_name)

        return matches

    def match(self, cfn: Template) -> RuleMatches:
        """Check that stage actions are set up properly."""
        matches: RuleMatches = []

        for resource_name, resource_value in cfn.get_resources(
            "AWS::CodePipeline::Pipeline"
        ).items():
            path: Path = ["Resources", resource_name, "Properties"]
            properties = resource_value.get("Properties", {})
            scenarios = cfn.get_object_without_nested_conditions(properties, path)
            for scenario in scenarios:
                conditions = scenario.get("Scenario")
                path = path + ["Stages"]
                properties = scenario.get("Object")
                artifact_names: set[str] = set()

                s_stages = properties.get("Stages")
                if not isinstance(s_stages, list):
                    self.logger.debug(
                        "Stages not list. Should have been caught by generic linting."
                    )
                    return matches
                for s_stage_i, s_stage_v in enumerate(s_stages):
                    action_names: set[str] = set()
                    s_actions = s_stage_v.get("Actions")
                    if not isinstance(s_actions, list):
                        self.logger.debug(
                            "Actions not list. Should have been caught by generic"
                            " linting."
                        )
                        return matches

                    for s_action_i, s_action_v in enumerate(s_actions):
                        try:
                            full_path = path + [s_stage_i, "Actions", s_action_i]
                            matches.extend(
                                self.check_names_unique(
                                    s_action_v, full_path, action_names, conditions
                                )
                            )
                            matches.extend(
                                self.check_version(s_action_v, full_path, conditions)
                            )
                            matches.extend(
                                self.check_artifact_counts(
                                    s_action_v, "InputArtifacts", full_path, conditions
                                )
                            )
                            matches.extend(
                                self.check_artifact_counts(
                                    s_action_v, "OutputArtifacts", full_path, conditions
                                )
                            )
                            matches.extend(
                                self.check_artifact_names(
                                    s_action_v, full_path, artifact_names, conditions
                                )
                            )
                        except AttributeError as err:
                            self.logger.debug(
                                (
                                    "Got AttributeError. Should have been caught by"
                                    " generic linting. Ignoring the error here: %s"
                                ),
                                str(err),
                            )

        return matches
