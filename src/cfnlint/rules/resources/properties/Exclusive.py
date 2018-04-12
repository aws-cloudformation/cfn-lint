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
import cfnlint.helpers


class Exclusive(CloudFormationLintRule):
    """Check Properties Resource Configuration"""
    id = 'E2520'
    shortdesc = 'Check Properties that are mutually exclusive'
    description = 'Making sure CloudFormation properties ' + \
                  'that are exclusive are not defined'
    tags = ['base', 'resources']

    def __init__(self):
        """Init"""
        self.exlusivespec = cfnlint.helpers.load_resources('data/ResourcePropertiesExclusive.json')

    def match(self, cfn):
        """Check CloudFormation Properties"""
        matches = list()

        for excl_type, excl_values in self.exlusivespec.items():
            for res_name, res_value in cfn.get_resources(excl_type).items():
                for excl_name, excl_value in excl_values.items():
                    properties = res_value.get('Properties', {})
                    if excl_name in properties:
                        for prop_name in excl_value:
                            if prop_name in res_value['Properties']:
                                message = "Parameter {0} shouldn't exist with {1} for {2}"
                                matches.append(RuleMatch(
                                    ['Resources', res_name, 'Properties', excl_name],
                                    message.format(excl_name, prop_name, res_name)
                                ))

        return matches
