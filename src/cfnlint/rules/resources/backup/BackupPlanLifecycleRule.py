"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class BackupPlanLifecycleRule(CloudFormationLintRule):
    """Check Backup Plan rules with lifecycle has minimum period between cold and delete"""
    id = 'E3504'
    shortdesc = 'Check minimum 90 period is met between BackupPlan cold and delete'
    description = 'Check that Backup plans with lifecycle rules have >= 90 days between cold and delete'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-backup-backupplan-lifecycleresourcetype.html'
    tags = ['properties', 'backup', 'plan', 'lifecycle']

    def match(self, cfn):
        """Check cold storage and deletion lifecycle period differences"""
        matches = []
        results = cfn.get_resource_properties(['AWS::Backup::BackupPlan', 'BackupPlan', 'BackupPlanRule', 'Lifecycle'])

        for result in results:
            backup_rule = result['Value']
            # if 'MoveToColdStorageAfterDays' in backup_rule and 'DeleteAfterDays' in backup_rule:
            if isinstance(backup_rule.get('MoveToColdStorageAfterDays'), int) and isinstance(backup_rule.get('DeleteAfterDays'), int):
                if backup_rule['DeleteAfterDays'] - backup_rule['MoveToColdStorageAfterDays'] < 90:
                    message = 'DeleteAfterDays in {0} must be at least 90 days after MoveToColdStorageAfterDays'
                    rule_match = RuleMatch(result['Path'], message.format('/'.join(map(str, result['Path']))))
                    matches.append(rule_match)

        return matches
