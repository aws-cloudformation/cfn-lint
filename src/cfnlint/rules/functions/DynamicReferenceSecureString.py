"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
import re
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch
import cfnlint.helpers


class DynamicReferenceSecureString(CloudFormationLintRule):
    """Check if Dynamic Reference Secure Strings are only used in the correct locations"""
    id = 'E1027'
    shortdesc = 'Check dynamic references secure strings are in supported locations'
    description = 'Dynamic References Secure Strings are only supported for a small set of resource properties.  ' \
                  'Validate that they are being used in the correct location when checking values ' \
                  'and Fn::Sub in resource properties. Currently doesn\'t check outputs, maps, conditions, '\
                  'parameters, and descriptions.'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html'
    tags = ['functions', 'dynamic reference']

    def __init__(self, ):
        """Init """
        specs = cfnlint.helpers.RESOURCE_SPECS.get('us-east-1')
        self.property_specs = specs.get('PropertyTypes')
        self.resource_specs = specs.get('ResourceTypes')
        for resource_spec in self.resource_specs:
            self.resource_property_types.append(resource_spec)
        for property_spec in self.property_specs:
            self.resource_sub_property_types.append(property_spec)
        self.exceptions = {
            'AWS::DirectoryService::MicrosoftAD': 'Password',
            'AWS::DirectoryService::SimpleAD': 'Password',
            'AWS::ElastiCache::ReplicationGroup': 'AuthToken',
            'AWS::IAM::User.LoginProfile': 'Password',
            'AWS::KinesisFirehose::DeliveryStream.RedshiftDestinationConfiguration': 'Password',
            'AWS::OpsWorks::App.Source': 'Password',
            'AWS::OpsWorks::Stack.Source': 'Password',
            'AWS::OpsWorks::Stack.RdsDbInstance': 'DbPassword',
            'AWS::RDS::DBCluster': 'MasterUserPassword',
            'AWS::RDS::DBInstance': 'MasterUserPassword',
            'AWS::Redshift::Cluster': 'MasterUserPassword',
        }

    def check_dyn_ref_value(self, value, path):
        """Chec item type"""
        matches = []

        if isinstance(value, six.string_types):
            if re.match(cfnlint.helpers.REGEX_DYN_REF_SSM_SECURE, value):
                message = 'Dynamic Reference secure strings are not supported for this property at %s' % (
                    '/'.join(map(str, path[:])))
                matches.append(RuleMatch(path[:], message))

        return matches

    def check_value(self, value, path, **kwargs):
        """Check Value"""
        matches = []
        item_type = kwargs.get('item_type', {})
        if item_type in ['Map']:
            if isinstance(value, dict):
                for map_key, map_value in value.items():
                    if not isinstance(map_value, dict):
                        matches.extend(self.check_dyn_ref_value(map_value, path[:] + [map_key]))
        else:
            matches.extend(self.check_dyn_ref_value(value, path[:]))

        return matches

    # pylint: disable=W0613
    # Need to disable for the function to work
    def check_sub(self, value, path, **kwargs):
        """Check Sub Function Dynamic References"""
        matches = []
        if isinstance(value, list):
            if isinstance(value[0], six.string_types):
                matches.extend(self.check_dyn_ref_value(value[0], path[:] + [0]))
        else:
            matches.extend(self.check_dyn_ref_value(value, path[:]))

        return matches

    def check(self, cfn, properties, specs, property_type, path):
        """Check itself"""
        matches = []

        for prop in properties:
            if prop in specs:
                if property_type in self.exceptions:
                    if prop == self.exceptions.get(property_type):
                        continue
                primitive_type = specs.get(prop).get('PrimitiveType')
                if not primitive_type:
                    primitive_type = specs.get(prop).get('PrimitiveItemType')
                if specs.get(prop).get('Type') in ['List', 'Map']:
                    item_type = specs.get(prop).get('Type')
                else:
                    item_type = None
                if primitive_type:
                    matches.extend(
                        cfn.check_value(
                            properties, prop, path[:],
                            check_value=self.check_value,
                            check_sub=self.check_sub,
                            primitive_type=primitive_type,
                            item_type=item_type
                        )
                    )

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = []

        property_specs = self.property_specs.get(property_type, {}).get('Properties', {})
        matches.extend(self.check(cfn, properties, property_specs, property_type, path))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []
        resource_specs = self.resource_specs.get(resource_type, {}).get('Properties', {})
        matches.extend(self.check(cfn, properties, resource_specs, resource_type, path))

        return matches
