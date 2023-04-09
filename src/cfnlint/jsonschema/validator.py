from __future__ import annotations

import reprlib
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, Optional

import attr
from jsonschema import exceptions
from jsonschema.validators import RefResolver, validator_for

from cfnlint.helpers import load_resource
from cfnlint.jsonschema import _types, _validators
from cfnlint.jsonschema.exceptions import ValidationError

if TYPE_CHECKING:
    from cfnlint.rules import CloudFormationLintRule
    from cfnlint.template import Template


def _id_of(schema):
    """
    Return the ID of a schema for recent JSON Schema drafts.
    """
    return schema.get("$id", "")


_cfn_validators: Dict[str, Callable[[Any, Any, Any, Any], Any]] = {
    "$ref": _validators.ref,
    "additionalItems": _validators.additionalItems,
    "additionalProperties": _validators.additionalProperties,
    "allOf": _validators.allOf,
    "anyOf": _validators.anyOf,
    "const": _validators.const,
    "contains": _validators.contains,
    "dependencies": _validators.dependencies,
    "enum": _validators.enum,
    "exclusiveMaximum": _validators.exclusiveMaximum,
    "exclusiveMinimum": _validators.exclusiveMinimum,
    "if": _validators.if_,
    "items": _validators.items,
    "maxItems": _validators.maxItems,
    "maxLength": _validators.maxLength,
    "maxProperties": _validators.maxProperties,
    "maximum": _validators.maximum,
    "minItems": _validators.minItems,
    "minLength": _validators.minLength,
    "minProperties": _validators.minProperties,
    "minimum": _validators.minimum,
    "multipleOf": _validators.multipleOf,
    "not": _validators.not_,
    "oneOf": _validators.oneOf,
    "pattern": _validators.pattern,
    "patternProperties": _validators.patternProperties,
    "properties": _validators.properties,
    "propertyNames": _validators.propertyNames,
    "required": _validators.required,
    "type": _validators.type,
    "uniqueItems": _validators.uniqueItems,
}


