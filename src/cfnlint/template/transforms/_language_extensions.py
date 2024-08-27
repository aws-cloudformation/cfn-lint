"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import hashlib
import json
import logging
import random
import string
import sys
from copy import deepcopy
from typing import Any, Iterator, Mapping, MutableMapping, Tuple

import regex as re

from cfnlint.conditions._utils import get_hash
from cfnlint.decode.node import str_node
from cfnlint.helpers import FUNCTION_FOR_EACH
from cfnlint.template.transforms._types import TransformResult

LOGGER = logging.getLogger("cfnlint")

# initializing size of string
_N = 7

_SCALAR_TYPES = (str, int, float, bool)


class _ResolveError(Exception):
    def __init__(self, message: str, key: Any) -> None:
        super().__init__(message)
        self.key = key


class _ValueError(Exception):
    def __init__(self, message: str, key: Any) -> None:
        super().__init__(message)
        self.key = key


class _TypeError(Exception):
    def __init__(self, message: str, key: Any) -> None:
        super().__init__(message)
        self.key = key


def language_extension(cfn: Any) -> TransformResult:
    transform = _Transform()
    try:
        return transform.transform(cfn)
    except (_ValueError, _TypeError, _ResolveError) as e:
        LOGGER.debug(e, exc_info=True)
        # pylint: disable=import-outside-toplevel
        from cfnlint.match import Match  # pylint: disable=cyclic-import
        from cfnlint.rules.errors import TransformError  # pylint: disable=cyclic-import

        message = "Error transforming template: {0}"
        if hasattr(e.key, "start_mark"):
            sm_line = e.key.start_mark.line + 1
            sm_column = e.key.start_mark.column + 1
        else:
            sm_line = 1
            sm_column = 1
        if hasattr(e.key, "end_mark"):
            em_line = e.key.end_mark.line + 1
            em_column = e.key.end_mark.column + 1
        else:
            em_line = 1
            em_column = 1

        return [
            Match.create(
                linenumber=sm_line,
                columnnumber=sm_column,
                linenumberend=em_line,
                columnnumberend=em_column,
                filename=cfn.filename,
                rule=TransformError(),
                message=message.format(str(e)),
            )
        ], None
    except Exception as e:  # pylint: disable=broad-exception-caught
        LOGGER.debug(e, exc_info=True)
        # pylint: disable=import-outside-toplevel
        from cfnlint.match import Match  # pylint: disable=cyclic-import
        from cfnlint.rules.errors import TransformError  # pylint: disable=cyclic-import

        message = "Error transforming template: {0}"
        return [
            Match.create(
                filename=cfn.filename,
                rule=TransformError(),
                message=message.format(str(e)),
            )
        ], None


