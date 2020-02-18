"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

    def match(self, cfn):
        """Check CertificateManager:Certificate:ValidationDomainOptions"""

        matches = []

        results = cfn.get_resource_properties(['AWS::CertificateManager::Certificate', 'DomainValidationOptions'])
        for result in results:
            if result['Value'][0]['DomainName'] == result['Value'][0]['ValidationDomain']:
                continue

            if not result['Value'][0]['DomainName'].endswith('.' + result['Value'][0]['ValidationDomain']):
                path = result['Path']
                matches.append(RuleMatch(path, 'ValidationDomain must be a superdomain of DomainName'))

        return matches
