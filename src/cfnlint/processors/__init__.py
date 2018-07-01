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
import os
import cfnlint.helpers

DEFAULT_PROCESSORSDIR = os.path.join(os.path.dirname(__file__))


class CloudFormationProcessor(object):
    """CloudFormation Transform Support"""
    type = ''

    run = None

    def run_all(self, cfn):
        """Generic transform"""
        if not self.run:
            return []

        return self.run(cfn)  # pylint: disable=E1102


class ProcessorsCollection(object):
    """Collection of processors"""

    def __init__(self):
        self.processors = cfnlint.helpers.load_plugins(
            os.path.expanduser(DEFAULT_PROCESSORSDIR), 'cfnlint.processors', 'CloudFormationProcessor')

    def __iter__(self):
        return iter(self.processors)

    def __len__(self):
        return len(self.processors)

    def extend(self, more):
        """Extend rules"""
        self.processors.extend(more)

    def run(self, cfn):
        """Run the transforms"""
        matches = list()

        for processor in self.processors:
            if processor.type == 'FnIf':
                matches = processor.run(cfn)

        for match in matches:
            for processor in self.processors:
                if processor.type == 'NoValue':
                    match = processor.run(match)

        return matches
