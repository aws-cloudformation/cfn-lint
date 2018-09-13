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
import re
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch
from cfnlint.helpers import REGEX_DYN_REF_SSM, REGEX_DYN_REF


class Password(CloudFormationLintRule):
    """Check if Password Properties are properly configured"""
    id = 'W2501'
    shortdesc = 'Check if Password Properties are correctly configured'
    description = 'Password properties should be strings and if parameter using NoEcho'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#creds'
    tags = ['parameters', 'passwords']

    def match(self, cfn):
        """Check CloudFormation Password Parameters"""

        matches = []
        password_properties = ['Password', 'DbPassword', 'MasterUserPassword']

        parameters = cfn.get_parameter_names()
        fix_params = set()
        for password_property in password_properties:
            # Build the list of refs
            trees = cfn.search_deep_keys(password_property)
            trees = [x for x in trees if x[0] == 'Resources']
            for tree in trees:
                obj = tree[-1]
                if isinstance(obj, (six.string_types)):
                    if re.match(REGEX_DYN_REF, obj):
                        if re.match(REGEX_DYN_REF_SSM, obj):
                            message = 'Password should use a secure dynamic reference for %s' % (
                                '/'.join(map(str, tree[:-1])))
                            matches.append(RuleMatch(tree[:-1], message))
                    else:
                        message = 'Password shouldn\'t be hardcoded for %s' % (
                            '/'.join(map(str, tree[:-1])))
                        matches.append(RuleMatch(tree[:-1], message))
                elif isinstance(obj, dict):
                    if len(obj) == 1:
                        for key, value in obj.items():
                            if key == 'Ref':
                                if value in parameters:
                                    param = cfn.template['Parameters'][value]
                                    if 'NoEcho' in param:
                                        if not param['NoEcho']:
                                            fix_params.add(value)
                                    else:
                                        fix_params.add(value)
                    else:
                        message = 'Inappropriate map found for password on %s' % (
                            '/'.join(map(str, tree[:-1])))
                        matches.append(RuleMatch(tree[:-1], message))

        for paramname in fix_params:
            message = 'Parameter %s should have NoEcho True' % (paramname)
            tree = ['Parameters', paramname]
            matches.append(RuleMatch(tree, message))
        return matches
