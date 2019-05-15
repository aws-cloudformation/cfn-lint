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
from datetime import datetime
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class DeprecatedRuntime(CloudFormationLintRule):
    """Check if EOL Lambda Function Runtimes are used"""
    id = 'W2530'
    shortdesc = 'Check if EOL Lambda Function Runtimes are used'
    description = 'Check if an EOL Lambda Runtime is specified and give a warning if used. '
    source_url = 'https://docs.aws.amazon.com/lambda/latest/dg/runtime-support-policy.html'
    tags = ['resources', 'lambda', 'runtime']

    def __init__(self):
        """Init"""
        super(DeprecatedRuntime, self).__init__()
        self.config_definition = {
            'check_eol_date': {
                'default': True,
                'type': 'boolean'
            }
        }
        self.configure()

    current_date = datetime.today()

    deprecated_runtimes = {
        'dotnetcore2.0': {
            'eol': '2019-04-30',
            'deprecated': '2019-05-30',
            'successor': 'dotnetcore2.0'
        },
        'nodejs': {
            'eol': '2016-10-31',
            'deprecated': '2016-10-31',
            'successor': 'nodejs10.x'
        },
        'nodejs4.3': {
            'eol': '2018-04-30',
            'deprecated': '2019-04-30',
            'successor': 'nodejs10.x'
        },
        'nodejs6.10': {
            'eol': '2019-04-30',
            'deprecated': '2019-06-30',
            'successor': 'nodejs10.x'
        }
    }

    def check_runtime(self, runtime_value, path):
        """ Check if the given runtime is valid"""
        matches = []

        runtime = self.deprecated_runtimes.get(runtime_value)
        if runtime:
            if datetime.strptime(runtime['deprecated'], '%Y-%m-%d') < self.current_date:
                message = 'Deprecated runtime ({0}) specified. Updating disabled since {1}, please consider to update to {2}'
                matches.append(
                    RuleMatch(
                        path,
                        message.format(
                            runtime_value,
                            runtime['deprecated'],
                            runtime['successor'])))

            elif self.config['check_eol_date']:
                if datetime.strptime(runtime['eol'], '%Y-%m-%d') < self.current_date:
                    message = 'EOL runtime ({0}) specified. Runtime is EOL since {1} and updating will be disabled at {2}, please consider to update to {3}'
                    matches.append(
                        RuleMatch(
                            path,
                            message.format(
                                runtime_value,
                                runtime['eol'],
                                runtime['deprecated'],
                                runtime['successor'])))
        return matches


    def check_value(self, value, path):
        """Check Lambda Runtime value """
        matches = []
        matches.extend(self.check_runtime(value, path))
        return matches

    def check_ref(self, value, path, parameters, resources): # pylint: disable=W0613
        """Check Lambda Runtime Ref value """

        matches = []
        if value in parameters:
            parameter = parameters.get(value, {})
            param_path = ['Parameters', value]

            # Validate the Default
            default_value = parameter.get('Default', '')
            matches.extend(self.check_runtime(default_value, param_path + ['Default']))

            # Validate AllowedValues
            allowed_values = parameter.get('AllowedValues')
            if isinstance(allowed_values, list):
                param_path = param_path + ['AllowedValues']
                for index, allowed_value in enumerate(allowed_values):
                    matches.extend(self.check_runtime(allowed_value, param_path + [index]))

        return matches

    def match(self, cfn):
        """Check if EOL Lambda Function Runtimes are used"""

        matches = []
        matches.extend(
            cfn.check_resource_property(
                'AWS::Lambda::Function', 'Runtime',
                check_value=self.check_value,
                check_ref=self.check_ref,
            )
        )

        return matches
