"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class SecurityGroupIngress(CloudFormationLintRule):
    """Check if EC2 Security Group Ingress Properties"""
    id = 'E2506'
    shortdesc = 'Resource EC2 Security Group Ingress Properties'
    description = 'See if EC2 Security Group Ingress Properties are set correctly. ' \
                  'Check that "SourceSecurityGroupId" or "SourceSecurityGroupName" are ' \
                  ' are exclusive and using the type of Ref or GetAtt '
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html'
    tags = ['resources', 'ec2', 'securitygroup']

    def check_ingress_rule(self, vpc_id, properties, path):
        """Check ingress rule"""

        matches = []
        if vpc_id:

            # Check that SourceSecurityGroupName isn't specified
            if properties.get('SourceSecurityGroupName', None):
                path_error = path[:] + ['SourceSecurityGroupName']
                message = 'SourceSecurityGroupName shouldn\'t be specified for ' \
                          'Vpc Security Group at {0}'
                matches.append(
                    RuleMatch(path_error, message.format('/'.join(map(str, path_error)))))

        else:

            if properties.get('SourceSecurityGroupId', None):
                path_error = path[:] + ['SourceSecurityGroupId']
                message = 'SourceSecurityGroupId shouldn\'t be specified for ' \
                          'Non-Vpc Security Group at {0}'
                matches.append(
                    RuleMatch(path_error, message.format('/'.join(map(str, path_error)))))

        return matches

    def match(self, cfn):
        """Check EC2 Security Group Ingress Resource Parameters"""

        matches = []

        resources = cfn.get_resources(resource_type='AWS::EC2::SecurityGroup')
        for resource_name, resource_object in resources.items():
            properties = resource_object.get('Properties', {})
            if properties:
                vpc_id = properties.get('VpcId', None)
                ingress_rules = properties.get('SecurityGroupIngress')
                if isinstance(ingress_rules, list):
                    for index, ingress_rule in enumerate(ingress_rules):
                        path = [
                            'Resources', resource_name, 'Properties',
                            'SecurityGroupIngress', index
                        ]
                        matches.extend(
                            self.check_ingress_rule(
                                vpc_id=vpc_id,
                                properties=ingress_rule,
                                path=path
                            )
                        )

        resources = None
        resources = cfn.get_resources(resource_type='AWS::EC2::SecurityGroupIngress')
        for resource_name, resource_object in resources.items():
            properties = resource_object.get('Properties', {})
            group_id = properties.get('GroupId', None)
            path = ['Resources', resource_name, 'Properties']
            if group_id:
                vpc_id = 'vpc-1234567'
            else:
                vpc_id = None

            if properties:
                path = ['Resources', resource_name, 'Properties']
                matches.extend(
                    self.check_ingress_rule(
                        vpc_id=vpc_id,
                        properties=properties,
                        path=path
                    )
                )
        return matches
