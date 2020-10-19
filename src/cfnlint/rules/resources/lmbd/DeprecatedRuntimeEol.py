"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from datetime import datetime
from cfnlint.rules.resources.lmbd.DeprecatedRuntime import DeprecatedRuntime
from cfnlint.rules import RuleMatch


class DeprecatedRuntimeEol(DeprecatedRuntime):
    """Check if EOL Lambda Function Runtimes are used"""
    id = 'W2531'
    shortdesc = 'Check if EOL Lambda Function Runtimes are used'
    description = 'Check if an EOL Lambda Runtime is specified and give a warning if used. '
    source_url = 'https://docs.aws.amazon.com/lambda/latest/dg/runtime-support-policy.html'
    tags = ['resources', 'lambda', 'runtime']

    def check_runtime(self, runtime_value, path):
        """ Check if the given runtime is valid"""
        matches = []

        runtime = self.deprecated_runtimes.get(runtime_value)
        if runtime:
            if datetime.strptime(runtime['eol'], '%Y-%m-%d') < self.current_date and datetime.strptime(runtime['deprecated'], '%Y-%m-%d') > self.current_date:
                message = 'EOL runtime ({0}) specified. Runtime is EOL since {1} and updating will be disabled at {2}. Please consider updating to {3}'
                matches.append(
                    RuleMatch(
                        path,
                        message.format(
                            runtime_value,
                            runtime['eol'],
                            runtime['deprecated'],
                            runtime['successor'])))
        return matches