class _Transform:
    def __init__(self) -> None:
        self._collections: MutableMapping[str, str] = {}

    def transform(self, cfn: Any) -> TransformResult:
        """Transform the template"""
        return [], self._walk(cfn.template, {}, cfn)

    # pylint: disable=too-many-return-statements
    def _walk(self, item: Any, params: MutableMapping[str, Any], cfn: Any):
        obj = deepcopy(item)
        if isinstance(obj, dict):
            # adjust keys if needed
            if params:
                for k, v in item.items():
                    _, new_k = self._replace_string_params(k, params)
                    if new_k != k:
                        del obj[k]
                        obj[new_k] = v

            for k, v in deepcopy(obj).items():
                # see if key matches Fn::ForEach
                if re.match(FUNCTION_FOR_EACH, k):
                    # only translate the foreach if its valid
                    foreach = _ForEach(k, v, self._collections)
                    # get the values will flatten the foreach
                    for collection_value in foreach.items(cfn):
                        flattened = self._walk(
                            v[2], {**params, **{v[0]: collection_value}}, cfn
                        )
                        for f_k, f_v in flattened.items():
                            if f_k not in obj:
                                obj[f_k] = f_v
                            else:
                                raise _ValueError(
                                    f"Duplicate {f_k} while doing transformation",
                                    f_k,
                                )
                    del obj[k]
                elif k == "Fn::ToJsonString":
                    # extra special handing for this as {} could be a valid value
                    return obj
                elif k == "Fn::Sub":
                    if isinstance(v, str):
                        only_string, obj[k] = self._replace_string_params(v, params)
                        if only_string:
                            return obj[k]
                    if isinstance(v, list):
                        only_string, obj[k][0] = self._replace_string_params(
                            v[0],
                            params,
                        )
                        if only_string:
                            return obj[k][0]
                        if len(v) == 2:
                            obj[k][1] = self._walk(v[1], params, cfn)
                elif k == "Fn::FindInMap":
                    try:
                        mapping = _ForEachValueFnFindInMap(get_hash(v), v)
                        map_value = mapping.value(cfn, params, True, False)
                        # if we can resolve it we will return it
                        if isinstance(map_value, tuple([list]) + _SCALAR_TYPES):
                            return map_value
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        # We couldn't resolve the FindInMap so we are going to
                        # leave it as it is
                        LOGGER.debug("Transform and Fn::FindInMap error: %s", {str(e)})
                    for i, el in enumerate(v):
                        v[i] = self._walk(el, params, cfn)
                    obj[k] = v
                elif k == "Ref":
                    if isinstance(v, str):
                        if v in params:
                            return params[v]
                    elif isinstance(v, dict):
                        r = self._walk(v, params, cfn)
                        if isinstance(r, str):
                            if r in params:
                                return params[r]
                        obj[k] = r
                else:
                    sub_value = self._walk(v, params, cfn)
                    # a sub object may be none or we have returned
                    # an empty object.  We don't want to remove empty
                    # strings "" or 0 (zeros)
                    # Remove `or sub_value == {}` for issue #2896
                    if sub_value is None:
                        del obj[k]
                    else:
                        obj[k] = sub_value
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                obj[i] = self._walk(v, params, cfn)
        return obj

    def _replace_string_params(
        self,
        s: str,
        params: Mapping[str, Any],
    ) -> Tuple[bool, str]:
        pattern = r"(\$|&){[a-zA-Z0-9\.:]+}"
        if not re.search(pattern, s):
            return (True, s)

        new_s = deepcopy(s)
        for k, v in params.items():
            if isinstance(v, dict):
                if sys.version_info.major == 3 and sys.version_info.minor > 8:
                    v = (
                        hashlib.md5(
                            json.dumps(v).encode("utf-8"), usedforsecurity=False
                        )
                        .digest()
                        .hex()[0:4]
                    )
                else:
                    v = hashlib.md5(json.dumps(v).encode("utf-8")).digest().hex()[0:4]
            new_s = re.sub(rf"\$\{{{k}\}}", v, new_s)
            new_s = re.sub(rf"\&\{{{k}\}}", re.sub("[^0-9a-zA-Z]+", "", v), new_s)

        if isinstance(s, str_node):
            new_s = str_node(new_s, s.start_mark, s.end_mark)

        return (not (bool(re.search(pattern, new_s))), new_s)


class _ForEachValue:
    def __init__(self, _hash: str, value: Any = None) -> None:
        if value:
            self._value = value

        self._hash = _hash

    @staticmethod
    def create(obj: Any) -> _ForEachValue:
        _hash = get_hash(obj)
        if isinstance(obj, _SCALAR_TYPES):
            return _ForEachValue(_hash, obj)
        if isinstance(obj, dict):
            if len(obj) != 1:
                raise _ValueError("Object must have only one key", obj)

            for k, v in obj.items():
                if k == "Ref":
                    return _ForEachValueRef(_hash, v)
                if k == "Fn::FindInMap":
                    return _ForEachValueFnFindInMap(_hash, v)

        raise _TypeError(f"Unsupported value {obj!r}", obj)

    # pylint: disable=unused-argument
    def value(
        self, cfn, params: Mapping[str, Any] | None = None, only_params: bool = False
    ):
        return self._value

    @property
    def hash(self):
        return self._hash


class _FnFindInMapDefaultValue(_ForEachValue):
    def __init__(self, _hash: str, value: Any = None) -> None:
        super().__init__(_hash, value)
        if not isinstance(value, dict):
            raise _TypeError(
                "Fn::FindInMap parameter must be an object with key 'DefaultValue'",
                value,
            )
        if len(value) != 1:
            raise _ValueError(
                "Fn::FindInMap parameter only supports 'DefaultValue'", value
            )

        for k, v in value.items():
            if k != "DefaultValue":
                raise _ValueError(
                    "Fn::FindInMap parameter only supports 'DefaultValue'", value
                )
            if isinstance(v, list):
                self._value = [_ForEachValue.create(a) for a in v]
                return
            self._value = _ForEachValue.create(v)

    def value(
        self, cfn, params: Mapping[str, Any] | None = None, only_params: bool = False
    ):
        if params is None:
            params = {}

        if isinstance(self._value, list):
            return [v.value(cfn, params, only_params) for v in self._value]
        return self._value.value(cfn, params, only_params)


