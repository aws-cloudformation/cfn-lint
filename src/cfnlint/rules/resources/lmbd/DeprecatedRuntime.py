"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from datetime import datetime
from cfnlint.helpers import load_resource
from cfnlint.data import AdditionalSpecs
from cfnlint.rules import CloudFormationLintRule


class DeprecatedRuntime(CloudFormationLintRule):
    """Check if EOL Lambda Function Runtimes are used"""

    def __init__(self):
        """Init"""
        super(DeprecatedRuntime, self).__init__()
        self.resource_property_types.append('AWS::Lambda::Function')
        self.deprecated_runtimes = load_resource(AdditionalSpecs, 'LmbdRuntimeLifecycle.json')

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