def create(
    validators=(),
    cfn: Optional[Template] = None,
    rules: Optional[Dict[str, CloudFormationLintRule]] = None,
):
    """
    Create a new validator class.
    Arguments:
        validators (collections.abc.Mapping):
            a mapping from names to callables, where each callable will
            validate the schema property with the given name.
            Each callable should take 4 arguments:
                1. a validator instance,
                2. the value of the property being validated within the
                   instance
                3. the instance
                4. the schema
    Returns:
        a new `jsonschema.protocols.Validator` class
    """
    applicable_validators = _validators.ignore_ref_siblings

    validators_arg = _cfn_validators.copy()
    validators_arg.update(validators)
    if rules is not None:
        for js in validators_arg:
            rule = rules.get(js)
            if rule is not None:
                if hasattr(rule, "validate_configure") and callable(
                    getattr(rule, "validate_configure")
                ):
                    rule.validate_configure(cfn)
                if hasattr(rule, js) and callable(getattr(rule, js)):
                    func = getattr(rule, js)
                    validators_arg[js] = func

    @attr.s
    class Validator:
        """
        The protocol to which all validator classes adhere.
        Arguments:
            schema:
                The schema that the validator object will validate with.
                It is assumed to be valid, and providing
                an invalid schema can lead to undefined behavior. See
                `Validator.check_schema` to validate a schema first.
            resolver:
                a resolver that will be used to resolve :kw:`$ref`
                properties (JSON references). If unprovided, one will be created.
            format_checker:
                if provided, a checker which will be used to assert about
                :kw:`format` properties present in the schema. If unprovided,
                *no* format validation is done, and the presence of format
                within schemas is strictly informational. Certain formats
                require additional packages to be installed in order to assert
                against instances. Ensure you've installed `jsonschema` with
                its `extra (optional) dependencies <index:extras>` when
                invoking ``pip``.
        """

        VALIDATORS = dict(validators_arg)
        META_SCHEMA = dict(
            load_resource(
                "cfnlint.data.schemas.extensions.json_schema", filename=("draft7.json")
            )
        )
        TYPE_CHECKER = _types.cfn_type_checker
        FORMAT_CHECKER = None
        ID_OF = staticmethod(_id_of)

        schema = attr.ib(repr=reprlib.repr)
        resolver = attr.ib(default=None, repr=False)
        format_checker = attr.ib(default=None)

        def __attrs_post_init__(self):
            if self.resolver is None:
                self.resolver = RefResolver.from_schema(
                    self.schema,
                    id_of=_id_of,
                )

        def is_type(self, instance: Any, t: str) -> bool:
            """
            Check if the instance is of the given (JSON Schema) type.
            Arguments:
                instance:
                    the value to check
                t:
                    the name of a known (JSON Schema) type
            Returns:
                whether the instance is of the given type
            Raises:
                `jsonschema.exceptions.UnknownType`:
                    if ``type`` is not a known type
            """
            try:
                return self.TYPE_CHECKER.is_type(instance, t)
            except exceptions.UndefinedTypeCheck as e:
                raise exceptions.UnknownType(t, instance, self.schema) from e

        def is_valid(self, instance: Any) -> bool:
            """
            Check if the instance is valid under the current `schema`.
            Returns:
                whether the instance is valid or not
            >>> schema = {"maxItems" : 2}
            >>> Draft202012Validator(schema).is_valid([2, 3, 4])
            False
            """
            error = next(self.iter_errors(instance), None)
            return error is None

        def iter_errors(self, instance: Any) -> Iterable[ValidationError]:
            r"""
            Lazily yield each of the validation errors in the given instance.
            >>> schema = {
            ...     "type" : "array",
            ...     "items" : {"enum" : [1, 2, 3]},
            ...     "maxItems" : 2,
            ... }
            >>> v = Draft202012Validator(schema)
            >>> for error in sorted(v.iter_errors([2, 3, 4]), key=str):
            ...     print(error.message)
            4 is not one of [1, 2, 3]
            [2, 3, 4] is too long
            .. deprecated:: v4.0.0
                Calling this function with a second schema argument is deprecated.
                Use `Validator.evolve` instead.
            """
            _schema = self.schema

            if self.is_type(instance, "object"):
                if len(instance) == 1:
                    for k, v in instance.items():
                        # if the element is a condition lets evaluate both the
                        # true and false paths of the condition
                        if k == "Fn::If":
                            if len(v) == 3:
                                # just need to evaluate the second and third element
                                # in the list
                                for i in range(1, 3):
                                    for error in self.iter_errors(instance=v[i]):
                                        # add the paths for the elements we have removed
                                        error.path.appendleft(i)
                                        error.path.appendleft("Fn::If")
                                        yield error
                            return
                        if k == "Ref":
                            if v == "AWS::NoValue":
                                # This is equivalent to an empty object
                                instance = {}
            for k, v in applicable_validators(_schema):
                validator = self.VALIDATORS.get(k)
                if validator is None:
                    continue

                errors = validator(self, v, instance, _schema) or ()
                for error in errors:
                    error.set(
                        validator=k,
                        validator_value=v,
                        instance=instance,
                        schema=_schema,
                        type_checker=self.TYPE_CHECKER,
                    )
                    if k not in {"if", "$ref"}:
                        error.schema_path.appendleft(k)
                    yield error

        def validate(self, instance: Any) -> None:
            """
            Check if the instance is valid under the current `schema`.
            Raises:
                `jsonschema.exceptions.ValidationError`:
                    if the instance is invalid
            >>> schema = {"maxItems" : 2}
            >>> Draft202012Validator(schema).validate([2, 3, 4])
            Traceback (most recent call last):
                ...
            ValidationError: [2, 3, 4] is too long
            """
            for error in self.iter_errors(instance):
                raise error

        def evolve(self, **kwargs) -> "Validator":
            """
            Create a new validator like this one, but with given changes.
            Preserves all other attributes, so can be used to e.g. create a
            validator with a different schema but with the same :kw:`$ref`
            resolution behavior.
            >>> validator = Draft202012Validator({})
            >>> validator.evolve(schema={"type": "number"})
            Draft202012Validator(schema={'type': 'number'}, format_checker=None)
            The returned object satisfies the validator protocol, but may not
            be of the same concrete class! In particular this occurs
            when a :kw:`$ref` occurs to a schema with a different
            :kw:`$schema` than this one (i.e. for a different draft).
            >>> validator.evolve(
            ...     schema={"$schema": Draft7Validator.META_SCHEMA["$id"]}
            ... )
            Draft7Validator(schema=..., format_checker=None)
            """
            cls = self.__class__

            schema = kwargs.setdefault("schema", self.schema)
            NewValidator = validator_for(schema, default=cls)

            for field in attr.fields(cls):
                if not field.init:
                    continue
                attr_name = field.name  # To deal with private attributes.
                init_name = attr_name if attr_name[0] != "_" else attr_name[1:]
                if init_name not in kwargs:
                    kwargs[init_name] = getattr(self, attr_name)

            return NewValidator(**kwargs)

        def descend(self, instance, schema, path=None, schema_path=None):
            for error in self.evolve(schema=schema).iter_errors(instance):
                if path is not None:
                    error.path.appendleft(path)
                if schema_path is not None:
                    error.schema_path.appendleft(schema_path)
                yield error

    return Validator


CfnValidator = create(
    validators=(),
)
