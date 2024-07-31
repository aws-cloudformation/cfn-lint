"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any, Iterator

from cfnlint.helpers import ensure_list, is_function
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.helpers import get_resource_by_name, get_value_from_path
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class InstanceImageId(CfnLintKeyword):
    id = "E3673"
    shortdesc = "Validate if an ImageId is required"
    description = (
        "Validate if an ImageID is required. It can be "
        "required if the associated LaunchTemplate doesn't specify "
        "an ImageID"
    )
    tags = ["resources", "ec2"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::EC2::Instance/Properties",
            ],
        )

    def _get_related_launch_template(
        self, validator: Validator, instance: Any
    ) -> Iterator[tuple[Any, Validator]]:

        for launch_template, launch_template_validator in get_value_from_path(
            validator, instance, deque(["LaunchTemplate"])
        ):
            if not launch_template:
                continue
            for id, id_validator in get_value_from_path(
                launch_template_validator, launch_template, deque(["LaunchTemplateId"])
            ):
                if id is None:
                    for name, name_validator in get_value_from_path(
                        id_validator,
                        launch_template,
                        deque(["LaunchTemplateName"]),
                    ):
                        yield name, name_validator
                yield id, id_validator

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        for (
            instance_image_id,
            instance_image_id_validator,
        ) in get_value_from_path(
            validator,
            instance,
            path=deque(["ImageId"]),
        ):
            if instance_image_id:
                continue

            launch_templates = list(
                self._get_related_launch_template(instance_image_id_validator, instance)
            )
            path: deque[str | int] = deque([])
            if "ImageId" != instance_image_id_validator.context.path.path[-1]:
                path = deque(
                    list(instance_image_id_validator.context.path.path)[
                        len(validator.context.path.path) :
                    ]
                )

            if not launch_templates:
                yield ValidationError(
                    "'ImageId' is a required property",
                    validator="required",
                    path=path,
                    rule=self,
                )
                continue

            for (
                instance_launch_template,
                instance_launch_template_validator,
            ) in launch_templates:
                fn_k, fn_v = is_function(instance_launch_template)

                # if its not a function we can't tell from a string
                # if the image ID is there or not
                if fn_k is None:
                    continue

                launch_template, launch_template_validator = None, None
                if fn_k == "Ref":
                    if fn_v in instance_launch_template_validator.context.parameters:
                        continue
                    elif fn_v in instance_launch_template_validator.context.resources:
                        launch_template, launch_template_validator = (
                            get_resource_by_name(
                                instance_launch_template_validator,
                                fn_v,
                                ["AWS::EC2::LaunchTemplate"],
                            )
                        )
                    else:
                        continue
                elif fn_k == "Fn::GetAtt":
                    launch_template, launch_template_validator = get_resource_by_name(
                        instance_launch_template_validator,
                        ensure_list(fn_v)[0].split(".")[0],
                        ["AWS::EC2::LaunchTemplate"],
                    )
                else:
                    continue

                for (
                    launch_template_image_id,
                    _,
                ) in get_value_from_path(
                    launch_template_validator,
                    launch_template or {},
                    path=deque(["Properties", "LaunchTemplateData", "ImageId"]),
                ):
                    if launch_template_image_id is None and instance_image_id is None:
                        yield ValidationError(
                            "'ImageId' is a required property",
                            validator="required",
                            path=path,
                            rule=self,
                        )
