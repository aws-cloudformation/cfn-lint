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
from cfnlint.helpers import load_resources
from cfnlint import CloudFormationLintRule


class DeprecatedRuntime(CloudFormationLintRule):
    """Check if EOL Lambda Function Runtimes are used"""

    def __init__(self):
        """Init"""
        super(DeprecatedRuntime, self).__init__()
        self.resource_property_types.append('AWS::Lambda::Function')
        self.deprecated_runtimes = load_resources('data/AdditionalSpecs/LmbdRuntimeLifecycle.json')

    current_date = datetime.today()

    def check_runtime(self, runtime_value, path):
        """ Check if the given runtime is valid"""
        self.logger.debug(runtime_value, path)
        return []

    def check_value(self, value, path):
        """Check Lambda Runtime value """
        matches = []
        matches.extend(self.check_runtime(value, path))
        return matches

    def check_ref(self, value, path, parameters, resources):  # pylint: disable=W0613
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

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        matches.extend(
            cfn.check_value(
                obj=properties, key='Runtime',
                path=path[:],
                check_value=self.check_value,
                check_ref=self.check_ref
            ))

        return matches
