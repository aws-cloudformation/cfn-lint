"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class InstanceEngine(CloudFormationLintRule):
    """Check if Resources RDS Instance Size is compatible with the RDS type"""
    id = 'E3040'
    shortdesc = 'RDS DB Instance Engine is valid'
    description = 'Check the RDS DB Instance Engine is valid'
    source_url = 'https://docs.aws.amazon.com/AmazonRDS/latest/APIReference/API_CreateDBInstance.html'
    tags = ['resources', 'rds']

    valid_engines = [
        'aurora',
        'aurora-mysql',
        'aurora-postgresql',
        'mariadb',
        'mysql',
        'oracle-ee',
        'oracle-se2',
        'oracle-se1',
        'oracle-se',
        'postgres',
        'sqlserver-ee',
        'sqlserver-se',
        'sqlserver-ex',
        'sqlserver-web'
    ]

    def __init__(self):
        """Init"""
        super(InstanceEngine, self).__init__()
        self.resource_property_types = ['AWS::RDS::DBInstance']

    def check_value(self, value, path):
        """Check engine"""
        if value.lower() not in self.valid_engines:
            message = 'RDS Engine "{0}" must be one of {1}'
            return [RuleMatch(path, message.format(value, json.dumps(self.valid_engines)))]

        return []

    def match_resource_properties(self, properties, _, path, cfn):
        """Match for sub properties"""
        matches = []
        matches.extend(
            cfn.check_value(
                obj=properties, key='Engine',
                path=path[:],
                check_value=self.check_value
            ))
        return matches
