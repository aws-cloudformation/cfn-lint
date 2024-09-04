"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import itertools
import logging
import traceback
from functools import lru_cache
from typing import Any, Iterator, Set, Tuple

from sympy import And, Implies, Not, Symbol
from sympy.assumptions.cnf import EncodedCNF
from sympy.logic.boolalg import BooleanFalse, BooleanTrue
from sympy.logic.inference import satisfiable

from cfnlint.conditions._condition import ConditionNamed
from cfnlint.conditions._equals import Equal, EqualParameter
from cfnlint.conditions._errors import UnknownSatisfisfaction
from cfnlint.conditions._rule import Rule
from cfnlint.conditions._utils import get_hash

LOGGER = logging.getLogger(__name__)


class Conditions:
    """Conditions provides the logic for relating individual condition together"""

    _max_scenarios: int = 128  # equivalent to 2^7

    def __init__(self, cfn) -> None:
        self._conditions: dict[str, ConditionNamed] = {}
        self._parameters: dict[str, list[str]] = {}
        self._rules: list[Rule] = []
        self._init_conditions(cfn=cfn)
        self._init_parameters(cfn=cfn)
        self._init_rules(cfn=cfn)
        self._cnf, self._solver_params = self._build_cnf(list(self._conditions.keys()))

    def _init_conditions(self, cfn):
        conditions = cfn.template.get("Conditions")
        if isinstance(conditions, dict):
            for k, _ in conditions.items():
                try:
                    self._conditions[k] = ConditionNamed(k, conditions)
                except ValueError as e:
                    LOGGER.debug(
                        "Captured error while building condition %s: %s", k, str(e)
                    )
                except Exception as e:  # pylint: disable=broad-exception-caught
                    if LOGGER.getEffectiveLevel() == logging.DEBUG:
                        error_message = traceback.format_exc()
                    else:
                        error_message = str(e)
                    LOGGER.debug(
                        "Captured unknown error while building condition %s: %s",
                        k,
                        error_message,
                    )

    def _init_parameters(self, cfn: Any) -> None:
        parameters = cfn.template.get("Parameters")
        if not isinstance(parameters, dict):
            return
        for parameter_name, parameter in parameters.items():
            if not isinstance(parameter, dict):
                continue
            allowed_values = parameter.get("AllowedValues")
            if not allowed_values or not isinstance(allowed_values, list):
                continue

            param_hash = get_hash({"Ref": parameter_name})
            self._parameters[param_hash] = []
            for allowed_value in allowed_values:
                if isinstance(allowed_value, (str, int, float, bool)):
                    self._parameters[param_hash].append(get_hash(str(allowed_value)))

    def _init_rules(self, cfn: Any) -> None:
        rules = cfn.template.get("Rules")
        conditions = cfn.template.get("Conditions", {})
        if not isinstance(rules, dict) or not isinstance(conditions, dict):
            return
        for k, v in rules.items():
            if not isinstance(v, dict):
                continue
            try:
                self._rules.append(Rule(v, conditions))
            except ValueError as e:
                LOGGER.debug("Captured error while building rule %s: %s", k, str(e))
            except Exception as e:  # pylint: disable=broad-exception-caught
                if LOGGER.getEffectiveLevel() == logging.DEBUG:
                    error_message = traceback.format_exc()
                else:
                    error_message = str(e)
                LOGGER.debug(
                    "Captured unknown error while building rule %s: %s",
                    k,
                    error_message,
                )

    def get(self, name: str, default: Any = None) -> ConditionNamed:
        """Return the conditions"""
        return self._conditions.get(name, default)

    def _build_cnf(
        self, condition_names: list[str]
    ) -> Tuple[EncodedCNF, dict[str, Any]]:
        cnf = EncodedCNF()

        # build parameters and equals into solver
        equal_vars: dict[str, Symbol] = {}

        equals: dict[str, Equal] = {}
        for condition_name in condition_names:
            c_equals = self._conditions[condition_name].equals
            for c_equal in c_equals:
                # check to see if equals already matches another one
                if c_equal.hash in equal_vars:
                    continue

                if c_equal.is_static is not None:
                    if c_equal.is_static:
                        equal_vars[c_equal.hash] = BooleanTrue()
                    else:
                        equal_vars[c_equal.hash] = BooleanFalse()
                else:
                    equal_vars[c_equal.hash] = Symbol(c_equal.hash)
                    # See if parameter in this equals is the same as another equals
                    for param in c_equal.parameters:
                        for e_hash, e_equals in equals.items():
                            if param in e_equals.parameters:
                                # equivalent to NAND logic. We want to make
                                # sure that both equals are not both True
                                # at the same time
                                cnf.add_prop(
                                    ~(equal_vars[c_equal.hash] & equal_vars[e_hash])
                                )
                equals[c_equal.hash] = c_equal

        # Determine if a set of conditions can never be all false
        allowed_values = self._parameters.copy()
        if allowed_values:
            # iteration 1 cleans up all the hash values
            # from allowed_values to know if we
            # used them all
            for _, equal_1 in equals.items():
                for param in equal_1.parameters:
                    if param.hash not in allowed_values:
                        continue
                    if isinstance(equal_1.left, str):
                        if get_hash(equal_1.left) in allowed_values[param.hash]:
                            allowed_values[param.hash].remove(get_hash(equal_1.left))
                        else:
                            equal_vars[equal_1.hash] = BooleanFalse()
                    if isinstance(equal_1.right, str):
                        if get_hash(equal_1.right) in allowed_values[param.hash]:
                            allowed_values[param.hash].remove(get_hash(equal_1.right))
                        else:
                            equal_vars[equal_1.hash] = BooleanFalse()

            # iteration 2 builds the cnf formulas to make sure any empty lists
            # are now full not equals
            for allowed_hash, allowed_value in allowed_values.items():
                # means the list is empty and all allowed values are validated
                # so not all equals can be false
                if not allowed_value:
                    prop = None
                    for _, equal_1 in equals.items():
                        for param in equal_1.parameters:
                            if allowed_hash == param.hash:
                                if prop is None:
                                    prop = Not(equal_vars[equal_1.hash])
                                else:
                                    prop = prop & Not(equal_vars[equal_1.hash])
                    # Need to make sure they aren't all False
                    # So Not(Not(Equal1) & Not(Equal2))
                    # When Equal1 False and Equal2 False
                    # Not(True & True) = False allowing this not to happen
                    if prop is not None:
                        cnf.add_prop(Not(prop))

        for rule in self._rules:
            cnf.add_prop(rule.build_cnf(equal_vars))

        return (cnf, equal_vars)

    def build_scenarios(
        self, conditions: dict[str, Set[bool]], region: str | None = None
    ) -> Iterator[dict[str, bool]]:
        """Given a list of condition names this function will
        yield scenarios that represent those conditions and
        there result (True/False)

        Args:
            condition_names (list[str]): A list of condition names

        Returns:
            Iterator[dict[str, bool]]: yield dict objects of {ConditionName: True/False}
        """
        # nothing to yield if there are no conditions
        if len(conditions) == 0:
            return

        c_cnf = self._cnf.copy()
        condition_names = []
        conditions_set = {}
        for condition_name, values in conditions.items():
            if condition_name in self._conditions:
                if values == {True}:
                    c_cnf.add_prop(
                        self._conditions[condition_name].build_true_cnf(
                            self._solver_params
                        )
                    )
                    conditions_set[condition_name] = True
                    continue
                if values == {False}:
                    c_cnf.add_prop(
                        self._conditions[condition_name].build_false_cnf(
                            self._solver_params
                        )
                    )
                    conditions_set[condition_name] = False
                    continue
            condition_names.append(condition_name)

        try:
            # build a large matric of True/False options
            # based on the provided conditions
            scenarios_attempted = 0
            if region:
                products = itertools.starmap(
                    self.build_scenerios_on_region,
                    itertools.product(condition_names, [region]),
                )
            else:
                products = itertools.product([True, False], repeat=len(condition_names))  # type: ignore

            for p in products:
                cnf = c_cnf.copy()
                params = dict(zip(condition_names, p))
                for condition_name, opt in params.items():
                    if opt:
                        cnf.add_prop(
                            self._conditions[condition_name].build_true_cnf(
                                self._solver_params
                            )
                        )
                    else:
                        cnf.add_prop(
                            self._conditions[condition_name].build_false_cnf(
                                self._solver_params
                            )
                        )

                # if the scenario can be satisfied then return it
                if satisfiable(cnf):
                    yield {**params, **conditions_set}

                scenarios_attempted += 1
                # On occassions people will use a lot of non-related conditions
                # this is fail safe to limit the maximum number of responses
                if scenarios_attempted >= self._max_scenarios:
                    return
        except KeyError:
            # KeyError is because the listed condition doesn't exist because of bad
            #  formatting or just the wrong condition name
            return

    def _build_cfn_implies(self, scenarios) -> And:
        conditions = []
        for condition_name, opt in scenarios.items():
            if opt:
                conditions.append(
                    self._conditions[condition_name].build_true_cnf(self._solver_params)
                )
            else:
                conditions.append(
                    self._conditions[condition_name].build_false_cnf(
                        self._solver_params
                    )
                )

        return And(*conditions)

    def check_implies(self, scenarios: dict[str, bool], implies: str) -> bool:
        """Based on a bunch of scenario conditions and their Truth/False value
        determine if implies condition is True any time the scenarios are satisfied
        solver, solver_params = self._build_solver(list(scenarios.keys()) + [implies])

        Args:
            scenarios (dict[str, bool]): A list of condition names
            and if they are True or False implies: the condition name that
            we are implying will also be True

        Returns:
            bool: if the implied condition will be True if the scenario is True
        """
        try:
            cnf = self._cnf.copy()
            # if the implies condition has to be false in the scenarios we
            # know it can never be true
            if not scenarios.get(implies, True):
                return False

            and_condition = self._build_cfn_implies(scenarios)
            cnf.add_prop(and_condition)
            implies_condition = self._conditions[implies].build_true_cnf(
                self._solver_params
            )
            cnf.add_prop(Not(Implies(and_condition, implies_condition)))

            results = satisfiable(cnf)
            if results:
                return False

            return True
        except KeyError:
            # KeyError is because the listed condition doesn't exist because of bad
            #  formatting or just the wrong condition name
            return True

    @lru_cache
    def build_scenerios_on_region(self, condition_name: str, region: str) -> list[bool]:
        """Based on a region validate if the condition_name could be true

        Args:
            condition_name (str): The name of the condition we are validating against
            region (str): the name of the region

        Returns:
            list[bool]: Returns True, False, or True and False depending on if the
               condition could be True, False or both based on the region parameter
        """
        cnf_region = self._cnf.copy()
        found_region = False

        # validate the condition name exists
        # return True/False if it doesn't
        if condition_name not in self._conditions:
            return [True, False]

        for eql in self._conditions[condition_name].equals:
            is_region, equal_region = eql.is_region
            if is_region:
                found_region = True
                if equal_region == region:
                    cnf_region.add_prop(And(self._solver_params[eql.hash]))
                else:
                    cnf_region.add_prop(Not(self._solver_params[eql.hash]))

        # The condition doesn't use a region parameter so it can be True or False
        # Note: It is possible its a hard coded condition but
        # for now we will return True and False
        if not found_region:
            return [True, False]

        results = []
        cnf_test = cnf_region.copy()
        cnf_test.add_prop(
            self._conditions[condition_name].build_true_cnf(self._solver_params)
        )
        if satisfiable(cnf_test):
            results.append(True)

        cnf_test = cnf_region.copy()
        cnf_test.add_prop(
            self._conditions[condition_name].build_false_cnf(self._solver_params)
        )
        if satisfiable(cnf_test):
            results.append(False)

        return results

    def satisfiable(
        self, conditions: dict[str, bool], parameter_values: dict[str, str]
    ) -> bool:
        """Given a list of condition names this function will
        determine if the conditions are satisfied

        Args:
            condition_names (dict[str, bool]): A list of condition names with if
              they are True or False

        Returns:
            bool: True if the conditions are satisfied

        Raises:
            UnknownSatisfisfaction: If we don't know how to satisfy a condition
        """
        if not conditions:
            if self._rules:
                satisfied = satisfiable(self._cnf, all_models=False)
                if satisfied is False:
                    return satisfied
                return True
            else:
                return True

        cnf = self._cnf.copy()
        at_least_one_param_found = False

        for condition_name, opt in conditions.items():
            for c_equals in self._conditions[condition_name].equals:
                found_params = {}
                for param, value in parameter_values.items():
                    ref_hash = get_hash({"Ref": param})

                    for c_equal_param in c_equals.parameters:
                        if isinstance(c_equal_param, EqualParameter):
                            if c_equal_param.satisfiable is False:
                                raise UnknownSatisfisfaction(
                                    f"Can't resolve satisfaction for {condition_name!r}"
                                )

                    if ref_hash in c_equals.parameters:
                        found_params = {ref_hash: value}

                if not found_params:
                    continue

                at_least_one_param_found = True
                if c_equals.test(found_params):
                    cnf.add_prop(Symbol(c_equals.hash))
                else:
                    cnf.add_prop(Not(Symbol(c_equals.hash)))

                if opt:
                    cnf.add_prop(
                        self._conditions[condition_name].build_true_cnf(
                            self._solver_params
                        )
                    )
                else:
                    cnf.add_prop(
                        self._conditions[condition_name].build_false_cnf(
                            self._solver_params
                        )
                    )

        if at_least_one_param_found is False:
            if self._rules:
                satisfied = satisfiable(self._cnf, all_models=False)
                if satisfied is False:
                    return satisfied
                return True
            else:
                return True

        satisfied = satisfiable(cnf, all_models=False)
        if satisfied is False:
            return satisfied
        return True
