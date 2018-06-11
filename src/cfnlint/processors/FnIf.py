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
import logging
import copy
import six
import cfnlint.processors


LOGGER = logging.getLogger(__name__)


class FnIf(cfnlint.processors.CloudFormationProcessor):
    """CloudFormation Transform Support"""
    type = 'FnIf'

    def run(self, cfn):
        """
            Main engine to run conditions processor
            Input: cfn (Template class)
            Output: Array of Template class objects with modified templates
        """
        results = list()

        condition_scenarios = self.get_condition_scenarios(cfn)
        # now that we have a list of scenarios where we know if a condition is
        # true or false we can build out a list of Templates where
        # - Fn::If is showing the resulting value
        # - Resources and Outputs with Conditions are removed
        if condition_scenarios:
            for condition_scenario in condition_scenarios:
                result = self.process_template(cfn, condition_scenario)
                results.append(result)
        else:
            results.append(cfn)

        return results

    def get_condition_scenarios(self, cfn):
        """ Get Condition Scnearios"""

        # All conditions end up being decided by a Equals.
        # Get all Unique Equals inside the conditions
        equals = self._get_condition_options(cfn)
        # Next we need a unique list of all the Refs being used inside the
        # conditions

        refs = self._get_all_ref_names(equals)
        # Then we need to get how refs are related to each other
        related_refs = self._get_related_refs(refs, equals)

        # From there we can compile a list of equals scenarios
        # Where the Ref would result in true or false for each unique equals
        equal_scenarios = self._get_equals_scenarios(related_refs)

        # After we have the equals scenarios we need to multiply the unique
        # condition paths together to create a complete list of scenarios
        scenarios = self._get_multiply_scenarios(equal_scenarios)

        # Now need to build a list of unique conditions as the equals scenarios
        # are played out.
        condition_scenarios = list()
        for scenario in scenarios:
            new_scenario = self.process_condition_scenario(cfn.template.get('Conditions', {}), scenario)
            is_matched = False
            for condition_scenario in condition_scenarios:
                if condition_scenario == new_scenario:
                    is_matched = True
            if not is_matched:
                condition_scenarios.append(new_scenario)

        return condition_scenarios

    def _get_multiple_scenarios(self, currents, key, values):
        results = list()
        for value in values:
            result = {}
            result[key] = value
            if currents:
                temp_currents = currents[:]
                for current in temp_currents:
                    item = current.copy()
                    item.update(result)
                    results.append(item)
            else:
                results.append(result)

        return results

    def _get_multiply_scenarios(self, ref_values):
        """
            Multiple unique scenarios together
            Input: ref values to multiply
            OUtputs:
                Example: [
                    {
                        'CreateAdditionalPrivateSubnets': 'true',
                        'NumberOfAZs': '4',
                        'CreatePrivateSubnets': 'true',
                        'AWS::Region': 'us-gov-west-1'
                    },
                    {
                        'CreateAdditionalPrivateSubnets': 'true.x',
                        'NumberOfAZs': '4',
                        'CreatePrivateSubnets': 'true',
                        'AWS::Region': 'us-gov-west-1'
                    }
                ...
                ]
        """
        results = list()
        for key, values in ref_values.items():
            results = self._get_multiple_scenarios(results, key, values)

        return results

    def _get_equals_scenarios(self, related_refs):
        """
            Get equals scenarios
            Input: Related Refs
            Outputs: Values for the Refs that will make conditions equals or false
                Example: {
                    'NumberOfAZs': ['4', '3', '4.3.x'],
                    'CreatePrivateSubnets': ['true', 'true.x'],
                    'AWS::Region': [
                        'us-gov-west-1', 'cn-north-1',
                        'us-east-1', 'us-gov-west-1.cn-north-1.us-east-1.x'
                    ],
                    'CreateAdditionalPrivateSubnets': ['true', 'true.x']
                }
        """
        results = {}
        for related_ref, related_values in related_refs.items():
            for related_value in related_values:
                if not results.get(related_value[0][1]):
                    results[related_ref] = list()
                if isinstance(related_value[1], (str, six.string_types, six.text_type)):
                    results[related_ref].append(related_value[1])
                if isinstance(related_value[0], (str, six.string_types, six.text_type)):
                    results[related_ref].append(related_value[0])
                # create one that can't be true
            results[related_ref].append('%s.x' % ('.'.join(results[related_ref])))

        return(results)

    def _get_related_refs(self, refs, equals):
        """
            Takes the unique refs, and equals and gets their relationships
            Input:
            - Unique list of Refs
            - Equals - A set of all the Equals in the Conditions
            Outputs: Relationship of Conditions based on Ref Values in Equals
                Example: {
                    'NumberOfAZs': [
                        (('Ref', 'NumberOfAZs'), '3'),
                        (('Ref', 'NumberOfAZs'), '4')
                    ],
                    'CreatePrivateSubnets': [
                        (('Ref', 'CreatePrivateSubnets'), 'true')
                    ],
                    'CreateAdditionalPrivateSubnets': [
                        (('Ref', 'CreateAdditionalPrivateSubnets'), 'true')
                    ],
                    'AWS::Region': [
                        (('Ref', 'AWS::Region'), 'us-gov-west-1'),
                        (('Ref', 'AWS::Region'), 'cn-north-1'),
                        (('Ref', 'AWS::Region'), 'us-east-1')]
                    }
        """
        matches = {}
        for ref in refs:
            for equal in equals:
                if ('Ref', ref) == equal[0]:
                    if not matches.get(ref):
                        matches[ref] = list()
                    matches[ref].append(equal)
                if ('Ref', ref) == equal[1]:
                    if not matches.get(ref):
                        matches[ref] = list()
                    matches[ref].append(equal)

        return matches

    def _get_all_ref_names(self, equals):
        """
            Gets all the ref names
            Intput: Equals set
            Output: Unique list of refs
                Example: {'CreateAdditionalPrivateSubnets', 'NumberOfAZs', 'CreatePrivateSubnets', 'AWS::Region'}
        """
        refs = set()
        for equal in equals:
            for value in equal:
                if len(value) == 2:
                    if value[0]:
                        refs.add(value[1])

        return refs

    def get_equal_elements(self, equal):
        """Get the Refs in an equals"""

        if isinstance(equal, list):
            return_element = list()
            if len(equal) == 2:
                for element in equal:
                    if isinstance(element, dict):
                        if len(element) == 1:
                            for key, value in element.items():
                                if key == 'Ref':
                                    return_element.append((key, value))
                                # there can be a findinmap in a condition
                                else:
                                    return_element.append(('FindInMap', ''))
                    elif not isinstance(element, (list)):
                        return_element.append(element)

                return (return_element[0], return_element[1])

        return None

    def _get_condition_options(self, cfn):
        """
            Get Conditions based on Condition definitions
            Input: Cfn (Template)
            Output: Python Set Representing Equals inside Conditions
                Example: {
                    (('Ref', 'CreateAdditionalPrivateSubnets'), 'true'),
                    (('Ref', 'AWS::Region'), 'cn-north-1'),
                    (('Ref', 'CreatePrivateSubnets'), 'true'),
                    (('Ref', 'AWS::Region'), 'us-east-1'),
                    (('Ref', 'AWS::Region'), 'us-gov-west-1'),
                    (('Ref', 'NumberOfAZs'), '4'),
                    (('Ref', 'NumberOfAZs'), '3')
                }
        """
        refs = set()
        equals = cfn.search_deep_keys('Fn::Equals')
        for equal in equals:
            if equal[0] == 'Conditions':
                new_element = self.get_equal_elements(equal[-1])
                refs.add(new_element)

        return refs

    def set_findinmap_value(self, obj, value, path):
        """
            Set the value of an object with dynamic length
        """
        if len(path) == 1 and path[0] == 'Fn::If':
            del obj['Fn::If']
            if isinstance(value, dict):
                obj.update(value)
            else:
                obj = value
            return obj

        key = path[0]
        obj[key] = self.set_findinmap_value(obj[key], value, path[1:])

        return obj

    def _process_condition_equals(self, equals, equal_values):
        values_to_compare = list()
        if isinstance(equals, list):
            if len(equals) == 2:
                for equal in equals:
                    if isinstance(equal, dict):
                        if len(equal) == 1:
                            for key, value in equal.items():
                                if key == 'Ref' and value in equal_values:
                                    values_to_compare.append(equal_values.get(value))

                    elif isinstance(equal, (str, six.text_type, six.string_types)):
                        values_to_compare.append(equal)

        if len(values_to_compare) == 2:
            return(values_to_compare[0] == values_to_compare[1])

        return False

    def _process_condition_and(self, conditions, equal_values, all_conditions):
        result = True
        if isinstance(conditions, list):
            for condition in conditions:
                result = self._process_condition_scenario(condition, equal_values, all_conditions)
                if not result:
                    break
        else:
            result = False

        return result

    def _process_condition_or(self, conditions, equal_values, all_conditions):
        result = False
        if isinstance(conditions, list):
            for condition in conditions:
                result = self._process_condition_scenario(condition, equal_values, all_conditions)
                if result:
                    break
        else:
            result = False

        return result

    def _process_condition_not(self, conditions, equal_values, all_conditions):
        if isinstance(conditions, list):
            if len(conditions) == 1:
                for condition in conditions:
                    return(not self._process_condition_scenario(condition, equal_values, all_conditions))

        return False

    def _process_condition_scenario(self, condition, equal_values, all_conditions):
        """ Helper """
        condition_result = False
        if isinstance(condition, dict):
            if len(condition) == 1:
                for condition_key, condition_values in condition.items():
                    if condition_key == 'Fn::And':
                        condition_result = self._process_condition_and(condition_values, equal_values, all_conditions)
                    elif condition_key == 'Fn::Or':
                        condition_result = self._process_condition_or(condition_values, equal_values, all_conditions)
                    elif condition_key == 'Fn::Not':
                        condition_result = self._process_condition_not(condition_values, equal_values, all_conditions)
                    elif condition_key == 'Fn::Equals':
                        condition_result = self._process_condition_equals(condition_values, equal_values)
                    elif condition_key == 'Condition':
                        condition_result = self._process_condition_scenario(
                            all_conditions[condition_values], equal_values, all_conditions)

        return condition_result

    def process_condition_scenario(self, conditions, equal_values):
        """Play out the conditions"""
        results = {}
        for condition_name, condition_value in conditions.items():
            results[condition_name] = self._process_condition_scenario(condition_value, equal_values, conditions)

        return results

    def process_template(self, cfn, condition_scenario):
        """
            Condition scenario to get a new template
            Input:
                - Cfn (Template Object)
                - Condition Scenario
            Output: A transposed Cfn (Template Object) with the condition applied
                   and Fn::If removed, condition resources/outputs removed.
        """
        processed_cfn = copy.deepcopy(cfn)

        resources = processed_cfn.template.get('Resources', {}).copy()
        for resource_name, resource_values in resources.items():
            condition = resource_values.get('Condition')
            if condition in condition_scenario:
                if not condition_scenario.get(condition):
                    del processed_cfn.template['Resources'][resource_name]

        resources = processed_cfn.template.get('Outputs', {}).copy()
        for output_name, output_values in resources.items():
            condition = output_values.get('Condition')
            if condition in condition_scenario:
                if not condition_scenario.get(condition):
                    del processed_cfn.template['Outputs'][output_name]

        all_findinmaps = processed_cfn.search_deep_keys('Fn::If')
        all_findinmaps.sort(key=len, reverse=True)

        for findinmap in all_findinmaps:
            findinmap_values = findinmap[-1]
            findinmap_path = findinmap[:-1]
            if isinstance(findinmap_values, list):
                if len(findinmap_values) == 3:
                    findinmap_name = findinmap_values[0]
                    if findinmap_name in condition_scenario:
                        if condition_scenario[findinmap_name]:
                            processed_cfn.template = self.set_findinmap_value(
                                processed_cfn.template,
                                findinmap_values[1],
                                findinmap_path)
                        else:
                            processed_cfn.template = self.set_findinmap_value(
                                processed_cfn.template,
                                findinmap_values[2],
                                findinmap_path)

        return processed_cfn
