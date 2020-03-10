"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class AuroraDBInstanceProperties(CloudFormationLintRule):
    """Aurora DB instances have a lot properties that can't be set and vice and versa"""
    id = 'E3029'
    shortdesc = 'Aurora instances don\'t require certain properties'
    description = 'Certain properties are not reuqired when using the Aurora engine for AWS::RDS::DBInstance'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html'
    tags = ['resources', 'rds']
    aurora_not_required_props = [
        'AllocatedStorage',
        'BackupRetentionPeriod',
        'CopyTagsToSnapshot',
        'DeletionProtection',
        'EnableIAMDatabaseAuthentication',
        'MasterUserPassword',
        'StorageEncrypted',
    ]
    aurora_engines = [
        'aurora',
        'aurora-mysql',
        'aurora-postgresql',
    ]

    def __init__(self):
        """Init"""
        super(AuroraDBInstanceProperties, self).__init__()
        self.resource_property_types = ['AWS::RDS::DBInstance']

    def check(self, properties, path, cfn):
        """Check itself"""
        matches = []
        property_sets = cfn.get_object_without_conditions(
            properties, ['Engine'] + self.aurora_not_required_props)
        for property_set in property_sets:
            properties = property_set.get('Object')
            scenario = property_set.get('Scenario')
            engine_sets = properties.get_safe('Engine', type_t=six.string_types)
            for engine, _ in engine_sets:
                if engine in self.aurora_engines:
                    for prop in properties:
                        if prop in self.aurora_not_required_props:
                            path_prop = path[:] + [prop]
                            message = 'You cannot specify {} for Aurora AWS::RDS::DBInstance at {}'
                            if scenario is None:
                                matches.append(
                                    RuleMatch(path_prop, message.format(prop, '/'.join(map(str, path_prop)))))
                            else:
                                scenario_text = ' and '.join(
                                    ['when condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
                                matches.append(
                                    RuleMatch(path_prop, message.format(prop, '/'.join(map(str, path_prop)) + ' ' + scenario_text)))
        return matches

    def match_resource_properties(self, properties, _, path, cfn):
        """Match for sub properties"""
        matches = []
        matches.extend(self.check(properties, path, cfn))
        return matches
