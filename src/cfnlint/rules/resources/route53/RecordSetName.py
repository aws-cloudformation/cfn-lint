"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class RecordSetName(CloudFormationLintRule):
    """Check if a Route53 Resoruce Records Name is valid with a HostedZoneName"""
    id = 'E3041'
    shortdesc = 'RecordSet HostedZoneName is a superdomain of Name'
    description = 'In a RecordSet, the HostedZoneName must be a superdomain of the Name being validated'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-name'
    tags = ['resource', 'properties', 'route53']

    def __init__(self):
        """ Init """
        super(RecordSetName, self).__init__()
        self.resource_property_types = ['AWS::Route53::RecordSet']

    def match_resource_properties(self, properties, _, path, cfn):
        matches = []

        property_sets = cfn.get_object_without_conditions(properties, ['Name', 'HostedZoneName'])
        for property_set in property_sets:
            props = property_set.get('Object')
            scenario = property_set.get('Scenario')
            name = props.get('Name', None)
            hz_name = props.get('HostedZoneName', None)
            if isinstance(name, str) and isinstance(hz_name, str):
                if hz_name[-1] != '.':
                    message = 'HostedZoneName must end in a dot at {}'
                    if scenario is None:
                        matches.append(
                            RuleMatch(path[:] + ['HostedZoneName'], message.format('/'.join(map(str, path)))))
                    else:
                        scenario_text = ' and '.join(
                            ['when condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
                        matches.append(
                            RuleMatch(path[:] + ['HostedZoneName'], message.format('/'.join(map(str, path)) + ' ' + scenario_text)))
                if hz_name[-1] == '.':
                    hz_name = hz_name[:-1]
                if name[-1] == '.':
                    name = name[:-1]

                if hz_name not in [name, name[-len(hz_name):]]:
                    message = 'Name must be a superdomain of HostedZoneName at {}'
                    if scenario is None:
                        matches.append(
                            RuleMatch(path[:] + ['Name'], message.format('/'.join(map(str, path)))))
                    else:
                        scenario_text = ' and '.join(
                            ['when condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
                        matches.append(
                            RuleMatch(path[:] + ['Name'], message.format('/'.join(map(str, path)) + ' ' + scenario_text)))

        return matches
