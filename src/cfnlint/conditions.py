"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import hashlib
from copy import copy
import json
import logging
import six
import cfnlint.helpers

LOGGER = logging.getLogger(__name__)


class ConditionParseError(Exception):
    """
    Error thrown when the template has poorly formatted condition
    """


def get_hash(obj):
    """ Return a hash of an object """
    return hashlib.sha1(json.dumps(obj, sort_keys=True).encode('utf-8')).hexdigest()


class EqualsValue(object):
    """ holds the values of a equals """
    Function = None
    String = None

    def __init__(self, value):
        if isinstance(value, dict):
            if len(value) == 1:
                # Save hashes of the dict for consistency and sorting
                self.Function = get_hash(value)
            else:
                LOGGER.debug('Length of the object needs to be 1')
                raise ConditionParseError
        elif isinstance(value, six.string_types):
            self.String = value
        elif isinstance(value, six.integer_types):
            self.String = str(value)
        else:
            LOGGER.debug('Equals value has to be string or object')
            raise ConditionParseError

    def __eq__(self, other):
        return other in [self.Function, self.String]


class Equals(object):
    """ Equals operator """
    Left = None
    Right = None

    def __init__(self, equals):
        if isinstance(equals, list):
            if len(equals) == 2:
                self.Left = EqualsValue(equals[0])
                self.Right = EqualsValue(equals[1])
            else:
                LOGGER.debug('Length of Equals needs to be 2')
                raise ConditionParseError
        else:
            LOGGER.debug('Equals needs to be a list')
            raise ConditionParseError

    def test(self, scenarios):
        """ Do an equals based on the provided scenario """
        for scenario, value in scenarios.items():
            if scenario == self.Left:
                return value == self.Right
            if scenario == self.Right:
                return value == self.Left

        return None


class Condition(object):
    """ Individual condition """
    And = None
    Or = None
    Not = None
    Equals = None
    Influenced_Equals = None

    def __init__(self, template, name=None, sub_condition=None):
        self.And = []
        self.Or = []
        self.Not = []
        self.Influenced_Equals = {}
        if name is not None:
            value = template.get('Conditions', {}).get(name, {})
            try:
                self.process_condition(template, value)
            except ConditionParseError:
                LOGGER.debug('Error parsing condition: %s', name)
                self.Equals = None
        elif sub_condition is not None:
            try:
                self.process_condition(template, sub_condition)
            except ConditionParseError:
                LOGGER.debug('Error parsing condition: %s', name)
                self.Equals = None

    def test(self, scenarios):
        """ Test a condition based on a scenario """
        if self.And:
            for a in self.And:
                if not a.test(scenarios):
                    return False
            return True
        if self.Or:
            for o in self.Or:
                if o.test(scenarios):
                    return True
            return False
        if self.Not:
            for n in self.Not:
                return not n.test(scenarios)
        return self.Equals.test(scenarios)

    def process_influenced_equal(self, equal):
        """ Get influenced equals from sub conditions """
        if equal.Left.Function:
            if not self.Influenced_Equals.get(equal.Left.Function):
                self.Influenced_Equals[equal.Left.Function] = set()
            if equal.Right.Function:
                self.Influenced_Equals[equal.Left.Function].add(equal.Right.Function)
            elif equal.Right.String is not None:
                self.Influenced_Equals[equal.Left.Function].add(equal.Right.String)
        if equal.Right.Function:
            if not self.Influenced_Equals.get(equal.Right.Function):
                self.Influenced_Equals[equal.Right.Function] = set()
            if equal.Left.Function:
                self.Influenced_Equals[equal.Right.Function].add(equal.Left.Function)
            elif equal.Left.String is not None:
                self.Influenced_Equals[equal.Right.Function].add(equal.Left.String)

    def process_condition(self, template, value):
        """ process condition """
        if isinstance(value, dict):
            if len(value) == 1:
                for func_name, func_value in value.items():
                    if func_name == cfnlint.helpers.FUNCTION_AND:
                        self.And = self.process_function(template, func_value)
                    elif func_name == cfnlint.helpers.FUNCTION_OR:
                        self.Or = self.process_function(template, func_value)
                    elif func_name == cfnlint.helpers.FUNCTION_NOT:
                        self.Not = self.process_function(template, func_value)
                    elif func_name == cfnlint.helpers.FUNCTION_EQUALS:
                        equal = Equals(func_value)
                        self.process_influenced_equal(equal)
                        self.Equals = equal
                    elif func_name == 'Condition':
                        value = template.get('Conditions', {}).get(func_value, {})
                        try:
                            self.process_condition(template, value)
                        except ConditionParseError:
                            LOGGER.debug('Error parsing condition: %s', func_value)
            else:
                LOGGER.debug('Length of the object must be 1')
                raise ConditionParseError
        else:
            LOGGER.debug('Condition has to be an object')
            raise ConditionParseError

    def process_function(self, template, values):
        """ Process Function """
        results = []
        for value in values:
            if isinstance(value, dict):
                if len(value) == 1:
                    for k, v in value.items():
                        if k == cfnlint.helpers.FUNCTION_EQUALS:
                            equal = Equals(v)
                            self.process_influenced_equal(equal)
                            results.append(equal)
                        elif k == 'Condition':
                            condition = Condition(template, v)
                            results.append(condition)
                            for i_e_k, i_e_v in condition.Influenced_Equals.items():
                                if not self.Influenced_Equals.get(i_e_k):
                                    self.Influenced_Equals[i_e_k] = set()
                                for s_v in i_e_v:
                                    self.Influenced_Equals[i_e_k].add(s_v)
                        else:
                            condition = Condition(template, None, value)
                            results.append(condition)
                            for i_e_k, i_e_v in condition.Influenced_Equals.items():
                                if not self.Influenced_Equals.get(i_e_k):
                                    self.Influenced_Equals[i_e_k] = set()
                                for s_v in i_e_v:
                                    self.Influenced_Equals[i_e_k].add(s_v)

        return results


