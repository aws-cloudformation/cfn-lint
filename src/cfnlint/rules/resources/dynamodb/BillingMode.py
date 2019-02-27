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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class BillingMode(CloudFormationLintRule):
    """Check DynamoDB BillingMode Configuration"""
    id = 'E3024'
    shortdesc = 'Validate that ProvisionedThroughput is not specified with BillingMode PAY_PER_REQUEST'
    description = 'When using ProvisionedThroughput with BillingMode PAY_PER_REQUEST will result in ' \
                  'BillingMode being changed to PROVISIONED'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html'
    tags = ['resources', 'dynamodb', 'provisioned_throughput', 'billing_mode']

    def __init__(self):
        """Init"""
        super(BillingMode, self).__init__()
        self.resource_property_types = ['AWS::DynamoDB::Table']

    def check(self, properties, path, cfn):
        """Check itself"""
        matches = []
        property_sets = cfn.get_object_without_conditions(properties)
        for property_set in property_sets:
            billing_mode = property_set.get('Object').get('BillingMode')
            if billing_mode == 'PAY_PER_REQUEST':
                if 'ProvisionedThroughput' in property_set.get('Object'):
                    if property_set['Scenario'] is None:
                        message = '"ProvisionedThroughput" must not be specified when BillingMode is set to "PAY_PER_REQUEST" at {0}'
                        matches.append(RuleMatch(
                            path,
                            message.format('/'.join(map(str, path)))
                        ))
                    else:
                        scenario_text = ' and '.join(['when condition "%s" is %s' % (k, v) for (k, v) in property_set['Scenario'].items()])
                        message = '"ProvisionedThroughput" must not be specified when BillingMode is set to "PAY_PER_REQUEST" {0} at {1}'
                        matches.append(RuleMatch(
                            path,
                            message.format(scenario_text, '/'.join(map(str, path)))
                        ))

        return matches

    def match_resource_properties(self, properties, _, path, cfn):
        """Match for sub properties"""
        matches = []

        matches.extend(self.check(properties, path, cfn))

        return matches
