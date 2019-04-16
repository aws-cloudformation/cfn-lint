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

    def _get_license_model(self, engine, license_model):
        """ Logic to get the correct license model"""
        if not license_model:
            if engine in self.valid_instance_types.get('license-included'):
                license_model = 'license-included'
            elif engine in self.valid_instance_types.get('bring-your-own-license'):
                license_model = 'bring-your-own-license'
            else:
                license_model = 'general-public-license'
            self.logger.debug('Based on Engine: %s we determined the default license will be %s', engine, license_model)

        return license_model

    def get_resources(self, cfn):
        """ Get resources that can be checked """
        results = []
        for resource_name, resource_values in cfn.get_resources('AWS::RDS::DBInstance').items():
            path = ['Resources', resource_name, 'Properties']
            properties = resource_values.get('Properties')
            # Properties items_safe heps remove conditions and focusing on the actual values and scenarios
            for prop_safe, prop_path_safe in properties.items_safe(path):
                engine = prop_safe.get('Engine')
                inst_class = prop_safe.get('DBInstanceClass')
                license_model = prop_safe.get('LicenseModel')

                # Need to get a default license model if none provided
                # Also need to validate all these values are strings otherwise we cannot
                # do validation
                if isinstance(engine, six.string_types) and isinstance(inst_class, six.string_types):
                    license_model = self._get_license_model(engine, license_model)
                    if isinstance(license_model, six.string_types):
                        results.append(
                            {
                                'Engine': engine,
                                'DBInstanceClass': inst_class,
                                'Path': prop_path_safe,
                                'LicenseModel': license_model
                            })
                    else:
                        self.logger.debug('Skip evaluation based on [LicenseModel] not being a string.')
                else:
                    self.logger.debug('Skip evaluation based on [Engine] or [DBInstanceClass] not being strings.')

        return results

    def check_db_config(self, properties, region):
        """ Check db properties """
        matches = []

        db_engine = properties.get('Engine')
        db_license = properties.get('LicenseModel')
        db_instance_class = properties.get('DBInstanceClass')
        if db_license in self.valid_instance_types:
            if db_engine in self.valid_instance_types[db_license]:
                if region in self.valid_instance_types[db_license][db_engine]:
                    if db_instance_class not in self.valid_instance_types[db_license][db_engine][region]:
                        message = 'DBInstanceClass "{0}" is not compatible with engine type "{1}" and LicenseModel "{2}" in region "{3}". Use instance types [{4}]'
                        matches.append(
                            RuleMatch(
                                properties.get('Path') + ['DBInstanceClass'], message.format(
                                    db_instance_class, db_engine, db_license, region, ', '.join(map(str, self.valid_instance_types[db_license][db_engine][region])))))
        else:
            self.logger.debug('Skip evaluation based on license [%s] not matching.', db_license)
        return matches

    def match(self, cfn):
        """Check RDS Resource Instance Sizes"""

        matches = []
        resources = self.get_resources(cfn)
        for resource in resources:
            for region in cfn.regions:
                matches.extend(self.check_db_config(resource, region))
        return matches
