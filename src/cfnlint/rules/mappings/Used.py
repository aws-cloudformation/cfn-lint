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


class Used(CloudFormationLintRule):
    """Check if Mappings are used anywhere in the template"""
    id = 'W7001'
    shortdesc = 'Check if Mappings are Used'
    description = 'Making sure the mappings defined are used'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['conditions']

    def match(self, cfn):
        """Check CloudFormation Mappings"""

        matches = []
        findinmap_mappings = []

        mappings = cfn.template.get('Mappings', {})

        if mappings:

            # Get all "FindInMaps" that reference a Mapping
            maptrees = cfn.search_deep_keys('Fn::FindInMap')
            for maptree in maptrees:

                if isinstance(maptree[-1], list):
                    map_name = maptree[-1][0]
                    if isinstance(map_name, dict):
                        self.logger.debug(
                            'Mapping Name has a function that can have too many variations. '
                            'Disabling check %s', self.id
                        )
                        return matches

                    findinmap_mappings.append(maptree[-1][0])
                else:
                    findinmap_mappings.append(maptree[-1])

            # Check if the mappings are used
            for mapname, _ in mappings.items():
                if mapname not in findinmap_mappings:
                    message = 'Mapping {0} not used'
                    matches.append(RuleMatch(
                        ['Mappings', mapname],
                        message.format(mapname)
                    ))

        return matches
