"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json
from collections import deque
from copy import deepcopy
from typing import Any, Iterable

import cfnlint.data.schemas.other.step_functions
from cfnlint.helpers import is_function
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails
from cfnlint.schema.resolver import RefResolver


class StateMachineDefinition(CfnLintJsonSchema):
    id = "E3601"
    shortdesc = "Validate the structure of a StateMachine definition"
    description = (
        "Validate the Definition or DefinitionString inside a "
        "AWS::StepFunctions::StateMachine resource"
    )
    source_url = "https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-state-machine-structure.html"
    tags = ["resources", "statemachine"]

    def __init__(self):
        super().__init__(
            keywords=[
                "Resources/AWS::StepFunctions::StateMachine/Properties",
                # https://github.com/aws-cloudformation/cfn-lint/issues/3518
                # Resources/AWS::StepFunctions::StateMachine/Properties/DefinitionString
            ],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.step_functions, "statemachine.json"
            ),
            all_matches=True,
        )

        self.store = {
            "definition": self.schema,
        }

        self.resolver = RefResolver.from_schema(self.schema, store=self.store)

    def _fix_message(self, err: ValidationError) -> ValidationError:
        if len(err.path) > 1:
            err.message = f"{err.message} at {'/'.join(err.path)!r}"
        for i, c_err in enumerate(err.context):
            err.context[i] = self._fix_message(c_err)
        return err

    def _convert_schema_to_jsonata(self) -> dict[str, Any]:
        schema: dict[str, Any] = deepcopy(self.schema)
        schema["definitions"]["common"] = deepcopy(schema["definitions"]["common"])
        schema["definitions"]["common"]["allOf"] = [
            {
                "properties": {
                    "QueryLanguage": {"const": "JSONata"},
                    "InputPath": False,
                    "OutputPath": False,
                    "Parameters": False,
                    "ResultPath": False,
                    "ResultSelector": False,
                },
            },
        ]
        schema["definitions"]["choice"]["allOf"] = [
            {
                "properties": {
                    "Choices": {
                        "items": {
                            "properties": {
                                "Comment": {"type": "string"},
                                "Condition": {"type": "string"},
                                "Next": {"pattern": "^.{1,128}$", "type": "string"},
                                "Assign": {"type": "object"},
                                "Output": {"type": ["string", "object"]},
                            },
                            "additionalProperties": False,
                            "required": ["Condition", "Next"],
                            "type": "object",
                        }
                    }
                }
            }
        ]
        schema["definitions"]["wait"]["properties"]["Seconds"] = {
            "maximum": 99999999,
            "minimum": 0,
            # JSONata supports JSONata expressions for Seconds
            "type": ["number", "string"],
        }
        for k in ["ItemsPath", "MaxConcurrencyPath"]:
            schema["definitions"]["map"]["properties"][k] = False
        for state_type in ["choice", "fail", "map", "parallel", "pass", "task", "wait"]:
            schema["definitions"][state_type]["properties"]["Arguments"] = {
                "type": ["string", "object"],
            }
        return schema

    def _clean_schema(
        self, validator: Validator, instance: Any
    ) -> Iterable[tuple[dict[str, Any], Validator]]:
        """Yield the appropriate schema and validator depending on QueryLanguage."""
        for ql, ql_validator in get_value_from_path(
            validator, instance, deque(["QueryLanguage"])
        ):
            if ql is None or ql == "JSONPath":
                yield self.schema, ql_validator

            if ql == "JSONata":
                yield self._convert_schema_to_jsonata(), ql_validator

    def _add_transition_error(
        self,
        errors: list[ValidationError],
        states: dict[str, Any],
        target: Any,
        k: str,
        base_path: deque[str | int],
        from_state_name: str,
        field_path: list[str | int],
    ) -> None:
        """Record an error if a transition target does not exist in States."""
        if not isinstance(target, str):
            return
        if target in states:
            return

        path = deque([k, *base_path, "States", from_state_name, *field_path])
        display_path = "/" + "/".join(
            [*map(str, base_path), "States", from_state_name, *map(str, field_path)]
        )
        errors.append(
            ValidationError(
                f"Missing transition target {target!r} at {display_path}",
                path=path,
                rule=self,
            )
        )

    def _validate_states(
        self,
        definition: Any,
        k: str,
        path: deque[str | int] | None = None,
    ) -> ValidationResult:
        """Validate state reachability and transition targets.

        Per the Amazon States Language specification:
          - 'StartAt' must reference an existing state name.
          - Every state must be reachable from 'StartAt'.
          - Every transition target (Next, Default, Choices[].Next, Catch[].Next)
            must reference an existing state name.
        """

        start_at = definition.get("StartAt")
        states = definition.get("States")

        if not isinstance(start_at, str) or not isinstance(states, dict):
            return  # Early return to avoid further checks

        path_list: list[str | int] = list(path) if path is not None else []

        # 1. Validate that StartAt points to an existing state
        if start_at not in states:
            display_path = "/" + "/".join([*map(str, path_list), "StartAt"])
            yield ValidationError(
                f"Missing 'StartAt' target {start_at!r} at {display_path}",
                path=deque([k, *path_list, "StartAt"]),
                rule=self,
            )
            return

        # 2. Traverse reachable states from StartAt and collect errors for
        #    missing transition targets along the way.
        reachable: set[str] = set()
        to_visit: list[str] = [start_at]
        transition_errors: list[ValidationError] = []

        while to_visit:
            current = to_visit.pop(0)
            if current in reachable or current not in states:
                continue

            reachable.add(current)
            state = states[current]
            if not isinstance(state, dict):
                continue

            base_path = deque([*path_list])

            # Next / Default
            for field in ("Next", "Default"):
                target = state.get(field)
                self._add_transition_error(
                    transition_errors,
                    states,
                    target,
                    k,
                    base_path,
                    current,
                    [field],
                )
                if isinstance(target, str) and target in states:
                    to_visit.append(target)

            # Choices[].Next
            for idx, choice in enumerate(state.get("Choices") or []):
                if not isinstance(choice, dict):
                    continue
                target = choice.get("Next")
                self._add_transition_error(
                    transition_errors,
                    states,
                    target,
                    k,
                    base_path,
                    current,
                    ["Choices", idx, "Next"],
                )
                if isinstance(target, str) and target in states:
                    to_visit.append(target)

            # Catch[].Next
            for idx, catch in enumerate(state.get("Catch") or []):
                if not isinstance(catch, dict):
                    continue
                target = catch.get("Next")
                self._add_transition_error(
                    transition_errors,
                    states,
                    target,
                    k,
                    base_path,
                    current,
                    ["Catch", idx, "Next"],
                )
                if isinstance(target, str) and target in states:
                    to_visit.append(target)
            state_type = state.get("Type")

            if state_type == "Parallel":
                for idx, branch in enumerate(state.get("Branches") or []):
                    if isinstance(branch, dict):
                        yield from self._validate_states(
                            branch,
                            k,
                            deque([*path_list, "States", current, "Branches", idx]),
                        )

            if state_type == "Map":
                for sub_key in ("ItemProcessor", "Iterator"):
                    sub = state.get(sub_key)
                    if isinstance(sub, dict):
                        yield from self._validate_states(
                            sub,
                            k,
                            deque([*path_list, "States", current, sub_key]),
                        )

        # 3. Report unreachable states (defined but never visited)
        for state_name in states:
            if state_name not in reachable:
                display_path = "/" + "/".join(
                    [*map(str, path_list), "States", state_name]
                )
                yield ValidationError(
                    f"State {state_name!r} is not reachable at {display_path}",
                    path=deque([k, *path_list, "States", state_name]),
                    rule=self,
                )

        # 4. Emit any transition target errors collected during traversal
        for err in transition_errors:
            yield err

    def _validate_step(
        self,
        validator: Validator,
        substitutions: Any,
        value: Any,
        add_path_to_message: bool,
        k: str,
    ) -> ValidationResult:
        # First run JSON Schema validation
        for err in validator.iter_errors(value):
            if validator.is_type(err.instance, "string"):
                if (
                    err.instance.replace("${", "").replace("}", "").strip()
                    in substitutions
                ):
                    continue
            if add_path_to_message:
                err = self._fix_message(err)

            err.path.appendleft(k)
            if err.schema in [True, False]:
                err.message = (
                    f"Additional properties are not allowed ({err.path[-1]!r} "
                    "was unexpected)"
                )
            if not err.validator or (
                not err.validator.startswith("fn_") and err.validator not in ["cfnLint"]
            ):
                err.rule = self

            yield self._clean_error(err)

        # Then run start/transition/reachability validation on the same value
        yield from self._validate_states(value, k)

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        definition_keys = ["Definition"]
        if not validator.cfn.has_serverless_transform():
            definition_keys.append("DefinitionString")

        substitutions: list[str] = []
        props_substitutions = instance.get("DefinitionSubstitutions", {})
        if validator.is_type(props_substitutions, "object"):
            substitutions = list(props_substitutions.keys())

        # First time child rules are configured against the rule
        # so we can run this now
        for k in definition_keys:
            value = instance.get(k)
            fn_name, _ = is_function(value)
            if fn_name:
                continue
            if not value:
                continue

            add_path_to_message = False
            if validator.is_type(value, "string"):
                try:
                    value = json.loads(value)
                    add_path_to_message = True
                    for schema_obj, schema_validator in self._clean_schema(
                        validator, value
                    ):
                        resolver = RefResolver.from_schema(schema_obj, store=self.store)
                        step_validator = schema_validator.evolve(
                            context=validator.context.evolve(
                                functions=[],
                            ),
                            resolver=resolver,
                            schema=self.schema,
                        )

                        yield from self._validate_step(
                            step_validator, substitutions, value, add_path_to_message, k
                        )
                except json.JSONDecodeError:
                    return
            else:
                for schema_obj, schema_validator in self._clean_schema(
                    validator, value
                ):
                    resolver = RefResolver.from_schema(schema_obj, store=self.store)
                    step_validator = schema_validator.evolve(
                        resolver=resolver,
                        schema=schema_obj,
                    )
                    yield from self._validate_step(
                        step_validator,
                        substitutions,
                        value,
                        add_path_to_message,
                        k,
                    )
