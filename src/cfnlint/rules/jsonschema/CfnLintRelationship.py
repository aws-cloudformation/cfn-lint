"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any, Iterator, Sequence

from cfnlint.helpers import is_function
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules import CloudFormationLintRule


class CfnLintRelationship(CloudFormationLintRule):
    def __init__(
        self, keywords: Sequence[str] | None = None, relationship: str | None = None
    ) -> None:
        super().__init__()
        self.keywords = keywords or []
        self.relationship = relationship or ""
        self.parent_rules = ["E1101"]

    def _get_relationship_fn_if(
        self, validator: Validator, key: Any, value: Any, path: deque[str | int]
    ) -> Iterator[tuple[Any, Validator]]:
        if not isinstance(value, list) or len(value) != 3:
            return
        condition = value[0]
        # True path
        status = {k: set([v]) for k, v in validator.context.conditions.status.items()}
        if condition not in status:
            status[condition] = set([True, False])
        for scenario in validator.cfn.conditions.build_scenarios(status):
            if_validator = validator.evolve(
                context=validator.context.evolve(
                    conditions=validator.context.conditions.evolve(
                        status=scenario,
                    )
                )
            )

            i = 1 if scenario[condition] else 2
            for r, v in self._get_relationship(
                validator.evolve(
                    context=if_validator.context.evolve(
                        path=if_validator.context.path.descend(path=key).descend(path=i)
                    )
                ),
                value[i],
                path.copy(),
            ):
                yield r, v

    def _get_relationship_list(
        self, validator: Validator, key: Any, instance: Any, path: deque[str | int]
    ) -> Iterator[tuple[Any, Validator]]:
        if key == "*":
            for i, v in enumerate(instance):
                for r, v in self._get_relationship(
                    validator.evolve(
                        context=validator.context.evolve(
                            path=validator.context.path.descend(path=i)
                        ),
                    ),
                    v,
                    path.copy(),
                ):
                    yield r, v

    def _get_relationship(
        self, validator: Validator, instance: Any, path: deque[str | int]
    ) -> Iterator[tuple[Any, Validator]]:
        fn_k, fn_v = is_function(instance)
        if fn_k == "Fn::If":
            yield from self._get_relationship_fn_if(validator, fn_k, fn_v, path)
            return

        if fn_k == "Ref" and fn_v == "AWS::NoValue":
            yield None, validator.evolve(
                context=validator.context.evolve(
                    path=validator.context.path.descend(path=fn_k)
                )
            )
            return

        if not path:
            yield instance, validator
            return

        key = path.popleft()
        if isinstance(instance, list):
            yield from self._get_relationship_list(validator, key, instance, path)
            return

        if not isinstance(instance, dict):
            return

        for r, v in self._get_relationship(
            validator.evolve(
                context=validator.context.evolve(
                    path=validator.context.path.descend(path=key)
                )
            ),
            instance.get(key),
            path.copy(),
        ):
            yield r, v

    def _validate_get_relationship_parameters(self, validator: Validator) -> bool:
        if len(validator.context.path.path) < 2:
            return False

        if "Resources" != validator.context.path.path[0]:
            return False

        if not validator.cfn.graph:
            return False

        if len(self.relationship.split("/")) < 2:
            return False

        return True

    def get_relationship(self, validator: Validator) -> Iterator[tuple[Any, Validator]]:
        if not self._validate_get_relationship_parameters(validator):
            return

        resource_name = validator.context.path.path[1]
        path = self.relationship.split("/")

        # get related resources by ref/getatt to the source
        # and relationship types
        for edge in validator.cfn.graph.graph.out_edges(resource_name):  # type: ignore
            other_resource = validator.cfn.template.get(path[0], {}).get(edge[1], {})

            if other_resource.get("Type") != path[1]:
                continue

            condition = other_resource.get("Condition", None)
            if condition:
                if not validator.cfn.conditions.implies(
                    validator.context.conditions.status, condition
                ):
                    continue
                validator = validator.evolve(
                    context=validator.context.evolve(
                        conditions=validator.context.conditions.evolve(
                            {
                                condition: True,
                            }
                        )
                    )
                )
            # validate reosurce type

            for r, v in self._get_relationship(
                validator, other_resource, deque(path[2:])
            ):
                yield r, v.evolve()

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        raise NotImplementedError("validate not implemented")
