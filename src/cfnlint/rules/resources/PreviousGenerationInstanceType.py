"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class PreviousGenerationInstanceType(CloudFormationLintRule):
    id = 'I3100'
    shortdesc = 'Checks for legacy instance type generations'
    description = 'New instance type generations increase performance and decrease cost'
    source_url = 'https://aws.amazon.com/ec2/previous-generation/'
    tags = ['resources', 'ec2', 'rds', 'elasticcache', 'elasticsearch']

    def match(self, cfn):
        matches = []
        for resource_type, property_type in [
          ('AWS::AutoScaling::LaunchConfiguration', 'InstanceType'),
          ('AWS::EC2::CapacityReservation', 'InstanceType'),
          ('AWS::EC2::Host', 'InstanceType'),
          ('AWS::EC2::Instance', 'InstanceType'),
          ('AWS::RDS::DBInstance', 'DBInstanceClass'),
          ('AWS::ElastiCache::CacheCluster', 'CacheNodeType'),
          ('AWS::ElastiCache::GlobalReplicationGroup', 'CacheNodeType'),
          ('AWS::ElastiCache::ReplicationGroup', 'CacheNodeType'),
        ]:
            for resource_name, resource in cfn.get_resources([resource_type]).items():
                if isinstance(resource.get('Properties', {}).get(property_type, ''), str):
                    if re.search(r'([cmr][1-3]|cc2|cg1|cr1|g2|hi1|hs1|i2|t1)\.', resource.get('Properties', {}).get(property_type, '')):
                        matches.append(RuleMatch(['Resources', resource_name, 'Properties', property_type], 'Upgrade previous generation instance type: ' + resource.get('Properties').get(property_type)))

        for resource_type, top_level_property_type, property_type in [
          ('AWS::EC2::EC2Fleet', 'FleetLaunchTemplateOverridesRequest', 'InstanceType'),
          ('AWS::EC2::LaunchTemplate', 'LaunchTemplateData', 'InstanceType'),
          ('AWS::EC2::SpotFleet', 'SpotFleetLaunchSpecification', 'InstanceType'),
          ('AWS::OpenSearchService::Domain', 'ClusterConfig', 'InstanceType'),
          ('AWS::Elasticsearch::Domain', 'ElasticsearchClusterConfig', 'InstanceType'),
        ]:
            for resource_name, resource in cfn.get_resources([resource_type]).items():
                if isinstance(resource.get('Properties', {}).get(top_level_property_type, {}).get(property_type, ''), str):
                    if re.search(r'([cmr][1-3]|cc2|cg1|cr1|g2|hi1|hs1|i2|t1)\.', resource.get('Properties', {}).get(top_level_property_type, {}).get(property_type, '')):
                        matches.append(RuleMatch(['Resources', resource_name, 'Properties', top_level_property_type, property_type], 'Upgrade previous generation instance type: ' + resource.get('Properties').get(top_level_property_type).get(property_type)))
        return matches
