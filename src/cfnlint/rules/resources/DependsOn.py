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


class DependsOn(CloudFormationLintRule):
    """Check Base Resource Configuration"""
    id = 'E3005'
    shortdesc = 'Check DependsOn values for Resources'
    description = 'Check that the DependsOn values are valid'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-dependson.html'
    tags = ['resources', 'dependson']

    def check_value(self, key, path, resources):
        """Check resource names for DependsOn"""
        matches = []

        if not isinstance(key, (six.text_type, six.string_types)):
            message = 'DependsOn values should be of string at {0}'
            matches.append(RuleMatch(path, message.format('/'.join(map(str, path)))))
            return matches
        if key not in resources:
            message = 'DependsOn should reference other resources at {0}'
            matches.append(RuleMatch(path, message.format('/'.join(map(str, path)))))

        return matches

    def match(self, cfn):
        """Check CloudFormation Resources"""

        matches = []

        resources = cfn.get_resources()

        for resource_name, resource_values in resources.items():
            depends_ons = resource_values.get('DependsOn')
            if depends_ons:
                path = ['Resources', resource_name, 'DependsOn']
                self.logger.debug('Validating DependsOn for %s base configuration', resource_name)
                if isinstance(depends_ons, list):
                    for index, depends_on in enumerate(depends_ons):
                        matches.extend(self.check_value(depends_on, path[:] + [index], resources))
                else:
                    matches.extend(self.check_value(depends_ons, path, resources))

        return matches
