from collections import defaultdict
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
import cfnlint.helpers
import pprint


class RouteTableAssociation(CloudFormationLintRule):
    """Check only one route table association defined per subnet"""
    id = 'E4001'
    shortdesc = 'Check to ensure API Gateways have an authorizer'
    description = 'Check to ensure API Gateways have an authorizer'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html'
    tags = ['resources', 'api gateway', 'authorizers']

    def match(self, cfn):
        """Check for authorizers"""
        matches = []
        resources = cfn.get_resources(['AWS::ApiGateway::RestApi'])
        #print(resources)
        for resource_name, resource in resources.items():
            properties = resource.get('Properties')
            failed_resources = []
            if properties:
                body = properties.get('Body')
                parameter = properties.get('Parameters')
                endpoint = parameter.get('endpointConfigurationTypes')
                if not body.get('securityDefinitions') and not endpoint == 'PRIVATE':
                    failed_resources.append(resource)
                if failed_resources:
                    path = ['Resources', resource_name, 'Properties']
                    message = 'Ridgeline Security: You are missing an authorizer on a public facing endpoint. This could potentially expose all of our data to the internet. No bueno. Please contact @security with any questions'
                    matches.append(
                        RuleMatch(path, message.format(resource_name, ', '.join(str(failed_resources)))))
        return matches
