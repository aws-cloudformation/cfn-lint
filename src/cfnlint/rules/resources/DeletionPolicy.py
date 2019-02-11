"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class DeletionPolicy(CloudFormationLintRule):
    """Check Base Resource Configuration"""
    id = 'E3035'
    shortdesc = 'Check DeletionPolicy values for Resources'
    description = 'Check that the DeletionPolicy values are valid'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html'
    tags = ['resources', 'deletionpolicy']

    def check_value(self, key, path, res_type):
        """Check resource names for DeletionPolicy"""
        matches = []

        valid_values = [
            'Delete',
            'Retain',
            'Snapshot'
        ]

        valid_snapshot_types = [
            'AWS::EC2::Volume',
            'AWS::ElastiCache::CacheCluster',
            'AWS::ElastiCache::ReplicationGroup',
            'AWS::Neptune::DBCluster',
            'AWS::RDS::DBCluster',
            'AWS::RDS::DBInstance',
            'AWS::Redshift::Cluster'
        ]
        if not isinstance(key, (six.text_type, six.string_types)):
            message = 'DeletionPolicy values should be of string at {0}'
            matches.append(RuleMatch(path, message.format('/'.join(map(str, path)))))
            return matches
        if key not in valid_values:
            message = 'DeletionPolicy should be only one of {0} at {1}'
            matches.append(RuleMatch(
                path,
                message.format(', '.join(map(str, valid_values)),
                               '/'.join(map(str, path)))))
        if key == 'Snapshot' and res_type not in valid_snapshot_types:
            message = 'DeletionPolicy cannot be Snapshot for resources of type {0} at {1}'
            matches.append(RuleMatch(
                path,
                message.format(res_type,
                               '/'.join(map(str, path)))))

        return matches

    def match(self, cfn):
        """Check CloudFormation Resources"""

        matches = []

        resources = cfn.get_resources()

        for resource_name, resource_values in resources.items():
            deletion_policies = resource_values.get('DeletionPolicy')
            if deletion_policies:
                path = ['Resources', resource_name, 'DeletionPolicy']
                res_type = resource_values.get('Type')
                self.logger.debug('Validating DeletionPolicy for %s base configuration', resource_name)
                if isinstance(deletion_policies, list):
                    message = 'Only one DeletionPolicy allowed per resource at {0}'
                    matches.append(RuleMatch(path, message.format('/'.join(map(str, path)))))
                else:
                    matches.extend(self.check_value(deletion_policies, path, res_type))

        return matches
