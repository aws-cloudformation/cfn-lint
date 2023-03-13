import itertools
import logging
import traceback
from typing import Any, Dict, Iterator, List, Tuple

from z3 import And, Bool, Implies, Not, Solver, sat

from cfnlint.conditions.condition import ConditionNamed
from cfnlint.conditions.equals import Equal

LOGGER = logging.getLogger(__name__)


class Conditions:
    _conditions: Dict[str, ConditionNamed] = {}

    def __init__(self, cfn):
        self._conditions = {}
        try:
            self._init_conditions(cfn=cfn)

        except Exception as err:  # pylint: disable=W0703
            traceback.print_exc()
            LOGGER.debug("While processing conditions got error: %s", err)

    def _init_conditions(self, cfn):
        conditions = cfn.template.get("Conditions")
        if isinstance(conditions, dict):
            for k, _ in conditions.items():
                try:
                    self._conditions[k] = ConditionNamed(k, conditions)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    LOGGER.debug(
                        "Captured error while building condition %s: %s", k, str(e)
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
        if len(condition_names) == 0:
            return

        # if only one condition we will assume its True/False
        if len(condition_names) == 1:
            yield {condition_names[0]: True}
            yield {condition_names[0]: False}
            return

        solver, solver_params = self._build_solver(condition_names)

        # build a large matric of True/False options based on the provided conditions
        for p in itertools.product([True, False], repeat=len(condition_names)):
            params = dict(zip(condition_names, p))
            solver.push()
            for condition_name, opt in params.items():
                if opt:
                    solver.add(
                        self._conditions[condition_name].build_true_solver(
                            solver_params
                        )
                    )
                else:
                    solver.add(
                        self._conditions[condition_name].build_false_solver(
                            solver_params
                        )
                    )

            # if the scenario can be satisfied then return it
            if solver.check() == sat:
                yield params
            solver.pop()

    def check_implies(self, scenarios: Dict[str, bool], implies: str) -> Bool:
        # Based on a bunch of conditions and their Truth/False value
        # determine if implies condition is True any time the scenarios are satisfied
        solver, solver_params = self._build_solver(list(scenarios.keys()) + [implies])

        conditions = []
        for condition_name, opt in scenarios.items():
            if opt:
                conditions.append(
                    self._conditions[condition_name].build_true_solver(solver_params)
                )
            else:
                conditions.append(
                    self._conditions[condition_name].build_false_solver(solver_params)
                )

        implies_condition = self._conditions[implies].build_true_solver(solver_params)

        and_condition = And(conditions)
        solver.add(and_condition)
        solver.add(Not(Implies(and_condition, implies_condition)))
        if solver.check() == sat:
            return True
        return False
