"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import cfnlint.data.AdditionalSpecs
from cfnlint.helpers import load_resource
from cfnlint.jsonschema import Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


class UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes(CfnLintJsonSchema):
    id = "I3011"
    shortdesc = "Check stateful resources have a set UpdateReplacePolicy/DeletionPolicy"
    description = (
        "The default action when replacing/removing a resource is to "
        "delete it. This check requires you to explicitly set policies"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html"
    tags = ["resources", "updatereplacepolicy", "deletionpolicy"]

    def __init__(self):
        """Init"""
        super().__init__(
            keywords=["Resources/*"],
            all_matches=True,
        )

        spec = load_resource(cfnlint.data.AdditionalSpecs, "StatefulResources.json")
        self.likely_stateful_resource_types = [
            resource_type
            for resource_type, descr in spec["ResourceTypes"].items()
            # Resources that won't be deleted if they're not empty (ex: S3)
            # don't need to be checked for policies, as chance of mistakes are low.
            if not descr.get("DeleteRequiresEmptyResource", False)
        ]

        self._schema = {"required": ["DeletionPolicy", "UpdateReplacePolicy"]}

    def validate(self, validator: Validator, s: Any, instance: Any, schema: Any):
        resource_type = instance.get("Type")

        if not isinstance(resource_type, str):
            return

        if resource_type not in self.likely_stateful_resource_types:  # type: ignore
            return

        for err in super().validate(validator, s, instance, self._schema):
            err.message = (
                f"{err.message} (The default action when replacing/removing "
                "a resource is to delete it. Set explicit values for "
                "stateful resource)"
            )
            yield err
