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


class LambdaRuntime(CloudFormationLintRule):
    """Check Lambda Runtime """
    id = 'W2512'
    shortdesc = 'Parameter Lambda Runtime has allowed values set'
    description = 'Check if a parameter that is used for Lambda runtime ' \
                  ' has allowed values constraint defined'
    source_url = 'https://docs.aws.amazon.com/lambda/latest/dg/API_CreateFunction.html#SSS-CreateFunction-request-Runtime'
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
        runtimes = [
            'nodejs', 'nodejs4.3', 'nodejs6.10', 'nodejs8.10', 'java8', 'python2.7',
            'python3.6', 'dotnetcore1.0', 'dotnetcore2.0', 'dotnetcore2.1',
            'nodejs4.3-edge', 'go1.x'
        ]

        if value in parameters:
            parameter = parameters.get(value, {})
            allowed_values = parameter.get('AllowedValues', {})

            if not allowed_values:
                param_path = ['Parameters', value]
                message = 'Parameter should have allowed values at {0}'
                matches.append(RuleMatch(param_path, message.format(('/'.join(param_path)))))
            for index, allowed_value in enumerate(allowed_values):
                if allowed_value not in runtimes:
                    param_path = ['Parameters', value, 'AllowedValues', index]
                    message = 'Allowed value should have valid runtimes at {0}'
                    matches.append(RuleMatch(param_path, message.format(('/'.join(map(str, param_path))))))

        return matches

    def check(self, properties, resource_type, path, cfn):
        """Check itself"""
        matches = []

        matches.extend(
            cfn.check_value(
                properties, 'Runtime', path,
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
