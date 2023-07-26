"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import itertools
import logging
import traceback
from typing import Any, Dict, Generator, Iterator, List, Tuple

from sympy import And, Implies, Not, Symbol
from sympy.assumptions.cnf import EncodedCNF
from sympy.logic.boolalg import BooleanFalse, BooleanTrue
from sympy.logic.inference import satisfiable

from cfnlint.conditions._utils import get_hash
from cfnlint.conditions.condition import ConditionNamed
from cfnlint.conditions.equals import Equal

LOGGER = logging.getLogger(__name__)


class Conditions:
    """Conditions provides the logic for relating individual condition together"""

    _conditions: Dict[str, ConditionNamed]
    _parameters: Dict[str, List[str]]  # Dict of parameters with AllowedValues hashed
    _max_scenarios: int = 128  # equivalent to 2^7

    def __init__(self, cfn):
        self._conditions = {}
        self._parameters = {}
        self._init_conditions(cfn=cfn)
        self._init_parameters(cfn=cfn)
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

    def get(self, name: str, default: Any = None) -> ConditionNamed:
        """Return the conditions"""
        return self._conditions.get(name, default)

    def _build_cnf(
        self, condition_names: List[str]
    ) -> Tuple[EncodedCNF, Dict[str, Any]]:
        cnf = EncodedCNF()

        # build parameters and equals into solver
        equal_vars: Dict[str, Symbol] = {}

        equals: Dict[str, Equal] = {}
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
                                # equivalent to NAND logic. We want to make sure that both equals
                                # are not both True at the same time
                                cnf.add_prop(
                                    ~(equal_vars[c_equal.hash] & equal_vars[e_hash])
                                )
                equals[c_equal.hash] = c_equal

        # Determine if a set of conditions can never be all false
        allowed_values = self._parameters.copy()
        if allowed_values:
            # iteration 1 cleans up all the hash values from allowed_values to know if we
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

        return (cnf, equal_vars)

    def build_scenarios(self, condition_names: List[str]) -> Iterator[Dict[str, bool]]:
        """Given a list of condition names this function will yield scenarios that represent
        those conditions and there result (True/False)

        Args:
            condition_names (List[str]): A list of condition names

        Returns:
            Iterator[Dict[str, bool]]: yield dict objects of {ConditionName: True/False}
        """
        # nothing to yield if there are no conditions
        if len(condition_names) == 0:
            return

        try:
            # build a large matric of True/False options based on the provided conditions
            scenarios_returned = 0
            for p in itertools.product([True, False], repeat=len(condition_names)):
                cnf = self._cnf.copy()
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
                    yield params
                    scenarios_returned += 1

                # On occassions people will use a lot of non-related conditions
                # this is fail safe to limit the maximum number of responses
                if scenarios_returned >= self._max_scenarios:
                    return
        except KeyError:
            # KeyError is because the listed condition doesn't exist because of bad
            #  formatting or just the wrong condition name
            return

    def check_implies(self, scenarios: Dict[str, bool], implies: str) -> bool:
        """Based on a bunch of scenario conditions and their Truth/False value
        determine if implies condition is True any time the scenarios are satisfied
        solver, solver_params = self._build_solver(list(scenarios.keys()) + [implies])

        Args:
            scenarios (Dict[str, bool]): A list of condition names and if they are True or False
            implies: the condition name that we are implying will also be True

        Returns:
            bool: if the implied condition will be True if the scenario is True
        """
        try:
            cnf = self._cnf.copy()
            # if the implies condition has to be false in the scenarios we
            # know it can never be true
            if not scenarios.get(implies, True):
                return False

            conditions = []
            for condition_name, opt in scenarios.items():
                if opt:
                    conditions.append(
                        self._conditions[condition_name].build_true_cnf(
                            self._solver_params
                        )
                    )
                else:
                    conditions.append(
                        self._conditions[condition_name].build_false_cnf(
                            self._solver_params
                        )
                    )

            implies_condition = self._conditions[implies].build_true_cnf(
                self._solver_params
            )

            and_condition = And(*conditions)
            cnf.add_prop(and_condition)

            # if the implies condition has to be true already then we don't
            # need to imply it
            if not scenarios.get(implies):
                cnf.add_prop(Not(Implies(and_condition, implies_condition)))
            if satisfiable(cnf):
                return True

            return False
        except KeyError:
            # KeyError is because the listed condition doesn't exist because of bad
            #  formatting or just the wrong condition name
            return True

    def build_scenerios_on_region(
        self, condition_name: str, region: str
    ) -> Generator[bool, None, None]:
        """Based on a region validate if the condition_name coudle be true

        Args:
            condition_name (str): The name of the condition we are validating against
            region (str): the name of the region

        Returns:
            Generator[bool]: Returns True, False, or True and False depending on if the
               condition could be True, False or both based on the region parameter
        """
        if not isinstance(condition_name, str):
            return
        cnf_region = self._cnf.copy()
        found_region = False
        if condition_name not in self._conditions:
            return
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
            yield True
            yield False
            return

        cnf_test = cnf_region.copy()
        cnf_test.add_prop(
            self._conditions[condition_name].build_true_cnf(self._solver_params)
        )
        if satisfiable(cnf_test):
            yield True

        cnf_test = cnf_region.copy()
        cnf_test.add_prop(
            self._conditions[condition_name].build_false_cnf(self._solver_params)
        )
        if satisfiable(cnf_test):
            yield False
