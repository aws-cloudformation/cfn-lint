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


class Elb(CloudFormationLintRule):
    """Check if Elb Resource Properties"""
    id = 'E2503'
    shortdesc = 'Resource ELB Properties'
    description = 'See if Elb Resource Properties are set correctly \
HTTPS has certificate HTTP has no certificate'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-listener.html'
    tags = ['properties', 'elb']

    def check_protocol_value(self, value, path, **kwargs):
        """
            Check Protocol Value
        """
        matches = []
        if isinstance(value, six.string_types):
            if value.upper() not in kwargs['accepted_protocols']:
                message = 'Protocol must be {0} is invalid at {1}'
                matches.append(RuleMatch(path, message.format((', '.join(kwargs['accepted_protocols'])), ('/'.join(map(str, path))))))
            elif value.upper() in kwargs['certificate_protocols']:
                if not kwargs['certificates']:
                    message = 'Certificates should be specified when using HTTPS for {0}'
                    matches.append(RuleMatch(path, message.format(('/'.join(map(str, path))))))

        return matches

    def is_application_loadbalancer(self, properties):
        """ Check if type is application """
        elb_type = properties.get('Type')
        if not elb_type or elb_type == 'application':
            return True
        return False

    def check_alb_subnets(self, properties, path):
        """ Validate at least two subnets with ALBs"""
        matches = []
        if self.is_application_loadbalancer(properties):
            subnets = properties.get('Subnets')
            if isinstance(subnets, list):
                if len(subnets) < 2:
                    path = path + ['Subnets']
                    matches.append(RuleMatch(path, 'You must specify at least two Subnets for load balancers with type "application"'))
            subnet_mappings = properties.get('SubnetMappings')
            if isinstance(subnet_mappings, list):
                if len(subnet_mappings) < 2:
                    path = path + ['SubnetMappings']
                    matches.append(RuleMatch(path, 'You must specify at least two SubnetMappings for load balancers with type "application"'))

        return matches

    def check_loadbalancer_allowed_attributes(self, properties, path):
        """ Validate loadbalancer attributes per loadbalancer type"""
        matches = []

        allowed_attributes = {
            'all': [
                'access_logs.s3.enabled',
                'access_logs.s3.bucket',
                'access_logs.s3.prefix',
                'deletion_protection.enabled'
            ],
            'application': [
                'idle_timeout.timeout_seconds',
                'routing.http2.enabled'
            ],
            'network': [
                'load_balancing.cross_zone.enabled'
            ]
        }

        loadbalancer_attributes = properties.get('LoadBalancerAttributes')
        if isinstance(loadbalancer_attributes, list):
            for item in loadbalancer_attributes:
                key = item.get('Key')
                value = item.get('Value')
                if isinstance(key, six.string_types) and isinstance(value, (six.string_types, bool, int)):
                    loadbalancer = 'network'
                    if self.is_application_loadbalancer(properties):
                        loadbalancer = 'application'
                    if key not in allowed_attributes['all'] and key not in allowed_attributes[loadbalancer]:
                        message = 'Attribute "{0}" not allowed for load balancers with type "{1}"'
                        matches.append(RuleMatch(path, message.format(key, loadbalancer)))

        return matches

    def match(self, cfn):
        """Check ELB Resource Parameters"""

        matches = []

        results = cfn.get_resource_properties(['AWS::ElasticLoadBalancingV2::Listener'])
        for result in results:
            matches.extend(
                cfn.check_value(
                    result['Value'], 'Protocol', result['Path'],
                    check_value=self.check_protocol_value,
                    accepted_protocols=['HTTP', 'HTTPS', 'TCP', 'TLS'],
                    certificate_protocols=['HTTPS', 'TLS'],
                    certificates=result['Value'].get('Certificates')))

        results = cfn.get_resource_properties(['AWS::ElasticLoadBalancing::LoadBalancer', 'Listeners'])
        for result in results:
            if isinstance(result['Value'], list):
                for index, listener in enumerate(result['Value']):
                    matches.extend(
                        cfn.check_value(
                            listener, 'Protocol', result['Path'] + [index],
                            check_value=self.check_protocol_value,
                            accepted_protocols=['HTTP', 'HTTPS', 'TCP', 'SSL'],
                            certificate_protocols=['HTTPS', 'SSL'],
                            certificates=listener.get('SSLCertificateId')))

        results = cfn.get_resource_properties(['AWS::ElasticLoadBalancingV2::LoadBalancer'])
        for result in results:
            properties = result['Value']
            if not self.is_application_loadbalancer(properties):
                if 'SecurityGroups' in properties:
                    path = result['Path'] + ['SecurityGroups']
                    matches.append(RuleMatch(path, 'Security groups are not supported for load balancers with type "network"'))

            matches.extend(self.check_alb_subnets(properties, result['Path']))
            matches.extend(self.check_loadbalancer_allowed_attributes(properties, result['Path']))

        return matches
