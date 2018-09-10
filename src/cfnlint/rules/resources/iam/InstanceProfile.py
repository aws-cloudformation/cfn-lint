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


class InstanceProfile(CloudFormationLintRule):
    """Check if IamInstanceProfile are used"""
    id = 'E2502'
    shortdesc = 'Check if IamInstanceProfile are using the name and not ARN'
    description = 'See if there are any properties IamInstanceProfile' + \
                  'are using name and not ARN'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['properties']

    def match(self, cfn):
        """Check CloudFormation IamInstanceProfile Parameters"""

        matches = []

        # Build the list of keys
        trees = cfn.search_deep_keys('Fn::GetAtt')
        # Filter only resoureces
        # Disable pylint for Pylint 2
        # pylint: disable=W0110
        trees = filter(lambda x: x[0] == 'Resources', trees)
        for tree in trees:
            if any(e == 'IamInstanceProfile' for e in tree):
                obj = tree[-1]
                objtype = cfn.template.get('Resources', {}).get(obj[0], {}).get('Type')
                if objtype:
                    if objtype != 'AWS::IAM::InstanceProfile':
                        message = 'Property IamInstanceProfile should relate to AWS::IAM::InstanceProfile for %s' % (
                            '/'.join(map(str, tree[:-1])))
                        matches.append(RuleMatch(tree[:-1], message))
                    else:
                        if cfn.template.get('Resources', {}).get(tree[1], {}).get('Type') in ['AWS::EC2::SpotFleet']:
                            if obj[1] != 'Arn':
                                message = 'Property IamInstanceProfile should be an ARN for %s' % (
                                    '/'.join(map(str, tree[:-1])))
                                matches.append(RuleMatch(tree[:-1], message))
                        else:
                            if obj[1] == 'Arn':
                                message = 'Property IamInstanceProfile shouldn\'t be an ARN for %s' % (
                                    '/'.join(map(str, tree[:-1])))
                                matches.append(RuleMatch(tree[:-1], message))

        # Search Refs
        trees = cfn.search_deep_keys('Ref')
        # Filter only resoureces
        trees = filter(lambda x: x[0] == 'Resources', trees)
        for tree in trees:
            if any(e == 'IamInstanceProfile' for e in tree):
                obj = tree[-1]
                objtype = cfn.template.get('Resources', {}).get(obj, {}).get('Type')
                if objtype:
                    if objtype != 'AWS::IAM::InstanceProfile':
                        message = 'Property IamInstanceProfile should relate to AWS::IAM::InstanceProfile for %s' % (
                            '/'.join(map(str, tree[:-1])))
                        matches.append(RuleMatch(tree[:-1], message))

        return matches