class _ForEachValueFnFindInMap(_ForEachValue):
    def __init__(self, _hash: str, obj: Any) -> None:
        super().__init__(_hash)
        if not isinstance(obj, list):
            raise _TypeError("Fn::FindInMap should be a list", obj)

        if len(obj) not in [3, 4]:
            raise _ValueError("Fn::FindInMap requires a list of 3 or 4 values", obj)

        self._map = [
            _ForEachValue.create(obj[0]),
            _ForEachValue.create(obj[1]),
            _ForEachValue.create(obj[2]),
        ]
        if len(obj) == 4:
            self._map.append(_FnFindInMapDefaultValue(get_hash(obj[3]), obj[3]))

        self._obj = obj

    def value(
        self,
        cfn: Any,
        params: Mapping[str, Any] | None = None,
        only_params: bool = False,
        default_on_resolver_failure: bool = True,
    ) -> Any:
        if params is None:
            params = {}
        t_map = deepcopy(self._map)
        mapping = None
        try:
            mapping = cfn.template.get("Mappings", {}).get(
                t_map[0].value(cfn, params, only_params)
            )
        except Exception:  # pylint: disable=broad-exception-caught
            if len(cfn.template.get("Mappings", {}).keys()) == 1:
                mapping = cfn.template.get("Mappings", {}).get(
                    list(cfn.template.get("Mappings", {}).keys())[0]
                )

        try:
            if mapping is None and isinstance(
                t_map[1].value(cfn, params, only_params), str
            ):
                for k, v in cfn.template.get("Mappings", {}).items():
                    if isinstance(v, dict):
                        if t_map[1].value(cfn, params) in v:
                            t_map[0] = _ForEachValue.create(k)
                            mapping = v
                            break
        except _ResolveError:
            pass

        try:
            if mapping is None and isinstance(
                t_map[2].value(cfn, params, only_params), str
            ):
                for m1, mv1 in cfn.template.get("Mappings", {}).items():
                    if isinstance(mv1, dict):
                        for k1, kv1 in mv1.items():
                            if isinstance(kv1, dict):
                                if t_map[2].value(cfn, params, only_params) in kv1:
                                    t_map[1] = _ForEachValue.create(k1)
                                    t_map[0] = _ForEachValue.create(m1)
                                    mapping = mv1
                                    break
        except _ResolveError:
            pass

        if mapping:
            try:
                t_map[1].value(cfn, params, only_params)
            except _ResolveError:
                try:
                    t_map[2].value(cfn, params)
                    for k, v in mapping.items():
                        if isinstance(v, dict):
                            if t_map[2].value(cfn, params, only_params) in v:
                                t_map[1] = _ForEachValue.create(k)
                except _ResolveError:
                    pass

        if mapping:
            try:
                return mapping.get(t_map[1].value(cfn, params, only_params), {}).get(
                    t_map[2].value(cfn, params, only_params)
                )
            except _ResolveError as e:
                if len(self._map) == 4 and default_on_resolver_failure:
                    return self._map[3].value(cfn, params, only_params)
                # no default value and map 1 exists
                try:
                    for _, v in mapping.get(
                        t_map[1].value(cfn, params, only_params), {}
                    ).items():
                        if isinstance(v, list):
                            return v
                except _ResolveError:
                    pass
                raise _ResolveError("Can't resolve Fn::FindInMap", self._obj) from e

        if len(self._map) == 4 and default_on_resolver_failure:
            return self._map[3].value(cfn, params, only_params)
        raise _ResolveError("Can't resolve Fn::FindInMap", self._obj)


