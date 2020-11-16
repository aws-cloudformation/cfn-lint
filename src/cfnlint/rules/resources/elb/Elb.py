"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Elb(CloudFormationLintRule):
    """Check if Elb Resource Properties"""
    id = 'E2503'
    shortdesc = 'Resource ELB Properties'
    description = 'See if Elb Resource Properties are set correctly \
HTTPS has certificate HTTP has no certificate'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-listener.html'
    tags = ['properties', 'elb']

    def __init__(self):
        """ Init """
        super(Elb, self).__init__()
        self.resource_property_types = ['AWS::ElasticLoadBalancingV2::LoadBalancer']

    def check_protocol_value(self, value, path, **kwargs):
        """
            Check Protocol Value
        """
        matches = []
        if isinstance(value, six.string_types):
            if value.upper() not in kwargs['accepted_protocols']:
                message = 'Protocol must be {0} is invalid at {1}'
                matches.append(RuleMatch(path, message.format(
                    (', '.join(kwargs['accepted_protocols'])), ('/'.join(map(str, path))))))
            elif value.upper() in kwargs['certificate_protocols']:
                if not kwargs['certificates']:
                    message = 'Certificates should be specified when using HTTPS for {0}'
                    matches.append(RuleMatch(path, message.format(('/'.join(map(str, path))))))

        return matches

    def get_loadbalancer_type(self, properties):
        """ Check if type is application """
        elb_type = properties.get('Type', 'application')
        if isinstance(elb_type, six.string_types):
            if elb_type == 'application':
                return 'application'
            return 'network'
        return None

    def check_alb_subnets(self, properties, path, scenario):
        """ Validate at least two subnets with ALBs"""
        matches = []
        if self.get_loadbalancer_type(properties) == 'application':
            subnets = properties.get('Subnets')
            if isinstance(subnets, list):
                if len(subnets) < 2:
                    if scenario:
                        message = 'You must specify at least two Subnets for load balancers with type "application" {0}'
                        scenario_text = ' and '.join(
                            ['when condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
                        matches.append(RuleMatch(path, message.format(scenario_text)))
                    else:
                        matches.append(RuleMatch(
                            path[:] + ['Subnets'], 'You must specify at least two Subnets for load balancers with type "application"'))
            subnet_mappings = properties.get('SubnetMappings')
            if isinstance(subnet_mappings, list):
                if len(subnet_mappings) < 2:
                    if scenario:
                        message = 'You must specify at least two SubnetMappings for load balancers with type "application" {0}'
                        scenario_text = ' and '.join(
                            ['when condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
                        matches.append(RuleMatch(path, message.format(scenario_text)))
                    else:
                        matches.append(RuleMatch(
                            path[:] + ['SubnetMappings'], 'You must specify at least two SubnetMappings for load balancers with type "application"'))

        return matches

    def check_loadbalancer_allowed_attributes(self, properties, path, scenario):
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
                'routing.http.desync_mitigation_mode',
                'routing.http.drop_invalid_header_fields.enabled',
                'routing.http2.enabled',
                'waf.fail_open.enabled'
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
                if isinstance(key, six.string_types) and isinstance(value, (six.string_types, bool, six.integer_types)):
                    loadbalancer = self.get_loadbalancer_type(properties)
                    if loadbalancer:
                        if key not in allowed_attributes['all'] and key not in allowed_attributes[loadbalancer]:
                            if scenario:
                                scenario_text = ' and '.join(
                                    ['when condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
                                message = 'Attribute "{0}" not allowed for load balancers with type "{1}" {2}'
                                matches.append(RuleMatch(path, message.format(
                                    key, loadbalancer, scenario_text)))
                            else:
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
                    accepted_protocols=['GENEVE', 'HTTP', 'HTTPS', 'TCP', 'TCP_UDP', 'TLS', 'UDP'],
                    certificate_protocols=['HTTPS', 'TLS'],
                    certificates=result['Value'].get('Certificates')))

        results = cfn.get_resource_properties(
            ['AWS::ElasticLoadBalancing::LoadBalancer', 'Listeners'])
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

        return matches

    def match_resource_properties(self, resource_properties, _, path, cfn):
        """ Check Load Balancers """
        matches = []

        # Play out conditions to determine the relationship between property values
        scenarios = cfn.get_object_without_nested_conditions(resource_properties, path)
        for scenario in scenarios:
            properties = scenario.get('Object')
            if self.get_loadbalancer_type(properties) == 'network':
                if properties.get('SecurityGroups'):
                    if scenario.get('Scenario'):
                        scenario_text = ' and '.join(['when condition "%s" is %s' % (
                            k, v) for (k, v) in scenario.get('Scenario').items()])
                        message = 'Security groups are not supported for load balancers with type "network" {0}'
                        matches.append(RuleMatch(path, message.format(scenario_text)))
                    else:
                        path = path + ['SecurityGroups']
                        matches.append(
                            RuleMatch(path, 'Security groups are not supported for load balancers with type "network"'))

            matches.extend(self.check_alb_subnets(properties, path, scenario.get('Scenario')))
            matches.extend(self.check_loadbalancer_allowed_attributes(
                properties, path, scenario.get('Scenario')))

        return matches
