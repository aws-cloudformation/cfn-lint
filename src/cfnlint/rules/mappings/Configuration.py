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


class Configuration(CloudFormationLintRule):
    """Check if Mappings are configured correctly"""
    id = 'E7001'
    shortdesc = 'Mappings are appropriately configured'
    description = 'Check if Mappings are properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/mappings-section-structure.html'
    tags = ['mappings']

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = []

        mappings = cfn.template.get('Mappings', {})
        if mappings:
            for mapname, mapobj in mappings.items():
                if not isinstance(mapobj, dict):
                    message = 'Mapping {0} has invalid property'
                    matches.append(RuleMatch(
                        ['Mappings', mapname],
                        message.format(mapname)
                    ))
                else:
                    for firstkey in mapobj:
                        firstkeyobj = mapobj[firstkey]
                        if not isinstance(firstkeyobj, dict):
                            message = 'Mapping {0} has invalid property at {1}'
                            matches.append(RuleMatch(
                                ['Mappings', mapname, firstkey],
                                message.format(mapname, firstkeyobj)
                            ))
                        else:
                            for secondkey in firstkeyobj:
                                if not isinstance(
                                        firstkeyobj[secondkey],
                                        (six.string_types, list, six.integer_types)):
                                    message = 'Mapping {0} has invalid property at {1}'
                                    matches.append(RuleMatch(
                                        ['Mappings', mapname, firstkey, secondkey],
                                        message.format(mapname, secondkey)
                                    ))

        return matches
