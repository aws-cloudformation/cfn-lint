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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class ServerlessTransform(CloudFormationLintRule):
    """Check if Serverless Resources exist without the Serverless Transform"""

    id = 'E3038'
    shortdesc = 'Check if Serverless Resources have Serverless Transform'
    description = (
        'Check that a template with Serverless Resources also includes the Serverless Transform'
    )
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['resources', 'transform']

    def match(self, cfn):
        """Check CloudFormation Resources"""

        matches = []

        transforms = cfn.template.get('Transform', [])
        if not isinstance(transforms, list):
            transforms = [transforms]
        has_serverless_transform = any(
            transform == 'AWS::Serverless-2016-10-31' for transform in transforms
        )
        if has_serverless_transform:
            return matches

        for resource_name, resource_values in cfn.get_resources().items():
            resource_type = resource_values['Type']
            if resource_type.startswith('AWS::Serverless::'):
                message = 'Serverless Transform required for Type {0} for resource {1}'
                matches.append(
                    RuleMatch(['Transform'], message.format(resource_type, resource_name))
                )
                break
        return matches
