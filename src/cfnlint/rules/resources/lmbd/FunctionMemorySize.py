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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class FunctionMemorySize(CloudFormationLintRule):
    """Check if Lambda Function Memory Size"""
    id = 'E2530'
    shortdesc = 'Check Lambda Memory Size Properties'
    description = 'See if Lambda Memory Size is valid'
    source_url = 'https://docs.aws.amazon.com/lambda/latest/dg/API_CreateFunction.html#SSS-CreateFunction-request-MemorySize'
    tags = ['resources', 'lambda']

    min_memory = 128
    max_memory = 3008

    def check_value(self, value, path):
        """ Check memory size value """
        matches = []

        message = 'You must specify a value that is greater than or equal to {0}, ' \
                  'and it must be a multiple of 64. You cannot specify a size ' \
                  'larger than {1}. Error at {2}'

        try:
            value = int(value)

            if value < self.min_memory or value > self.max_memory:
                matches.append(
                    RuleMatch(
                        path, message.format(
                            self.min_memory, self.max_memory, ('/'.join(path)))))
            elif value % 64 != 0:
                matches.append(
                    RuleMatch(
                        path, message.format(
                            self.min_memory, self.max_memory, ('/'.join(path)))))
        except ValueError:
            matches.append(
                RuleMatch(
                    path, message.format(
                        self.min_memory, self.max_memory, ('/'.join(path)))))

        return matches

    def check_memory_size_value(self, value):
        """ Check the memory size value"""
        if value < self.min_memory or value > self.max_memory:
            return False

        return True

    def check_ref(self, value, path, parameters, resources):
        """ Check Memory Size Ref """

        matches = []
        if value in resources:
            message = 'MemorySize can\'t use a Ref to a resource for {0}'
            matches.append(RuleMatch(path, message.format(('/'.join(path)))))
        elif value in parameters:
            parameter = parameters.get(value, {})
            param_type = parameter.get('Type', '')
            if param_type != 'Number':
                param_path = ['Parameters', value, 'Type']
                message = 'Type for Parameter should be Number at {0}'
                matches.append(RuleMatch(param_path, message.format(('/'.join(param_path)))))

            min_value = parameter.get('MinValue')
            max_value = parameter.get('MaxValue')
            allowed_values = parameter.get('AllowedValues')
            if isinstance(allowed_values, list):
                for allowed_value in allowed_values:
                    if isinstance(allowed_value, six.integer_types):
                        if not self.check_memory_size_value(allowed_value):
                            param_path = ['Parameters', value, 'AllowedValues']
                            message = 'AllowedValues should be between {0} and {1} at {2}'
                            matches.append(
                                RuleMatch(
                                    param_path,
                                    message.format(
                                        self.min_memory,
                                        self.max_memory,
                                        ('/'.join(param_path)))))
            else:
                if min_value:
                    if not self.check_memory_size_value(min_value):
                        param_path = ['Parameters', value, 'MinValue']
                        message = 'MinValue should be greater than {0} and equal or less than {1} at {2}'
                        matches.append(
                            RuleMatch(
                                param_path,
                                message.format(
                                    self.min_memory,
                                    self.max_memory,
                                    ('/'.join(param_path)))))
                if max_value:
                    if not self.check_memory_size_value(max_value):
                        param_path = ['Parameters', value, 'MaxValue']
                        message = 'MaxValue should be greater than {0} and equal or less than {1} at {2}'
                        matches.append(
                            RuleMatch(
                                param_path,
                                message.format(
                                    self.min_memory,
                                    self.max_memory,
                                    ('/'.join(param_path)))))

        return matches

    def match(self, cfn):
        """Check Lambda Function Memory Size Resource Parameters"""

        matches = []
        matches.extend(
            cfn.check_resource_property(
                'AWS::Lambda::Function', 'MemorySize',
                check_value=self.check_value,
                check_ref=self.check_ref,
            )
        )

        return matches
