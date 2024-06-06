"""
Copyright (c) 2013 Julian Berman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

SPDX-License-Identifier: MIT
"""

# Code is taken from jsonschema package and adapted CloudFormation use
# https://github.com/python-jsonschema/jsonschema
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Mapping, Sequence
from urllib.parse import unquote, urldefrag, urljoin

from cfnlint.schema.resolver._exceptions import RefResolutionError
from cfnlint.schema.resolver._utils import id_of

_SUBSCHEMAS_KEYWORDS = ("$id", "id", "$anchor", "$dynamicAnchor")


def _match_subschema_keywords(value):
    for keyword in _SUBSCHEMAS_KEYWORDS:
        if keyword in value:
            yield keyword, value


def _search_schema(schema, matcher):
    """Breadth-first search routine."""
    values = deque([schema])
    while values:
        value = values.pop()
        if not isinstance(value, dict):
            continue
        yield from matcher(value)
        values.extendleft(value.values())


def _match_keyword(keyword):
    def matcher(value):
        if keyword in value:
            yield value

    return matcher


@dataclass
class RefResolver:
    referrer: Any = field(init=True)
    base_uri: str = field(init=True, default="")
    _id_of: Any = field(init=False, default=id_of)
    _scopes_stack: Any = field(init=False)
    _urljoin_cache: Any = field(init=True, default=None)
    _cache: Any = field(init=True, default=None)
    _cache_cfn_pointer: Any = field(init=True, default=None)
    store: Any = field(init=True, default=None)

    def __post_init__(self):
        self._scopes_stack = [self.base_uri]
        if self._cache is None:
            self._cache = lru_cache(1024)(self.resolve_from_url)
        if self._cache_cfn_pointer is None:
            self._cache_cfn_pointer = lru_cache(1024)(self.resolve_cfn_pointer)
        if self._urljoin_cache is None:
            self._urljoin_cache = lru_cache(1024)(urljoin)
        if self.store is None:
            self.store = {}
            self.store.update(
                (schema["$id"], schema)
                for schema in self.store.values()
                if isinstance(schema, Mapping) and "$id" in schema
            )

    @classmethod
    def from_schema(cls, schema, **kwargs):
        """
        Construct a resolver from a JSON schema object.

        Arguments:

            schema:

                the referring schema

        Returns:

            `RefResolver`
        """
        return cls(base_uri=id_of(schema), referrer=schema, **kwargs)

    def push_scope(self, scope):
        """
        Enter a given sub-scope.

        Treats further dereferences as being performed underneath the
        given scope.
        """
        self._scopes_stack.append(
            self._urljoin_cache(self.resolution_scope, scope),
        )

    def pop_scope(self):
        """
        Exit the most recent entered scope.

        Treats further dereferences as being performed underneath the
        original scope.

        Don't call this method more times than `push_scope` has been
        called.
        """
        try:
            self._scopes_stack.pop()
        except IndexError as e:
            raise RefResolutionError(
                "Failed to pop the scope from an empty stack. "
                "`pop_scope()` should only be called once for every "
                "`push_scope()`",
            ) from e

    def resolve_from_url(self, url):
        """
        Resolve the given URL.
        """
        url, fragment = urldefrag(url)
        if url:
            try:
                document = self.store[url]
            except KeyError as e:
                raise RefResolutionError(
                    "Failed to pop the scope from an empty stack. "
                    "`pop_scope()` should only be called once for every "
                    "`push_scope()`",
                ) from e
        else:
            document = self.referrer

        return self.resolve_fragment(document, fragment)

    def resolve(self, ref):
        """
        Resolve the given reference.
        """
        url = self._urljoin_cache(self.resolution_scope, ref).rstrip("/")
        match = self._find_in_subschemas(url)
        if match is not None:
            return match

        return url, self._cache(url)

    def resolve_cfn_pointer(self, pointer: str) -> dict[str, Any]:
        """
        Resolve the given cfn pointer.

        /properties/Tags/*/Name
        /properties/SourceConfiguration/ApplicationName
        """

        # cfn pointers don't cross schemas so there is no remote URL to
        # to worry about

        schema = self.referrer

        # to handle custom resources
        if pointer == "/properties/CfnLintAllTypes":
            return {
                "type": [
                    "string",
                    "integer",
                    "number",
                    "boolean",
                    "object",
                    "array",
                ]
            }
        elif pointer == "/properties/CfnLintStringType":
            return {
                "type": [
                    "string",
                ]
            }

        ref = pointer.lstrip("/").split("/") if pointer else []

        return self._walk_cfn_pointer(schema, ref[1:])

    @property
    def resolution_scope(self):
        """
        Retrieve the current resolution scope.
        """
        return self._scopes_stack[-1]

    def _walk_cfn_pointer(
        self, document: dict[str, Any], pointer: Sequence[str]
    ) -> dict[str, Any]:
        """
        Resolve a cfn ``pointer`` within the referenced ``document``.

        Arguments:

            document:

                The referent document

            pointer (str):

                a CFN pointer to resolve within it
        """

        # depth first takes precedence
        if isinstance(document, dict) and "$ref" in document:
            _, document = self.resolve(document.get("$ref"))
            return self._walk_cfn_pointer(document, pointer)

        if not pointer:
            return document

        point = pointer[0]

        try:
            if point == "*":
                if "items" in document:
                    return self._walk_cfn_pointer(document["items"], pointer[1:])
            return self._walk_cfn_pointer(document["properties"][point], pointer[1:])
        except (TypeError, LookupError, KeyError, RefResolutionError) as e:
            for c in ["anyOf", "allOf", "oneOf"]:
                if c in document:
                    for i in document[c]:
                        try:
                            return self._walk_cfn_pointer(i, pointer)
                        except RefResolutionError:
                            continue

            if e.__class__.__name__ == "RefResolutionError":
                raise e

            raise RefResolutionError(f"Unresolvable CFN pointer: {point!r}") from e

    def resolve_fragment(self, document, fragment):
        """
        Resolve a ``fragment`` within the referenced ``document``.

        Arguments:

            document:

                The referent document

            fragment (str):

                a URI fragment to resolve within it
        """
        fragment = fragment.lstrip("/")

        if not fragment:
            return document

        def find(key):
            yield from _search_schema(document, _match_keyword(key))

        for keyword in ["id", "$id"]:
            for subschema in find(keyword):
                if "#" + fragment == subschema[keyword]:
                    return subschema

        # Resolve via path
        parts = unquote(fragment).split("/") if fragment else []
        for part in parts:
            part = part.replace("~1", "/").replace("~0", "~")

            if isinstance(document, Sequence):
                # Array indexes should be turned into integers
                try:
                    part = int(part)
                except ValueError:
                    pass
            try:
                document = document[part]
            except (TypeError, LookupError) as e:
                raise RefResolutionError(
                    f"Unresolvable JSON pointer: {fragment!r}"
                ) from e

        return document

    def _get_subschemas_cache(self):
        cache = {key: [] for key in _SUBSCHEMAS_KEYWORDS}
        for keyword, subschema in _search_schema(
            self.referrer,
            _match_subschema_keywords,
        ):
            cache[keyword].append(subschema)
        return cache

    def _find_in_subschemas(self, url):
        uri, fragment = urldefrag(url)
        subschemas = self._get_subschemas_cache()["$id"]
        if not subschemas:
            return None

        for subschema in subschemas:
            target_uri = self._urljoin_cache(
                self.resolution_scope,
                subschema["$id"],
            )
            if target_uri.rstrip("/") == uri.rstrip("/"):
                if fragment:
                    subschema = self.resolve_fragment(subschema, fragment)
                return url, subschema
        return None
