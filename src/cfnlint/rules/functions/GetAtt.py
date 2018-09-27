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
import cfnlint.helpers


class GetAtt(CloudFormationLintRule):
    """Check if GetAtt values are correct"""
    id = 'E1010'
    shortdesc = 'GetAtt validation of parameters'
    description = 'Validates that GetAtt parameters are to valid resources and properties of those resources'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html'
    tags = ['functions', 'getatt']

    def __init__(self):
        resourcespecs = cfnlint.helpers.RESOURCE_SPECS['us-east-1']
        self.resourcetypes = resourcespecs['ResourceTypes']
        self.propertytypes = resourcespecs['PropertyTypes']

    def match(self, cfn):
        """Check CloudFormation GetAtt"""

        matches = []

        getatts = cfn.search_deep_keys('Fn::GetAtt')
        valid_getatts = cfn.get_valid_getatts()
        for getatt in getatts:
            if len(getatt[-1]) < 2:
                message = 'Invalid GetAtt for {0}'
                matches.append(RuleMatch(getatt, message.format('/'.join(map(str, getatt[:-1])))))
                continue
            if isinstance(getatt[-1], six.string_types):
                resname, restype = getatt[-1].split('.')
            else:
                resname = getatt[-1][0]
                restype = '.'.join(getatt[-1][1:])

            if resname in valid_getatts:
                if restype not in valid_getatts[resname] and '*' not in valid_getatts[resname]:
                    message = 'Invalid GetAtt {0}.{1} for resource {2}'
                    matches.append(RuleMatch(
                        getatt[:-1], message.format(resname, restype, getatt[1])))
            else:
                message = 'Invalid GetAtt {0}.{1} for resource {2}'
                matches.append(RuleMatch(getatt, message.format(resname, restype, getatt[1])))

        return matches
