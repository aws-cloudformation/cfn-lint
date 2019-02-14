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


class DefaultRef(CloudFormationLintRule):
    """Check if Parameter defaults don't use Refs"""
    id = 'E2014'
    shortdesc = 'Default value cannot use Refs'
    description = 'Check if Refs are not used in Parameter Defaults'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html'
    tags = ['parameters']

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = []

        ref_objs = cfn.search_deep_keys('Ref')

        # Filter out the Parameters
        parameter_refs = [x for x in ref_objs if x[0] == 'Parameters']

        for parameter_ref in parameter_refs:
            message = 'Invalid value ({}), Ref cannot be used in Parameters'
            matches.append(RuleMatch(parameter_ref, message.format(parameter_ref[-1])))

        return matches
