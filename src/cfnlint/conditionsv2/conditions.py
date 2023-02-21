import logging
from z3 import Solver, Not, Bool, sat, unsat, And, Implies
from typing import List, Dict, Optional, MutableSet, Set, Tuple, Any, Iterator
import cfnlint.helpers
import traceback
import itertools
from cfnlint.conditionsv2.condition import Condition, ConditionNamed, ConditionPath
from cfnlint.conditionsv2._utils import get_hash
from cfnlint.conditionsv2.equals import Equal, EqualParameter

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
            for k, v in conditions.items():
                try:
                    self._conditions[k] = ConditionNamed(k, conditions)
                except Exception as e:
                    LOGGER.debug(
                        f"Captured error while building condition {k}: {str(e)} "
                    )

    def get_parameters(
        self, conditions: Optional[List[str]] = None
    ) -> Dict[EqualParameter, List[str]]:
        results: Dict[EqualParameter, Set[str]] = {}
        try:
            for k, v in self._conditions.items():
                if not conditions or (conditions and k in conditions):
                    for param in v.get_parameters():
                        if param not in results:
                            results[param] = set([k])
                        else:
                            results[param].add(k)
        except:
            traceback.print_exc()
        return results

    def get_equals(
        self, conditions: Optional[List[str]] = None
    ) -> Dict[Equal, List[str]]:
        results: Dict[str, Set[Equal]] = {}
        try:
            for k, v in self._conditions.items():
                if not conditions or (conditions and k in conditions):
                    equals = v.get_equals()
                    results[k] = set(equals)
        except:
            traceback.print_exc()
        return results

    def _build_solver(
        self, condition_names: List[str]
    ) -> Tuple[Solver, Dict[str, Any]]:
        solver = Solver()

        # build parameters and equals into solver
        vars: Dict[str, Any] = {}

        equals: Dict[str, Equal] = {}
        for condition_name in condition_names:
            c_equals = self._conditions[condition_name].get_equals()
            for c_equal in c_equals:
                # check to see if equals already matches another one
                if c_equal.hash in vars:
                    continue

                vars[c_equal.hash] = Bool(c_equal.hash)
                # See if parameter in this equals is the same as another equals
                for param in c_equal.get_parameters():
                    for e_hash, e_equals in equals.items():
                        if param in e_equals.get_parameters():
                            solver.add(Not(And(vars[c_equal.hash], vars[e_hash])))
                equals[c_equal.hash] = c_equal
                
        return (solver, vars)

    def build_scenarios(self, condition_names: List[str]) -> Iterator[Dict[str, bool]]:
        if len(condition_names) == 0:
            return

        # if only one condition we will assume its True/False
        if len(condition_names) == 1:
            yield {condition_names[0]: True}
            yield {condition_names[0]: False}
            return

        solver, vars = self._build_solver(condition_names)

        for p in itertools.product([True, False], repeat=len(condition_names)):
            params = dict(zip(condition_names, p))
            solver.push()
            for condition_name, opt in params.items():
                if opt:
                    solver.add(self._conditions[condition_name].build_true_solver(vars))
                else:
                    solver.add(
                        self._conditions[condition_name].build_false_solver(vars)
                    )

            if solver.check() == sat:
                yield params
            solver.pop()

    def check_implies(self, scenarios: Dict[str, bool], implies: str) -> Bool:
        solver, vars = self._build_solver(list(scenarios.keys()) + [implies])

        conditions = []
        for condition_name, opt in scenarios.items():
            if opt:
                conditions.append(
                    self._conditions[condition_name].build_true_solver(vars)
                )
            else:
                conditions.append(
                    self._conditions[condition_name].build_false_solver(vars)
                )

        implies_condition = self._conditions[implies].build_true_solver(vars)

        and_condition = And(conditions)
        solver.add(and_condition)
        solver.add(Not(Implies(and_condition, implies_condition)))
        if solver.check() == sat:
            return True
        return False
