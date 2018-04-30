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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class Elb(CloudFormationLintRule):
    """Check if Elb Resource Properties"""
    id = 'E2503'
    shortdesc = 'Resource ELB Properties'
    description = 'See if Elb Resource Properties are set correctly \
HTTPS has certificate HTTP has no certificate'
    tags = ['base', 'properties', 'elb']

    def match(self, cfn):
        """Check ELB Resource Parameters"""

        matches = list()

        results = cfn.get_resource_properties(['AWS::ElasticLoadBalancingV2::Listener'])
        for result in results:
            protocol = result['Value'].get('Protocol')
            if protocol:
                if protocol not in ['HTTP', 'HTTPS', 'TCP']:
                    message = 'Protocol is invalid for {0}'
                    path = result['Path'] + ['Protocol']
                    matches.append(RuleMatch(path, message.format(('/'.join(result['Path'])))))
                elif protocol in ['HTTPS']:
                    certificate = result['Value'].get('Certificates')
                    if not certificate:
                        message = 'Certificates should be specified when using HTTPS for {0}'
                        path = result['Path'] + ['Protocol']
                        matches.append(RuleMatch(path, message.format(('/'.join(result['Path'])))))

        results = cfn.get_resource_properties(['AWS::ElasticLoadBalancing::LoadBalancer', 'Listeners'])
        for result in results:
            if isinstance(result['Value'], list):
                for index, listener in enumerate(result['Value']):
                    protocol = listener.get('Protocol')
                    if protocol:
                        if protocol not in ['HTTP', 'HTTPS', 'TCP', 'SSL']:
                            message = 'Protocol is invalid for {0}'
                            path = result['Path'] + [index, 'Protocol']
                            matches.append(RuleMatch(path, message.format(('/'.join(result['Path'])))))
                        elif protocol in ['HTTPS', 'SSL']:
                            certificate = listener.get('SSLCertificateId')
                            if not certificate:
                                message = 'Certificates should be specified when using HTTPS for {0}'
                                path = result['Path'] + [index, 'Protocol']
                                matches.append(RuleMatch(path, message.format(('/'.join(result['Path'])))))

        return matches
