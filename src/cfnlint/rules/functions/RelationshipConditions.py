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
import six
from cfnlint.helpers import PSEUDOPARAMS
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class RelationshipConditions(CloudFormationLintRule):
    """Check if Ref/GetAtt values are available via conditions"""
    id = 'W1001'
    shortdesc = 'Ref/GetAtt to resource that is available when conditions are applied'
    description = 'Check the Conditions that affect a Ref/GetAtt to make sure ' \
                  'the resource being related to is available when there is a resource ' \
                  'condition.'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html'
    tags = ['resources', 'relationships']

    def match(self, cfn):
        """Check CloudFormation Ref/GetAtt for Conditions"""

        matches = []

        # Start with Ref checks
        ref_objs = cfn.search_deep_keys('Ref')
        for ref_obj in ref_objs:
            value = ref_obj[-1]
            if value not in PSEUDOPARAMS:
                scenarios = cfn.is_resource_available(ref_obj, value)
                for scenario in scenarios:
                    scenario_text = ' and '.join(
                        ['when condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
                    message = 'Ref to resource "{0}" that may not be available {1} at {2}'
                    matches.append(
                        RuleMatch(
                            ref_obj[:-1],
                            message.format(
                                value,
                                scenario_text,
                                '/'.join(map(str, ref_obj[:-1])))))

        # The do GetAtt
        getatt_objs = cfn.search_deep_keys('Fn::GetAtt')
        for getatt_obj in getatt_objs:
            value_obj = getatt_obj[-1]
            value = None
            if isinstance(value_obj, list):
                value = value_obj[0]
            elif isinstance(value_obj, six.string_types):
                value = value_obj.split('.')[0]
            if value:
                if value not in PSEUDOPARAMS:
                    scenarios = cfn.is_resource_available(getatt_obj, value)
                    for scenario in scenarios:
                        scenario_text = ' and '.join(
                            ['when condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
                        message = 'GetAtt to resource "{0}" that may not be available {1} at {2}'
                        matches.append(
                            RuleMatch(
                                getatt_obj[:-1],
                                message.format(
                                    value,
                                    scenario_text,
                                    '/'.join(map(str, getatt_obj[:-1])))))

        return matches
