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


class LambdaMemorySize(CloudFormationLintRule):
    """Check Lambda Memory Size """
    id = 'W2510'
    shortdesc = 'Parameter Memory Size attributes should have max and min'
    description = 'Check if a parameter that is used for Lambda memory size ' \
                  ' should have a min and max size that matches Lambda constraints'
    source_url = 'https://docs.aws.amazon.com/lambda/latest/dg/API_CreateFunction.html#SSS-CreateFunction-request-MemorySize'
    tags = ['parameters', 'lambda']

    def __init__(self):
        """Init"""
        resource_type_specs = [
            'AWS::Lambda::Function',
        ]

        for resoruce_type_spec in resource_type_specs:
            self.resource_property_types.append(resoruce_type_spec)

    # pylint: disable=W0613
    def check_lambda_memory_size_ref(self, value, path, parameters, resources):
        """Check ref for VPC"""
        matches = []

        if value in parameters:
            parameter = parameters.get(value)
            min_value = parameter.get('MinValue')
            max_value = parameter.get('MaxValue')
            allowed_values = parameter.get('AllowedValues')
            if (not min_value or not max_value) and (not allowed_values):
                param_path = ['Parameters', value]
                message = 'Lambda Memory Size parameters should use MinValue, MaxValue ' \
                          'or AllowedValues at {0}'
                matches.append(
                    RuleMatch(
                        param_path,
                        message.format(('/'.join(param_path)))))

        return matches

    def check(self, properties, resource_type, path, cfn):
        """Check itself"""
        matches = []

        matches.extend(
            cfn.check_value(
                properties, 'MemorySize', path,
                check_value=None, check_ref=self.check_lambda_memory_size_ref,
                check_find_in_map=None, check_split=None, check_join=None
            )
        )

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        matches.extend(self.check(properties, resource_type, path, cfn))

        return matches
