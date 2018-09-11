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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class ImageId(CloudFormationLintRule):
    """Check if Parameters are used"""
    id = 'W2506'
    shortdesc = 'Check if ImageId Parameters have the correct type'
    description = 'See if there are any refs for ImageId to a parameter ' + \
                  'of inappropriate type. Appropriate Types are ' + \
                  '[AWS::EC2::Image::Id, AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>]'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#parmtypes'
    tags = ['parameters', 'imageid']

    def match(self, cfn):
        """Check CloudFormation ImageId Parameters"""

        matches = []

        # Build the list of refs
        imageidtrees = cfn.search_deep_keys('ImageId')
        valid_refs = cfn.get_valid_refs()
        allowed_types = [
            'AWS::EC2::Image::Id',
            'AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>'
        ]
        # Filter only resoureces
        imageidtrees = [x for x in imageidtrees if x[0] == 'Resources']
        for imageidtree in imageidtrees:
            imageidobj = imageidtree[-1]
            if isinstance(imageidobj, dict):
                if len(imageidobj) == 1:
                    for key, paramname in imageidobj.items():
                        if key == 'Ref':
                            if paramname in valid_refs:
                                if valid_refs[paramname]['Type'] not in allowed_types:
                                    message = 'Parameter %s should be of type ' \
                                              '[%s]' % (paramname, ', '.join(map(str, allowed_types)))
                                    tree = ['Parameters', paramname]
                                    matches.append(RuleMatch(tree, message))
                else:
                    message = 'Inappropriate map found for ImageId on %s' % (
                        '/'.join(map(str, imageidtree[:-1])))
                    matches.append(RuleMatch(imageidtree[:-1], message))

        return matches
