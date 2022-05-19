"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class DomainValidationOptions(CloudFormationLintRule):
    """Check if a certificate's domain validation options are set up correctly"""
    id = 'E3503'
    shortdesc = 'ValidationDomain is superdomain of DomainName'
    description = 'In ValidationDomainOptions, the ValidationDomain must be a superdomain of the DomainName being validated'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-certificatemanager-certificate-domainvalidationoption.html#cfn-certificatemanager-certificate-domainvalidationoption-validationdomain'
    tags = ['certificate', 'certificatemanager', 'domainvalidationoptions', 'validationdomain']

    def __init__(self):
        """ Init """
        super(DomainValidationOptions, self).__init__()
        self.resource_property_types = ['AWS::CertificateManager::Certificate']

    def check_value(self, value, path, **kwargs):
        """ Check value inside the list of DomainValidationOptions"""
        matches = []
        cfn = kwargs.get('cfn')
        if isinstance(value, dict):
            property_sets = cfn.get_object_without_conditions(value)
            for property_set in property_sets:
                properties = property_set.get('Object')
                scenario = property_set.get('Scenario')
                domain_name = properties.get('DomainName', None)
                validation_domain = properties.get('ValidationDomain', None)
                if isinstance(domain_name, str) and isinstance(validation_domain, str):
                    if domain_name == validation_domain:
                        continue

                    if not domain_name.endswith('.' + validation_domain):
                        message = 'ValidationDomain must be a superdomain of DomainName at {}'
                        if scenario is None:
                            matches.append(
                                RuleMatch(path[:] + ['DomainName'], message.format('/'.join(map(str, path)))))
                        else:
                            scenario_text = ' and '.join(
                                ['when condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
                            matches.append(
                                RuleMatch(path[:] + ['DomainName'], message.format('/'.join(map(str, path)) + ' ' + scenario_text)))
        return matches

    def match_resource_properties(self, properties, _, path, cfn):
        matches = []
        matches.extend(cfn.check_value(
            properties, 'DomainValidationOptions', path[:],
            check_value=self.check_value,
            cfn=cfn,
        ))

        return matches