class _ForEachValueRef(_ForEachValue):
    def __init__(self, _hash: str, obj: Any) -> None:
        super().__init__(_hash)
        if not isinstance(obj, (str, dict)):
            raise _TypeError("Fn::FindInMap should be a list", obj)

        self._ref = _ForEachValue.create(obj)
        self._obj = obj

    # pylint: disable=too-many-return-statements
    def value(
        self,
        cfn: Any,
        params: Mapping[str, Any] | None = None,
        only_params: bool = False,
    ) -> Any:
        if params is None:
            params = {}
        v = self._ref.value(cfn, params)

        if not isinstance(v, str):
            raise _ResolveError("Can't resolve Fn::Ref", self._obj)

        if v in params:
            return params[v]

        if only_params:
            raise _ResolveError("Can't resolve Fn::Ref", self._obj)

        region = cfn.regions[0]
        account_id = "123456789012"
        partition = "aws"
        if region in ("us-gov-east-1", "us-gov-west-1"):
            partition = "aws-us-gov"
        if region in ("cn-north-1", "cn-northwest-1"):
            partition = "aws-cn"
        if v == "AWS::Region":
            return region

        if v == "AWS::AccountId":
            return account_id

        if v == "AWS::NotificationARNs":
            return [f"arn:{partition}:sns:{region}:{account_id}:notification"]

        if v == "AWS::NoValue":
            return None

        if v == "AWS::Partition":
            return partition

        if v == "AWS::StackId":
            return (
                f"arn:{partition}:cloudformation:"
                f"{region}:{account_id}:"
                "stack/teststack/51af3dc0-da77-11e4-872e-1234567db123"
            )

        if v == "AWS::StackName":
            return "teststack"

        if v == "AWS::URLSuffix":
            if region in ("cn-north-1", "cn-northwest-1"):
                return "amazonaws.com.cn"

            return "amazonaws.com"

        p = cfn.template.get("Parameters", {}).get(v)
        if not p:
            raise _ResolveError("Can't resolve Fn::Ref", self._obj)
        t = p.get("Type", "String")
        if t.startswith("AWS::SSM::Parameter"):
            raise _ResolveError("Can't resolve Fn::Ref", self._obj)
        default = p.get("Default")
        if default:
            if "List" in t:
                return [x.strip() for x in default.split(",")]
            return default
        allowed_values = p.get("AllowedValues", [])
        if len(allowed_values) > 0:
            if "List" in t:
                return [x.strip() for x in allowed_values[0].split(",")]
            return allowed_values[0]

        if "List" in t:
            return [{"Fn::Select": [0, {"Ref": v}]}, {"Fn::Select": [1, {"Ref": v}]}]

        raise _ResolveError("Can't resolve Fn::Ref", self._obj)


class _ForEachCollection:
    def __init__(self, obj: Any) -> None:
        self._collection: list[_ForEachValue] | None = None
        self._obj = obj
        self._fn: _ForEachValue | None = None
        if isinstance(obj, list):
            self._collection = []
            self._string = obj
            for item in obj:
                self._collection.append(_ForEachValue.create(item))
            return
        if isinstance(obj, dict):
            self._fn = _ForEachValue.create(obj)
            return
        raise _TypeError("Collection must be a list or an object", obj)

    def values(
        self, cfn: Any, collection_cache: MutableMapping[str, Any]
    ) -> Iterator[str | dict[Any, Any]]:
        if self._collection:
            for item in self._collection:
                try:
                    yield item.value(cfn, {}, False)
                except _ResolveError:
                    v = "".join(random.choices(string.ascii_letters, k=_N))  # nosec
                    collection_cache[item.hash] = v
                    yield v
            return
        if self._fn:
            try:
                values = self._fn.value(cfn, {}, False)
                if values:
                    if isinstance(values, list):
                        for value in values:
                            if isinstance(value, (str, dict)):
                                yield value
                            else:
                                raise _ValueError(
                                    (
                                        "Fn::ForEach collection value "
                                        f"must be a {_SCALAR_TYPES!r}"
                                    ),
                                    self._obj,
                                )
                        return
                    raise _ValueError(
                        "Fn::ForEach collection must return a list", self._obj
                    )
            except _ResolveError:
                if self._fn.hash in collection_cache:
                    yield from iter(collection_cache[self._fn.hash])
                else:
                    collection_cache[self._fn.hash] = []
                    for _ in range(0, 2):
                        v = "".join(random.choices(string.ascii_letters, k=_N))  # nosec
                        collection_cache[self._fn.hash].append(v)
                        yield v
                return
        raise _ResolveError("Fn::ForEach could not be resolved", self._obj)


class _ForEachOutput:
    def __init__(self, obj: Any) -> None:
        if isinstance(obj, dict):
            self._output = obj
            return
        raise _TypeError("Output must be a dict", obj)

    def value(self) -> Any:
        return self._output


class _ForEach:
    def __init__(
        self, key: str, value: Any, collection_cache: MutableMapping[str, str]
    ) -> None:
        self._key = key
        self._collection_cache: MutableMapping[str, str] = collection_cache
        if not isinstance(value, list):
            raise _TypeError("Fn::ForEach values must be a list of 3 elements", key)

        if not len(value) == 3:
            raise _TypeError("Fn::ForEach values must be a list of 3 elements", key)

        self._identifier = _ForEachValue.create(value[0])
        self._collection = _ForEachCollection(value[1])
        self._output = _ForEachOutput(value[2])

    def items(self, cfn: Any) -> Iterator[str | dict[str, str]]:
        items = self._collection.values(cfn, self._collection_cache)
        yield from iter(items)
