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


class CircularDependency(CloudFormationLintRule):
    """Check if Resources have a circular dependency"""
    id = 'E3004'
    shortdesc = 'Resource dependencies are not circular'
    description = 'Check that Resources are not circularly dependent ' \
                  'by Ref, Sub, or GetAtt'
    tags = ['base', 'resources', 'circularly']

    def searchstring(self, string):
        """Search string for tokenized fields"""
        regex = re.compile(r'\${([a-zA-Z0-9.]*)}')
        return regex.findall(string)

    def match(self, cfn):
        """Check CloudFormation Resources"""

        matches = list()

        ref_objs = cfn.search_deep_keys('Ref')

        resources = {}
        for ref_obj in ref_objs:
            value = ref_obj[-1]
            ref_type, ref_name = ref_obj[:2]
            if ref_type == 'Resources':
                if cfn.template.get('Resources', {}).get(value, {}):
                    if not resources.get(ref_name):
                        resources[ref_name] = []
                    resources[ref_name].append(value)
                    if ref_name in resources.get(value, []) or ref_name == value:
                        message = "Refs cannot create circular dependencies on resources for {0}"
                        matches.append(RuleMatch(ref_obj, message.format('/'.join(map(str, ref_obj)))))

        getatt_objs = cfn.search_deep_keys('Fn::GetAtt')
        for getatt_obj in getatt_objs:
            value = getatt_obj[-1]
            if not isinstance(value, list):
                continue
            if not len(value) == 2:
                continue
            ref_name = value[0]
            res_type, res_name = getatt_obj[:2]
            if res_type == 'Resources':
                if cfn.template.get('Resources', {}).get(ref_name, {}):
                    if not resources.get(res_name):
                        resources[res_name] = []
                    resources[res_name].append(ref_name)
                    if res_name in resources.get(ref_name, []) or ref_name == res_name:
                        path_error = getatt_obj[:-1]
                        message = "GetAtt cannot create circular dependencies on resources for {0}"
                        matches.append(RuleMatch(path_error, message.format('/'.join(map(str, path_error)))))

        sub_objs = cfn.search_deep_keys('Fn::Sub')
        sub_parameter_values = {}
        for sub_obj in sub_objs:
            value = sub_obj[-1]
            res_type, res_name = sub_obj[:2]
            if isinstance(value, list):
                if not value:
                    continue
                if len(value) == 2:
                    sub_parameter_values = value[1]
                sub_parameters = self.searchstring(value[0])
            elif isinstance(value, (six.text_type, six.string_types)):
                sub_parameters = self.searchstring(value)

            for sub_parameter in sub_parameters:
                if sub_parameter not in sub_parameter_values:
                    if '.' in sub_parameter:
                        sub_parameter = sub_parameter.split('.')[0]
                    if cfn.template.get('Resources', {}).get(sub_parameter, {}):
                        if not resources.get(res_name):
                            resources[res_name] = []
                        resources[res_name].append(sub_parameter)
                        if res_name in resources.get(sub_parameter, []) or res_name == sub_parameter:
                            path_error = sub_obj[:-1]
                            message = "GetAtt cannot create circular dependencies on resources for {0}"
                            matches.append(RuleMatch(path_error, message.format('/'.join(map(str, path_error)))))

        return matches
