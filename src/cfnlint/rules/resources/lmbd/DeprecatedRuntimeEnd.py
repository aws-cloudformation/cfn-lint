"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from datetime import datetime
from cfnlint.rules.resources.lmbd.DeprecatedRuntime import DeprecatedRuntime
from cfnlint.rules import RuleMatch


class DeprecatedRuntimeEnd(DeprecatedRuntime):
    """Check if EOL Lambda Function Runtimes are used"""
    id = 'E2531'
    shortdesc = 'Check if EOL Lambda Function Runtimes are used'
    description = 'Check if an EOL Lambda Runtime is specified and give an error if used. '
    source_url = 'https://docs.aws.amazon.com/lambda/latest/dg/runtime-support-policy.html'
    tags = ['resources', 'lambda', 'runtime']

    def check_runtime(self, runtime_value, path):
        """ Check if the given runtime is valid"""
        matches = []

        runtime = self.deprecated_runtimes.get(runtime_value)
        if runtime:
            if datetime.strptime(runtime['deprecated'], '%Y-%m-%d') < self.current_date:
                message = 'Deprecated runtime ({0}) specified. Updating disabled since {1}. Please consider updating to {2}'
                matches.append(
                    RuleMatch(
                        path,
                        message.format(
                            runtime_value,
                            runtime['deprecated'],
                            runtime['successor'])))
        return matches
