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


class Configuration(CloudFormationLintRule):
    """Check if Parameters are configured correctly"""
    id = 'E2001'
    shortdesc = 'Parameters have appropriate properties'
    description = 'Making sure the parameters are properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html'
    tags = ['parameters']

    valid_keys = [
        'AllowedPattern',
        'AllowedValues',
        'ConstraintDescription',
        'Default',
        'Description',
        'MaxLength',
        'MaxValue',
        'MinLength',
        'MinValue',
        'NoEcho',
        'Type'
    ]

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = []

        for paramname, paramvalue in cfn.get_parameters().items():
            for propname, _ in paramvalue.items():
                if propname not in self.valid_keys:
                    message = 'Parameter {0} has invalid property {1}'
                    matches.append(RuleMatch(
                        ['Parameters', paramname, propname],
                        message.format(paramname, propname)
                    ))

        return matches
