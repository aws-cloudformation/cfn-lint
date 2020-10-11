"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes(CloudFormationLintRule):
    """Check for UpdateReplacePolicy / DeletionPolicy"""
    id = 'I3011'
    shortdesc = 'Check stateful resources have a set UpdateReplacePolicy/DeletionPolicy'
    description = 'The default action when replacing/removing a resource is to ' \
                  'delete it. This check requires you to explicitly set policies'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html'
    tags = ['resources', 'updatereplacepolicy', 'deletionpolicy']

    def match(self, cfn):
        """Check for UpdateReplacePolicy / DeletionPolicy"""
        matches = []

        likely_stateful_resource_types = ['AWS::CloudFormation::Stack',
                                          'AWS::Backup::BackupVault',
                                          'AWS::Cognito::UserPool',
                                          'AWS::DocDB::DBCluster',
                                          'AWS::DocDB::DBInstance',
                                          'AWS::DynamoDB::Table',
                                          'AWS::EC2::Volume',
                                          'AWS::EFS::FileSystem',
                                          'AWS::EMR::Cluster',
                                          'AWS::ElastiCache::CacheCluster',
                                          'AWS::ElastiCache::ReplicationGroup',
                                          'AWS::Elasticsearch::Domain',
                                          'AWS::FSx::FileSystem',
                                          'AWS::Logs::LogGroup',
                                          'AWS::Neptune::DBCluster',
                                          'AWS::Neptune::DBInstance',
                                          'AWS::QLDB::Ledger',
                                          'AWS::RDS::DBCluster',
                                          'AWS::RDS::DBInstance',
                                          'AWS::Redshift::Cluster',
                                          'AWS::SDB::Domain',
                                          'AWS::SQS::Queue',
                                          # 'AWS::S3::Bucket', (CloudFormation won't delete anyways)
                                         ]

        resources = cfn.get_resources()
        for r_name, r_values in resources.items():
            if r_values.get('Type') in likely_stateful_resource_types:
                if not r_values.get('DeletionPolicy') or not r_values.get('UpdateReplacePolicy'):
                    path = ['Resources', r_name]
                    message = 'The default action when replacing/removing a resource is to delete it. Set explicit values for UpdateReplacePolicy / DeletionPolicy on potentially stateful resource: %s' \
                    % '/'.join(path)
                    matches.append(RuleMatch(path, message))

        return matches
