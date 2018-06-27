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

class SecurityGroupDescription(CloudFormationLintRule):
    """Check SecurityGroup Description Configuration"""
    id = 'E2509'
    shortdesc = 'Validate SecurityGroup description'
    description = 'Check if SecurityGroup descriptions are correctly configured'
    tags = ['base', 'resources', 'securitygroup']

    description_regex = r'^([a-z,A-Z,0-9,. _\-:/()#,@[\]+=&;\{\}!$*])*$'

    def match(self, cfn):
        """Check SecurityGroup descriptions"""

        matches = list()

        resources = cfn.get_resources(['AWS::EC2::SecurityGroup'])

        for resource_name, resource in resources.items():
            path = ['Resources', resource_name, 'Properties']

            props = resource.get('Properties')
            if props:
                description = props.get('GroupDescription')

                if description:
                    path = ['Resources', resource_name, 'Properties', 'GroupDescription']
                    full_path = ('/'.join(str(x) for x in path))

                    if isinstance(description, six.string_types):
                        # Check max length
                        if len(description) > 255:
                            message = 'GroupDescription length of {0} ({1}) exceeds the limit (255) at {2}'
                            matches.append(RuleMatch(path, message.format(resource_name, len(description), full_path)))
                        else:
                            # Check valid characters
                            regex = re.compile(self.description_regex)
                            if not regex.match(description):
                                message = 'GroupDescription contains invalid characters (valid characters are: '\
                                          '"a-zA-Z0-9. _-:/()#,@[]+=&;\\{{}}!$*"") at {0}'
                                matches.append(RuleMatch(path, message.format(full_path)))

        return matches
