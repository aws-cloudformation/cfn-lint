"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class CircularDependency(CloudFormationLintRule):
    """Check if Resources have a circular dependency"""
    id = 'E3004'
    shortdesc = 'Resource dependencies are not circular'
    description = 'Check that Resources are not circularly dependent ' \
                  'by Ref, Sub, or GetAtt'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['resources', 'circularly']

    def searchstring(self, string):
        """Search string for tokenized fields"""
        regex = re.compile(r'\${([a-zA-Z0-9.]*)}')
        return regex.findall(string)

    def _check_circular_dependency(self, resources, starting_resource, found_resources, association):
        """Check resource association """
        result = []

        # if association for evaluation is in found resources
        # we are looping and its time to stop
        if association in found_resources:
            # Only respond with the list if it is directly related to the resource
            # being analyzed.  Sometimes loops can happen outside of the
            # resource being analyzed.
            if association == starting_resource:
                return found_resources

            return []

        association_resources = resources.get(association)
        if association_resources:
            for association_resource in association_resources:
                result.extend(self._check_circular_dependency(
                    resources, starting_resource, found_resources[:] + [association], association_resource))

        return result

    def check_circular_dependencies(self, resources):
        """Check circular dependencies one item at a time"""
        matches = []
        for resource_name, associations in resources.items():
            resource_results = []
            for association in associations:
                results = set(
                    self._check_circular_dependency(
                        resources, resource_name, [resource_name], association))
                found = False
                if results:
                    for resource_result in resource_results:
                        if resource_result == results:
                            found = True
                    if not found:
                        resource_results.append(results)
            for resource_result in resource_results:
                message = 'Circular Dependencies for resource {0}.  Circular dependency with [{1}]'
                resource_tree = [
                    'Resources', resource_name
                ]
                matches.append(
                    RuleMatch(
                        resource_tree, message.format(
                            resource_name, ', '.join(map(str, resource_result)))))

        return matches

    def match(self, cfn):
        """Check CloudFormation Resources"""

        matches = []

        ref_objs = cfn.search_deep_keys('Ref')
        resources = {}
        for ref_obj in ref_objs:
            value = ref_obj[-1]
            if isinstance(value, (six.text_type, six.string_types, int)):
                ref_type, ref_name = ref_obj[:2]
                if ref_type == 'Resources':
                    if cfn.template.get('Resources', {}).get(value, {}):
                        if not resources.get(ref_name):
                            resources[ref_name] = []
                        resources[ref_name].append(value)

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

        sub_objs = cfn.search_deep_keys('Fn::Sub')
        for sub_obj in sub_objs:
            sub_parameters = []
            sub_parameter_values = {}
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

            if res_type == 'Resources':
                for sub_parameter in sub_parameters:
                    if sub_parameter not in sub_parameter_values:
                        if '.' in sub_parameter:
                            sub_parameter = sub_parameter.split('.')[0]
                        if cfn.template.get('Resources', {}).get(sub_parameter, {}):
                            if not resources.get(res_name):
                                resources[res_name] = []
                            resources[res_name].append(sub_parameter)

        matches.extend(self.check_circular_dependencies(resources))
        return matches
