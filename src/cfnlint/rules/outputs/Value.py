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
from cfnlint.helpers import RESOURCE_SPECS


class Value(CloudFormationLintRule):
    """Check if Outputs have string values"""
    id = 'E6003'
    shortdesc = 'Outputs have values of strings'
    description = 'Making sure the outputs have strings as values'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html'
    tags = ['outputs']

    def __init__(self):
        resourcespecs = RESOURCE_SPECS['us-east-1']
        self.resourcetypes = resourcespecs['ResourceTypes']

    def match(self, cfn):
        """Check CloudFormation Outputs"""

        matches = []

        template = cfn.template

        getatts = cfn.search_deep_keys('Fn::GetAtt')
        refs = cfn.search_deep_keys('Ref')
        # If using a getatt make sure the attribute of the resource
        # is not of Type List
        for getatt in getatts:
            if getatt[0] == 'Outputs':
                if getatt[2] == 'Value':
                    obj = getatt[-1]
                    if isinstance(obj, list):
                        objtype = template.get('Resources', {}).get(obj[0], {}).get('Type')
                        if objtype:
                            attribute = self.resourcetypes.get(
                                objtype, {}).get('Attributes', {}).get(obj[1], {}).get('Type')
                            if attribute == 'List':
                                if getatt[-4] != 'Fn::Join' and getatt[-3] != 1:
                                    message = 'Output {0} value {1} is of type list'
                                    matches.append(RuleMatch(
                                        getatt,
                                        message.format(getatt[1], '/'.join(obj))
                                    ))

        # If using a ref for an output make sure it isn't a
        # Parameter of Type List
        for ref in refs:
            if ref[0] == 'Outputs':
                if ref[2] == 'Value':
                    obj = ref[-1]
                    if isinstance(obj, six.string_types):
                        param = template.get('Parameters', {}).get(obj)
                        if param:
                            paramtype = param.get('Type')
                            if paramtype:
                                if paramtype.startswith('List<'):
                                    if ref[-4] != 'Fn::Join' and ref[-3] != 1:
                                        message = 'Output {0} value {1} is of type list'
                                        matches.append(RuleMatch(
                                            ref,
                                            message.format(ref[1], obj)
                                        ))

        return matches
