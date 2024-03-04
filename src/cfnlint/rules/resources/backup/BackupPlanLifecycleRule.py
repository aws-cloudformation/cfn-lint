"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class BackupPlanLifecycleRule(CfnLintKeyword):
    """
    Check Backup Plan rules with lifecycle has minimum
    period between cold and delete
    """

    id = "E3504"
    shortdesc = "Check minimum 90 period is met between BackupPlan cold and delete"
    description = (
        "Check that Backup plans with lifecycle rules have >= 90 days between cold and"
        " delete"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-lifecycleresourcetype.html"
    tags = ["properties", "backup", "plan", "lifecycle"]

    def __init__(self) -> None:
        super().__init__(
            [
                "AWS::Backup::BackupPlan/Properties/BackupPlanResourceType/BackupRuleResourceType/Lifecycle"
            ]
        )

    def backupbackupplanlifecycle(self, validator, uI, instance, schema):
        delete_after_days = instance.get("DeleteAfterDays")
        move_to_cold_storage_after_days = instance.get("MoveToColdStorageAfterDays")

        if not validator.is_type(delete_after_days, "integer"):
            return
        if not validator.is_type(move_to_cold_storage_after_days, "integer"):
            return
        if delete_after_days - move_to_cold_storage_after_days < 90:
            yield ValidationError(
                (
                    f"DeleteAfterDays {delete_after_days!r} must be at least "
                    "90 days after MoveToColdStorageAfterDays "
                    f"{move_to_cold_storage_after_days}"
                ),
                path=deque(["DeleteAfterDays"]),
                rule=self,
            )
