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


class FunctionRuntime(CloudFormationLintRule):
    """Check if Lambda Function Memory Size"""
    id = 'E2531'
    shortdesc = 'Check Lambda Runtime Properties'
    description = 'See if Lambda Runtime is in valid'
    source_url = 'https://docs.aws.amazon.com/lambda/latest/dg/API_CreateFunction.html#SSS-CreateFunction-request-Runtime'
    tags = ['resources', 'lambda']

    runtimes = [
        'nodejs', 'nodejs4.3', 'nodejs6.10', 'nodejs8.10', 'java8', 'python2.7',
        'python3.6', 'dotnetcore1.0', 'dotnetcore2.0', 'dotnetcore2.1',
        'nodejs4.3-edge', 'go1.x'
    ]

    def check_value(self, value, path):
        """ Check runtime value """
        matches = []

        message = 'You must specify a valid value for runtime ({0}) at {1}'

        if value not in self.runtimes:
            matches.append(RuleMatch(path, message.format(value, ('/'.join(path)))))

        return matches

    def check_ref(self, value, path, parameters, resources):
        """ Check Memory Size Ref """

        matches = []
        if value in resources:
            message = 'Runtime can\'t use a Ref to a resource for {0}'
            matches.append(RuleMatch(path, message.format(('/'.join(path)))))
        elif value in parameters:
            parameter = parameters.get(value, {})
            param_type = parameter.get('Type', '')

            if param_type != 'String':
                param_path = ['Parameters', value, 'Type']
                message = 'Type for Parameter should be String at {0}'
                matches.append(RuleMatch(param_path, message.format(('/'.join(param_path)))))

        return matches

    def match(self, cfn):
        """Check Lambda Function Memory Size Resource Parameters"""

        matches = []
        matches.extend(
            cfn.check_resource_property(
                'AWS::Lambda::Function', 'Runtime',
                check_value=self.check_value,
                check_ref=self.check_ref,
            )
        )

        return matches
