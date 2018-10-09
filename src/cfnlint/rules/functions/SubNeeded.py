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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch

class SubNeeded(CloudFormationLintRule):
    """Check if a substitution string exists without a substitution function"""
    id = 'E1029'
    shortdesc = 'Sub is required if a variable is used in a string'
    description = 'If a substitution variable exists in a string but isn\'t wrapped with the Fn::Sub function the deployment will fail.'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html'
    tags = ['functions', 'sub']

    def _match_values(self, searchRegex, cfndict, path, cfn):
        """Recursively search for values matching the searchRegex"""
        values = []
        if isinstance(cfndict, dict):
            for key in cfndict:
                pathprop = path[:]
                pathprop.append(key)
                if isinstance(cfndict[key], str) and re.match(searchRegex, cfndict[key]):
                    pathprop.append(cfndict[key])
                    values.append(pathprop)
                    # pop the last element off for nesting of found elements for
                    # dict and list checks
                    pathprop = pathprop[:-1]
                if isinstance(cfndict[key], dict):
                    values.extend(self._match_values(searchRegex, cfndict[key], pathprop, cfn))
                elif isinstance(cfndict[key], list):
                    for index, item in enumerate(cfndict[key]):
                        pathproparr = pathprop[:]
                        pathproparr.append(index)
                        values.extend(self._match_values(searchRegex, item, pathproparr, cfn))
        elif isinstance(cfndict, list):
            for index, item in enumerate(cfndict):
                pathprop = path[:]
                pathprop.append(index)
                values.extend(self._match_values(searchRegex, item, pathprop, cfn))
        else:
            # Leaf node
            if isinstance(cfndict, str) and re.match(searchRegex, cfndict):
                values.append(path + [cfndict])

        return values

    def match_values(self, searchRegex, cfn):
        """
            Search for values in all parts of the templates that match the searchRegex
        """
        results = []
        results.extend(self._match_values(searchRegex, cfn.template, [], cfn))
        # Globals are removed during a transform.  They need to be checked manually
        results.extend(self._match_values(searchRegex, cfn.template.get('Globals', {}), [], cfn))
        return results

    def match(self, cfn):
        """Basic Rule Matching"""

        matches = []

        # Generic regex to match a string containing at least one ${parameter}
        parameter_search = re.compile(r'^(.*\$\{.*\}.*(\$\{.*\}.*)*)$')

        # Get a list of paths to every leaf node string containing at least one ${parameter}
        parameter_string_paths = self.match_values(parameter_search, cfn)

        # We want to search all of the paths to check if each one contains an 'Fn::Sub' 
        for parameter_string_path in parameter_string_paths:
            found_sub = False

            # Does the path contain an 'Fn::Sub'?
            for step in parameter_string_path:
                if step == 'Fn::Sub':
                    found_sub = True

            # If we didn't find an 'Fn::Sub' it means a string containing a ${parameter} may not be evaluated correctly
            if not found_sub:
                message = 'Found an embedded parameter outside of an "Fn::Sub" at {}'.format('/'.join(map(str, parameter_string_path)))
                matches.append(RuleMatch(parameter_string_path, message))

        return matches
