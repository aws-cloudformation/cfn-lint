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


class FunctionMemorySize(CloudFormationLintRule):
    """Check if Lambda Function Memory Size"""
    id = 'E2530'
    shortdesc = 'Check Lambda Memory Size Properties'
    description = 'See if Lambda Memory Size is valid'
    tags = ['base', 'resources', 'lambda']

    def check_value(self, value, path):
        """ Check memory size value """
        matches = list()

        message = 'You must specify a value that is greater than or equal to 128, ' \
                  'and it must be a multiple of 64. You cannot specify a size ' \
                  'larger than 1536. The default value is 128 MB at {0}'

        try:
            value = int(value)

            if value < 128 or value > 1536:
                matches.append(RuleMatch(path, message.format(value, ('/'.join(path)))))
            elif value % 64 != 0:
                matches.append(RuleMatch(path, message.format(value, ('/'.join(path)))))
        except ValueError:
            matches.append(RuleMatch(path, message.format(value, ('/'.join(path)))))

        return matches

    def check_ref(self, value, path, parameters, resources):
        """ Check Memory Size Ref """

        matches = list()
        if value in resources:
            message = 'MemorySize can\'t use a Ref to a resource for {0}'
            matches.append(RuleMatch(path, message.format(('/'.join(path)))))
        elif value in parameters:
            parameter = parameters.get(value, {})
            param_type = parameter.get('Type', '')
            min_value = parameter.get('MinValue', 0)
            max_value = parameter.get('MaxValue', 999999)
            if param_type != 'Number' or min_value < 128 or max_value > 1536:
                param_path = ['Parameters', value, 'Type']
                message = 'Type for Parameter should be Integer, MinValue should be ' \
                          'at least 128, and MaxValue equal or less than 1536 at {0}'
                matches.append(RuleMatch(param_path, message.format(('/'.join(param_path)))))

        return matches

    def match(self, cfn):
        """Check Lambda Function Memory Size Resource Parameters"""

        matches = list()
        matches.extend(
            cfn.check_resource_property(
                'AWS::Lambda::Function', 'MemorySize',
                check_value=self.check_value,
                check_ref=self.check_ref,
            )
        )

        return matches