class Conditions(object):
    """ All the conditions """
    Conditions = None
    Equals = None
    Parameters = None

    def __init__(self, cfn):
        self.Conditions = {}
        self.Equals = {}
        self.Parameters = {}
        try:
            self.Equals = self._get_condition_equals(
                cfn.search_deep_keys(cfnlint.helpers.FUNCTION_EQUALS))
            for condition_name in cfn.template.get('Conditions', {}):
                self.Conditions[condition_name] = Condition(cfn.template, condition_name)
            # Configure parameters Allowed Values if they have them
            for parameter_name, parameter_values in cfn.template.get('Parameters', {}).items():
                # ALlowed Values must be a list so validate they are
                if isinstance(parameter_values.get('AllowedValues'), list):
                    # Any parameter in a condition could be used but would have to be done by
                    # Ref so build a ref to match for getting an equivalent hash
                    self.Parameters[
                        get_hash({'Ref': parameter_name})
                    ] = parameter_values.get('AllowedValues')
        except Exception as err:  # pylint: disable=W0703
            LOGGER.debug('While processing conditions got error: %s', err)

    def _get_condition_equals(self, equals):
        """
            Get Conditions based on Condition definitions
            Input: Cfn (Template)
            Output: List of hashes of Equal dict objects (Ref or FindInMap)
        """
        results = {}

        for equal in equals:
            if equal[0] == 'Conditions':
                condition_name = equal[1]
                equals = equal[-1]
                if isinstance(equals, list):
                    if len(equals) == 2:
                        dict_hash_1 = None
                        value_1 = None
                        dict_hash_2 = None
                        value_2 = None
                        if isinstance(equals[0], dict):
                            dict_hash_1 = get_hash(equals[0])
                        elif isinstance(equals[0], six.string_types):
                            value_1 = equals[0]
                        elif isinstance(equals[0], six.integer_types):
                            value_1 = str(equals[0])
                        if isinstance(equals[1], dict):
                            dict_hash_2 = get_hash(equals[1])
                        elif isinstance(equals[1], six.string_types):
                            value_2 = equals[1]
                        elif isinstance(equals[1], six.integer_types):
                            value_2 = str(equals[1])

                        if dict_hash_1:
                            if dict_hash_1 not in results:
                                results[dict_hash_1] = []
                            if dict_hash_2:
                                results[dict_hash_1].append({
                                    'Condition': condition_name,
                                    'Type': 'dict',
                                    'Value': dict_hash_2
                                })
                            else:
                                results[dict_hash_1].append({
                                    'Condition': condition_name,
                                    'Type': 'string',
                                    'Value': value_2
                                })
                        if dict_hash_2:
                            if dict_hash_2 not in results:
                                results[dict_hash_2] = []
                            if dict_hash_1:
                                results[dict_hash_2].append({
                                    'Condition': condition_name,
                                    'Type': 'dict',
                                    'Value': dict_hash_1
                                })
                            else:
                                results[dict_hash_2].append({
                                    'Condition': condition_name,
                                    'Type': 'string',
                                    'Value': value_1
                                })
        return results

    def multiply_conditions(self, currents, condition, values):
        """ Build out scenarios for when conditions don't match """
        results = []
        if not currents:
            for value in values:
                new = {}
                new[condition] = value
                results.append(new)
        for current in currents:
            for value in values:
                new = copy(current)
                new[condition] = value
                results.append(new)

        return results

    def get_scenarios(self, conditions):
        """Get scenarios for all conditions provided"""
        matched_equals = {}
        matched_conditions = []

        results = []

        # When conditions don't properly get loaded (configuration error)
        # lets just return an empty list
        if not self.Conditions:
            return results

        for condition in conditions:
            # When one of the conditions don't exist we return an empty result
            if not self.Conditions.get(condition):
                return []
            for equal_key, equal_values in self.Conditions.get(condition).Influenced_Equals.items():
                if not matched_equals.get(equal_key):
                    matched_equals[equal_key] = set()
                else:
                    matched_conditions.append(condition)
                for s_v in equal_values:
                    matched_equals[equal_key].add(s_v)

        def multiply_equals(currents, s_hash, sets, parameter_values):
            """  Multiply Equals when building scenarios """
            results = []
            false_case = ''
            if not currents:
                # If the Parameter being REFed has Allowed Values use those instead
                if parameter_values:
                    for p_value in parameter_values:
                        # the allowed value must be an integer or string
                        # protecting against really badly formatted templates
                        if isinstance(p_value, (six.integer_types, six.string_types)):
                            new = {}
                            # the allowed values could be numbers so force a string
                            new[s_hash] = str(p_value)
                            results.append(new)
                else:
                    for s_set in sets:
                        new = {}
                        new[s_hash] = s_set
                        false_case += s_set
                        results.append(new)
                    new = {}
                    new[s_hash] = false_case + '.bad'
                    results.append(new)
            for current in currents:
                # If the Parameter being REFed has Allowed Values use those instead
                if parameter_values:
                    for p_value in parameter_values:
                        # the allowed value must be an integer or string
                        # protecting against really badly formatted templates
                        if isinstance(p_value, (six.integer_types, six.string_types)):
                            new = copy(current)
                            # the allowed values could be numbers so force a string
                            new[s_hash] = str(p_value)
                            results.append(new)
                else:
                    for s_set in sets:
                        new = copy(current)
                        new[s_hash] = s_set
                        false_case += s_set
                        results.append(new)
                    new = copy(current)
                    new[s_hash] = false_case + '.bad'
                    results.append(new)

            return results

        if not matched_conditions:
            # fail safe to not create a lot of unrelated scenarios. Just test if they are true/false
            # At this point this value is completely arbitrary and not configurable
            if len(conditions) > 4:
                LOGGER.info(
                    'Found %s conditions.  Limiting results to protect against heavy cpu time', len(conditions))
                true_results = []
                false_results = []
                for condition in conditions:
                    true_results = self.multiply_conditions(true_results, condition, [True])
                    false_results = self.multiply_conditions(false_results, condition, [False])
                results.extend(true_results)
                results.extend(false_results)
            else:
                for condition in conditions:
                    results = self.multiply_conditions(results, condition, [True, False])

            return results

        if matched_conditions:
            scenarios = []
            for con_hash, sets in matched_equals.items():
                scenarios = multiply_equals(scenarios, con_hash, sets,
                                            self.Parameters.get(con_hash))

        for scenario in scenarios:
            r_condition = {}
            for condition in conditions:
                r_condition[condition] = self.Conditions.get(condition).test(scenario)

            if r_condition not in results:
                results.append(r_condition)

        return(results)
