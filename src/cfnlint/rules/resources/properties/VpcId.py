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


class VpcId(CloudFormationLintRule):
    """Check if VPC Parameters are of correct type"""
    id = 'W2505'
    shortdesc = 'Check if VpcID Parameters have the correct type'
    description = 'See if there are any refs for VpcId to a parameter ' + \
                  'of inappropriate type. Appropriate Types are ' + \
                  '[AWS::EC2::VPC::Id, AWS::SSM::Parameter::Value<AWS::EC2::VPC::Id>]'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#parmtypes'
    tags = ['parameters', 'vpcid']

    def match(self, cfn):
        """Check CloudFormation VpcId Parameters"""

        matches = []

        # Build the list of refs
        trees = cfn.search_deep_keys('VpcId')
        parameters = cfn.get_parameter_names()
        allowed_types = [
            'AWS::EC2::VPC::Id',
            'AWS::SSM::Parameter::Value<AWS::EC2::VPC::Id>'
        ]
        fix_param_types = set()
        trees = [x for x in trees if x[0] == 'Resources']
        for tree in trees:
            obj = tree[-1]
            if isinstance(obj, dict):
                if len(obj) == 1:
                    for key in obj:
                        if key == 'Ref':
                            paramname = obj[key]
                            if paramname in parameters:
                                param = cfn.template['Parameters'][paramname]
                                if 'Type' in param:
                                    paramtype = param['Type']
                                    if paramtype not in allowed_types:
                                        fix_param_types.add(paramname)
                else:
                    message = 'Innappropriate map found for vpcid on %s' % (
                        '/'.join(map(str, tree[:-1])))
                    matches.append(RuleMatch(tree[:-1], message))

        for paramname in fix_param_types:
            message = 'Parameter %s should be of type %s' % (paramname, ', '.join(map(str, allowed_types)))
            tree = ['Parameters', paramname]
            matches.append(RuleMatch(tree, message))
        return matches
