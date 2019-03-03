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
import cfnlint.helpers
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class InstanceSize(CloudFormationLintRule):
    """Check if Resources RDS Instance Size is compatible with the RDS type"""
    id = 'E3025'
    shortdesc = 'RDS instance type is compatible with the RDS type'
    description = 'Check the RDS instance types are supported by the type of RDS engine. ' \
                  'Only if the values are strings will this be checked.'
    source_url = 'https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html'
    tags = ['resources', 'rds']

    valid_instance_types = cfnlint.helpers.load_resources('data/AdditionalSpecs/RdsProperties.json')

    def get_resources(self, cfn):
        """ Get resources that can be checked """
        results = []
        for resource_name, resource_values in cfn.get_resources('AWS::RDS::DBInstance').items():
            path = ['Resources', resource_name, 'Properties']
            properties = resource_values.get('Properties')
            for prop_safe, prop_path_safe in properties.items_safe(path):
                engine = prop_safe.get('Engine')
                inst_class = prop_safe.get('DBInstanceClass')
                license_model = prop_safe.get('LicenseModel')
                if isinstance(engine, six.string_types) and isinstance(inst_class, six.string_types):
                    results.append(
                        {
                            'Engine': engine,
                            'DBInstanceClass': inst_class,
                            'Path': prop_path_safe,
                            'LicenseModel': license_model
                        })

        return results

    def check_db_config(self, properties, region):
        """ Check db properties """
        matches = []

        for valid_instance_type in self.valid_instance_types:
            engine = properties.get('Engine')
            if engine in valid_instance_type.get('engines'):
                if region in valid_instance_type.get('regions'):
                    db_license = properties.get('LicenseModel')
                    valid_licenses = valid_instance_type.get('license')
                    db_instance_class = properties.get('DBInstanceClass')
                    valid_instance_types = valid_instance_type.get('instance_types')
                    if db_license and valid_licenses:
                        if db_license not in valid_licenses:
                            self.logger.debug('Skip evaluation based on license not matching.')
                            continue
                    if db_instance_class not in valid_instance_types:
                        if db_license is None:
                            message = 'DBInstanceClass "{0}" is not compatible with engine type "{1}" in region "{2}". Use instance types [{3}]'
                            matches.append(
                                RuleMatch(
                                    properties.get('Path') + ['DBInstanceClass'], message.format(
                                        db_instance_class, engine, region, ', '.join(map(str, valid_instance_types)))))
                        else:
                            message = 'DBInstanceClass "{0}" is not compatible with engine type "{1}" and LicenseModel "{2}" in region "{3}". Use instance types [{4}]'
                            matches.append(
                                RuleMatch(
                                    properties.get('Path') + ['DBInstanceClass'], message.format(
                                        db_instance_class, engine, db_license, region, ', '.join(map(str, valid_instance_types)))))
        return matches

    def match(self, cfn):
        """Check RDS Resource Instance Sizes"""

        matches = []
        resources = self.get_resources(cfn)
        for resource in resources:
            for region in cfn.regions:
                matches.extend(self.check_db_config(resource, region))
        return matches
