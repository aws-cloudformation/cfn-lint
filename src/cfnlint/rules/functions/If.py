"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.context.conditions.exceptions import Unsatisfiable
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.functions._BaseFn import BaseFn, all_types


class If(BaseFn):
    """Check if Condition exists"""

    id = "E1028"
    shortdesc = "Check Fn::If structure for validity"
    description = "Check Fn::If to make sure its valid.  Condition has to be a string."
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-if"
    tags = ["functions", "if"]

    def __init__(self) -> None:
        super().__init__(
            "Fn::If",
            all_types,
        )
        self.child_rules["W1028"] = None

    def fn_if(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        # validate this function will return the correct type
        errs = list(self.validate_fn_output_types(validator, s, instance))

        key, value = self.key_value(instance)

        errs.extend(
            list(
                self.fix_errors(
                    self.validator(validator, schema).descend(
                        value,
                        self.schema(validator, instance),
                        path=key,
                    )
                )
            )
        )

        if errs:
            yield from iter(errs)
            return

        for i in [1, 2]:
            if validator.context.conditions.regions and all(
                (i == 1)
                not in validator.cfn.conditions.build_scenerios_on_region(
                    value[0], region
                )
                for region in validator.context.regions
            ):
                continue
            # we pass through the functions for the paths down
            # the second and third element of the if
            try:
                element_validator = validator.evolve(
                    context=validator.context.evolve(
                        path=validator.context.path.descend(
                            path=key,
                        ),
                        conditions=validator.context.conditions.evolve(
                            {value[0]: True if i == 1 else False}
                        ),
                    )
                )
                for err in element_validator.descend(
                    instance=value[i], schema=s, path=i
                ):
                    err.path.appendleft(key)
                    yield err
            except Unsatisfiable as e:
                condition = validator.context.conditions.conditions.get(value[0])
                if (
                    validator.context.conditions.regions
                    and condition is not None
                    and condition.is_region
                    and validator.context.conditions.is_reachable(value[0], i == 1)
                ):
                    continue
                # The branch could not be evolved under the current conditions.
                # Only report it as unreachable when the condition truly cannot
                # take this value given the forced facts (resource/output
                # Condition, an enclosing Fn::If, parameter and condition
                # definitions).  When the condition was merely pinned by
                # condition-scenario enumeration (e.g. a schema if/then that
                # walks this subtree once per scenario), the other value is
                # still reachable in its own scenario, so reporting it would be
                # a tautology rather than a reachability finding.
                # See https://github.com/aws-cloudformation/cfn-lint/issues/4673
                if not validator.context.conditions.is_reachable(
                    value[0], True if i == 1 else False
                ):
                    yield ValidationError(
                        f"{[key, i]!r} is not reachable. {e.message}",
                        path=deque([key, i]),
                        rule=self.child_rules["W1028"],
                    )
                element_validator = validator.evolve(
                    context=validator.context.evolve(
                        path=validator.context.path.descend(
                            path=key,
                        ),
                    )
                )
                for err in element_validator.descend(
                    instance=value[i], schema=s, path=i
                ):
                    err.path.appendleft(key)
                    yield err
