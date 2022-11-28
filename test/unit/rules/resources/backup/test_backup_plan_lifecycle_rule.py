"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.backup.BackupPlanLifecycleRule import (
    BackupPlanLifecycleRule,  # pylint: disable=E0401
)


class TestBackupPlanLifecycleRule(BaseRuleTestCase):
    """Check Backup Plan rules with lifecycle has minimum 90 day period between cold and delete"""

    def setUp(self):
        """Setup"""
        super(TestBackupPlanLifecycleRule, self).setUp()
        self.collection.register(BackupPlanLifecycleRule())
        self.success_templates = [
            "test/fixtures/templates/good/resources/backup/test_backup_plan_lifecycle_rule.yml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/backup/test_backup_plan_lifecycle_rule.yml",
            1,
        )
