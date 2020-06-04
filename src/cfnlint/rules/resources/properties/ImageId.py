"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class ImageId(CloudFormationLintRule):
    id = 'W2506'
    shortdesc = 'Check if ImageId Parameters have the correct type'
    description = 'See if there are any refs for ImageId to a parameter ' + \
                  'of inappropriate type. Appropriate Types are ' + \
                  '[AWS::EC2::Image::Id, AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>]'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#parmtypes'
    tags = ['parameters', 'ec2', 'imageid']

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
                                              '[%s]' % (paramname, ', '.join(
                                                  map(str, allowed_types)))
                                    tree = ['Parameters', paramname]
                                    matches.append(RuleMatch(tree, message))
                else:
                    message = 'Inappropriate map found for ImageId on %s' % (
                        '/'.join(map(str, imageidtree[:-1])))
                    matches.append(RuleMatch(imageidtree[:-1], message))

        return matches
