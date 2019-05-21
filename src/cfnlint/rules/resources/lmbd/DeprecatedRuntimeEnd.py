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
from cfnlint.rules.resources.lmbd.DeprecatedRuntime import DeprecatedRuntime
from cfnlint import RuleMatch


class DeprecatedRuntimeEnd(DeprecatedRuntime):
    """Check if EOL Lambda Function Runtimes are used"""
    id = 'E2531'
    shortdesc = 'Check if EOL Lambda Function Runtimes are used'
    description = 'Check if an EOL Lambda Runtime is specified and give a warning if used. '
    source_url = 'https://docs.aws.amazon.com/lambda/latest/dg/runtime-support-policy.html'
    tags = ['resources', 'lambda', 'runtime']

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
        return matches
