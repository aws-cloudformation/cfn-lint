"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class RetentionPeriodOnResourceTypesWithAutoExpiringContent(CloudFormationLintRule):
    """Check for RetentionPeriod """
    id = 'I3012'
    shortdesc = 'Check resources with auto expiring content have explicit retention period'
    description = 'The behaviour for data retention is different across AWS Services.'\
                  'If no retention period is specified the default for some services is to delete the data after a period of time.' \
                  'This check requires you to explicitly set the retention period for those resources to avoid unexpected data losses'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['resources', 'retentionperiod']

    def match(self, cfn):
        """Check for RetentionPeriod"""
        matches = []

        retention_attributes_by_resource_type = {
            'AWS::Kinesis::Stream': [
                {
                    'Attribute': 'RetentionPeriodHours',
                    'SourceUrl': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesis-stream.html#cfn-kinesis-stream-retentionperiodhours'
                }
            ],
            'AWS::SQS::Queue':  [
                {
                    'Attribute': 'MessageRetentionPeriod',
                    'SourceUrl': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html#aws-sqs-queue-msgretentionperiod'
                }
            ],
            'AWS::DocDB::DBCluster': [
                {
                    'Attribute': 'BackupRetentionPeriod',
                    'SourceUrl': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-backupretentionperiod'
                }
            ],
            'AWS::Synthetics::Canary': [
                {
                    'Attribute': 'SuccessRetentionPeriod',
                    'SourceUrl': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-successretentionperiod'
                },
                {
                    'Attribute': 'FailureRetentionPeriod',
                    'SourceUrl': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-failureretentionperiod'
                }
            ],
            'AWS::Redshift::Cluster': [
                {
                    'Attribute': 'AutomatedSnapshotRetentionPeriod',
                    'SourceUrl': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-automatedsnapshotretentionperiod'
                }
            ],
            'AWS::RDS::DBInstance': [
                {
                    'Attribute': 'BackupRetentionPeriod',
                    'SourceUrl': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-backupretentionperiod'
                }
            ],
            'AWS::RDS::DBCluster': [
                {
                    'Attribute': 'BackupRetentionPeriod',
                    'SourceUrl': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-backuprententionperiod'
                }
            ]
        }

        resources = cfn.get_resources()
        for r_name, r_values in resources.items():
            if r_values.get('Type') in retention_attributes_by_resource_type:
                for attr_def in retention_attributes_by_resource_type[r_values.get('Type')]:
                    properties = r_values.get('Properties')
                    if not properties or not properties.get(attr_def.get('Attribute')):
                        path = ['Resources', r_name]
                        message = 'The default retention period will delete the data after a pre-defined time. Set an explicit values to avoid data loss on resource : %s' % '/'.join(path)
                        matches.append(RuleMatch(path, message))

        return matches
