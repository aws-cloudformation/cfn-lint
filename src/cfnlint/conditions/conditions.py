import itertools
import logging
import traceback
from typing import Any, Dict, Iterator, List, Tuple

from z3 import And, Bool, Implies, Not, Solver, sat

from cfnlint.conditions.condition import ConditionNamed
from cfnlint.conditions.equals import Equal

LOGGER = logging.getLogger(__name__)


class Conditions:
    """Conditions provides the logic for relating individual condition together"""

    _conditions: Dict[str, ConditionNamed] = {}
    _max_scenarios: int = 120  # equivalent to 5!

    def __init__(self, cfn):
        self._conditions = {}
        self._init_conditions(cfn=cfn)
        self._solver, self._solver_params = self._build_solver(
            list(self._conditions.keys())
        )

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

    def _build_solver(
        self, condition_names: List[str]
    ) -> Tuple[Solver, Dict[str, Any]]:
        solver = Solver()

        # build parameters and equals into solver
        equal_vars: Dict[str, Any] = {}

        equals: Dict[str, Equal] = {}
        for condition_name in condition_names:
            c_equals = self._conditions[condition_name].get_equals()
            for c_equal in c_equals:
                # check to see if equals already matches another one
                if c_equal.hash in equal_vars:
                    continue

                equal_vars[c_equal.hash] = Bool(c_equal.hash)
                # See if parameter in this equals is the same as another equals
                for param in c_equal.get_parameters():
                    for e_hash, e_equals in equals.items():
                        if param in e_equals.get_parameters():
                            # equivalent to NAND logic. We want to make sure that both equals
                            # are not both True at the same time
                            solver.add(
                                Not(And(equal_vars[c_equal.hash], equal_vars[e_hash]))
                            )
                equals[c_equal.hash] = c_equal

        return (solver, equal_vars)

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

        # if only one condition we will assume its True/False
        if len(condition_names) == 1:
            yield {condition_names[0]: True}
            yield {condition_names[0]: False}
            return

        try:
            # build a large matric of True/False options based on the provided conditions
            scenarios_returned = 0
            for p in itertools.product([True, False], repeat=len(condition_names)):
                params = dict(zip(condition_names, p))
                self._solver.push()
                for condition_name, opt in params.items():
                    if opt:
                        self._solver.add(
                            self._conditions[condition_name].build_true_solver(
                                self._solver_params
                            )
                        )
                    else:
                        self._solver.add(
                            self._conditions[condition_name].build_false_solver(
                                self._solver_params
                            )
                        )

                # if the scenario can be satisfied then return it
                if self._solver.check() == sat:
                    yield params
                    scenarios_returned += 1
                self._solver.pop()

                # On occassions people will use a lot of non-related conditions
                # this is fail safe to limit the maximum number of responses
                if scenarios_returned >= self._max_scenarios:
                    return
        except KeyError:
            # KeyError is because the listed condition doesn't exist because of bad
            #  formatting or just the wrong condition name
            return

    def check_implies(self, scenarios: Dict[str, bool], implies: str) -> Bool:
        """Based on a bunch of scenario conditions and their Truth/False value
        determine if implies condition is True any time the scenarios are satisfied
        solver, solver_params = self._build_solver(list(scenarios.keys()) + [implies])

        Args:
            scenarios (Dict[str, bool]): A list of condition names and if they are True or False
            implies: the condition name that we are implying will also be True

        Returns:
            Bool: if the implied condition will be True if the scenario is True
        """
        try:
            # if the implies condition has to be false in the scenarios we
            # know it can never be true
            if not scenarios.get(implies, True):
                return False

            self._solver.push()
            conditions = []
            for condition_name, opt in scenarios.items():
                if opt:
                    conditions.append(
                        self._conditions[condition_name].build_true_solver(
                            self._solver_params
                        )
                    )
                else:
                    conditions.append(
                        self._conditions[condition_name].build_false_solver(
                            self._solver_params
                        )
                    )

            implies_condition = self._conditions[implies].build_true_solver(
                self._solver_params
            )

            and_condition = And(conditions)
            self._solver.add(and_condition)
            # if the implies condition has to be true already then we don't
            # need to imply it
            if not scenarios.get(implies):
                self._solver.add(Not(Implies(and_condition, implies_condition)))
            if self._solver.check() == sat:
                self._solver.pop()
                return True

            self._solver.pop()
            return False
        except KeyError:
            # KeyError is because the listed condition doesn't exist because of bad
            #  formatting or just the wrong condition name
            return True
