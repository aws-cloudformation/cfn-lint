"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class PipelineArtifactCounts(CfnLintKeyword):
    id = "E3702"
    shortdesc = "Validate the number of input and output artifacts in a CodePipeline"
    description = (
        "When using AWS::CodePipeline::Pipeline action types "
        "have different contraints for InputArtifacts and "
        "OutputArtifacts"
    )
    tags = ["resources", "codepipeline"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::CodePipeline::Pipeline/Properties/Stages/*/Actions/*",
            ],
        )

        self._artifact_counts: dict[str, dict[str, dict[str, Any]]] = {
            "AWS": {
                "Source": {
                    "S3": {
                        "InputArtifacts": {"maxItems": 0},
                        "OutputArtifacts": {"minItems": 1, "maxItems": 1},
                    },
                    "CodeCommit": {
                        "InputArtifacts": {"maxItems": 0},
                        "OutputArtifacts": {"minItems": 1, "maxItems": 1},
                    },
                    "ECR": {
                        "InputArtifacts": {"maxItems": 0},
                        "OutputArtifacts": {"minItems": 1, "maxItems": 1},
                    },
                },
                "Test": {
                    "CodeBuild": {
                        "InputArtifacts": {"minItems": 1, "maxItems": 5},
                        "OutputArtifacts": {"minItems": 0, "maxItems": 5},
                    },
                    "DeviceFarm": {
                        "InputArtifacts": {"minItems": 1, "maxItems": 1},
                        "OutputArtifacts": {"maxItems": 0},
                    },
                },
                "Build": {
                    "CodeBuild": {
                        "InputArtifacts": {"minItems": 1, "maxItems": 5},
                        "OutputArtifacts": {"minItems": 0, "maxItems": 5},
                    }
                },
                "Approval": {
                    "Manual": {
                        "InputArtifacts": {"maxItems": 0},
                        "OutputArtifacts": {"maxItems": 0},
                    }
                },
                "Deploy": {
                    "S3": {
                        "InputArtifacts": {"minItems": 1, "maxItems": 1},
                        "OutputArtifacts": {"maxItems": 0},
                    },
                    "CloudFormation": {
                        "InputArtifacts": {"minItems": 0, "maxItems": 10},
                        "OutputArtifacts": {"minItems": 0, "maxItems": 1},
                    },
                    "CodeDeploy": {
                        "InputArtifacts": {"minItems": 1, "maxItems": 1},
                        "OutputArtifacts": {"maxItems": 0},
                    },
                    "ElasticBeanstalk": {
                        "InputArtifacts": {"minItems": 1, "maxItems": 1},
                        "OutputArtifacts": {"maxItems": 0},
                    },
                    "OpsWorks": {
                        "InputArtifacts": {"minItems": 1, "maxItems": 1},
                        "OutputArtifacts": {"maxItems": 0},
                    },
                    "ECS": {
                        "InputArtifacts": {"minItems": 1, "maxItems": 1},
                        "OutputArtifacts": {"maxItems": 0},
                    },
                    "ServiceCatalog": {
                        "InputArtifacts": {"minItems": 1, "maxItems": 1},
                        "OutputArtifacts": {"maxItems": 0},
                    },
                },
                "Invoke": {
                    "Lambda": {
                        "InputArtifacts": {"minItems": 0, "maxItems": 5},
                        "OutputArtifacts": {"minItems": 0, "maxItems": 5},
                    }
                },
            },
            "ThirdParty": {
                "Source": {
                    "GitHub": {
                        "InputArtifacts": {"maxItems": 0},
                        "OutputArtifacts": {"minItems": 1, "maxItems": 1},
                    }
                },
                "Deploy": {
                    "AlexaSkillsKit": {
                        "InputArtifacts": {"minItems": 0, "maxItems": 2},
                        "OutputArtifacts": {"maxItems": 0},
                    },
                },
            },
            "Custom": {
                "Build": {
                    "Jenkins": {
                        "InputArtifacts": {"minItems": 0, "maxItems": 5},
                        "OutputArtifacts": {"minItems": 0, "maxItems": 5},
                    },
                },
                "Test": {
                    "Jenkins": {
                        "InputArtifacts": {"minItems": 0, "maxItems": 5},
                        "OutputArtifacts": {"minItems": 0, "maxItems": 5},
                    },
                },
            },
        }

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not validator.is_type(instance, "object"):
            return

        for action, action_validator in get_value_from_path(
            validator, instance, path=deque(["ActionTypeId"])
        ):
            for owner, owner_validator in get_value_from_path(
                action_validator, action, path=deque(["Owner"])
            ):
                owner_artifact_counts = self._artifact_counts.get(owner)
                if not owner_artifact_counts:
                    continue
                for category, categor_validator in get_value_from_path(
                    owner_validator, action, path=deque(["Category"])
                ):
                    category_artifact_counts = owner_artifact_counts.get(category)
                    if not category_artifact_counts:
                        continue
                    for provider, provider_provider in get_value_from_path(
                        categor_validator, action, deque(["Provider"])
                    ):
                        count_schema: dict[str, Any] = {
                            "properties": category_artifact_counts.get(provider),
                            "required": [],
                        }
                        if not count_schema.get("properties"):
                            continue

                        for key in ["InputArtifacts", "OutputArtifacts"]:
                            if (
                                count_schema.get("properties", {})
                                .get(key, {})
                                .get("minItems", 0)
                                > 0
                            ):
                                count_schema["required"].append(key)

                        provider_provider = provider_provider.evolve(
                            schema=count_schema,
                        )

                        repr = {
                            "Owner": owner,
                            "Category": category,
                            "Provider": provider,
                        }
                        for err in provider_provider.iter_errors(instance):
                            err.message = f"{err.message} when using {repr!r}"
                            err.rule = self
                            yield err
