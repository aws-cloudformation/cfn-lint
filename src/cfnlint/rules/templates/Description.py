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
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class Description(CloudFormationLintRule):
    """Check Template Description is only a String"""
    id = 'E1004'
    shortdesc = 'Template description can only be a string'
    description = 'Template description can only be a string'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-description-structure.html'
    tags = ['description']

    def match(self, cfn):
        """Basic Matching"""
        matches = []

        description = cfn.template.get('Description')

        if description:
            if not isinstance(description, six.string_types):
                message = 'Description can only be a string'
                matches.append(RuleMatch(['Description'], message))
        return matches
