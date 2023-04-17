from __future__ import annotations

from typing import TYPE_CHECKING, List, Union

from jsonschema import exceptions

from cfnlint.jsonschema._utils import Unset

if TYPE_CHECKING:
    from cfnlint.rules import CloudFormationLintRule


_unset = Unset()


class ValidationError(exceptions.ValidationError):
    def __init__(
        self,
        message,
        validator=_unset,
        path=(),
        cause=None,
        context=(),
        validator_value=_unset,
        instance=_unset,
        schema=_unset,
        schema_path=(),
        parent=None,
        type_checker=_unset,
        extra_args=None,
        rule: Union[CloudFormationLintRule, None] = None,
        path_override: Union[List, None] = None,
    ):
        super().__init__(
            message=message,
            validator=validator,
            path=path,
            cause=cause,
            context=context,
            validator_value=validator_value,
            instance=instance,
            schema=schema,
            schema_path=schema_path,
            parent=parent,
            type_checker=type_checker,
        )
        self.extra_args = extra_args or {}
        self.rule = rule
        self.path_override = path_override

    def _set(self, type_checker=None, **kwargs):
        if type_checker is not None and self._type_checker is _unset:
            self._type_checker = type_checker

        for k, v in kwargs.items():
            if getattr(self, k) is _unset:
                setattr(self, k, v)


class UndefinedTypeCheck(Exception):
    """
    A type checker was asked to check a type it did not have registered.
    """

    def __init__(self, t):
        self.t = t

    def __str__(self):
        return f"Type {self.t!r} is unknown to this type checker"
