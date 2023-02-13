"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import itertools
from typing import Mapping, Sequence

from cfnlint.jsonschema import ValidationError, _utils
from cfnlint.rules import CloudFormationLintRule


class ListDuplicates(CloudFormationLintRule):
    """Check if duplicates exist in a List"""

    id = "E3037"
    shortdesc = "Check if a list has duplicate values"
    description = (
        "Certain lists don't support duplicate items. "
        "Check when duplicates are provided but not supported."
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedvalue"
    tags = ["resources", "property", "list"]
    child_rules = {
        "I3037": None,
    }

    def _mapping_equal(self, one, two):
        if len(one) != len(two):
            return False
        return all(
            key in two and self._equal(value, two[key]) for key, value in one.items()
        )

    def _sequence_equal(self, one, two):
        if len(one) != len(two):
            return False
        return all(self._equal(i, j) for i, j in zip(one, two))

    def _equal(self, one, two):
        if isinstance(one, str) or isinstance(two, str):
            return one == two
        if isinstance(one, Sequence) and isinstance(two, Sequence):
            return self._sequence_equal(one, two)
        if isinstance(one, Mapping) and isinstance(two, Mapping):
            return self._mapping_equal(one, two)
        return _utils.unbool(one) == _utils.unbool(two)

    def _uniq(self, container):
        try:
            sort = sorted(_utils.unbool(i) for i in container)
            sliced = itertools.islice(sort, 1, None)

            for i, j in zip(sort, sliced):
                if self._equal(i, j):
                    return False

        except (NotImplementedError, TypeError):
            seen = []
            for e in container:
                e = _utils.unbool(e)
                for i in seen:
                    if self._equal(i, e):
                        return False

                seen.append(e)
        return True

    # pylint: disable=unused-argument
    def uniqueItems(self, validator, uI, instance, schema):
        if validator.is_type(instance, "array") and not self._uniq(instance):
            if uI:
                yield ValidationError(f"{instance!r} has non-unique elements")
            else:
                yield ValidationError(
                    f"{instance!r} has non-unique elements",
                    rule=self.child_rules["I3037"],
                )
