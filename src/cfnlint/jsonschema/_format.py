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

import datetime
import ipaddress
import typing
from dataclasses import dataclass, field

import regex as re

from cfnlint.jsonschema.exceptions import FormatError

_FormatCheckCallable = typing.Callable[[object], bool]
_RaisesType = typing.Union[
    typing.Type[Exception],
    typing.Tuple[typing.Type[Exception], ...],
]

_RE_DATE_FULLYEAR = "\\d{4}"
_RE_DATE_MONTH = "(0[1-9]|1[0-2])"
_RE_DATE_MDAY = "\\d{2}"
_RE_TIME_HOUR = "([01]\\d|2[0123])"
_RE_TIME_MINUTE = "[0-5]\\d"
_RE_TIME_SECOND = "[0-5]\\d"
_RE_TIME_SECRFAC = "(\\.\\d+)?"
_RE_TIME_NUMOFFSET = f"[+-]{_RE_TIME_HOUR}:{_RE_TIME_MINUTE}"
_RE_TIME_OFFSET = f"(Z|[+-]{_RE_TIME_NUMOFFSET})"
_RE_PARTIAL_TIME = (
    f"{_RE_TIME_HOUR}:{_RE_TIME_MINUTE}:{_RE_TIME_SECOND}{_RE_TIME_SECRFAC}"
)
_RE_FULL_DATE = f"{_RE_DATE_FULLYEAR}-{_RE_DATE_MONTH}-{_RE_DATE_MDAY}"
_RE_FULL_TIME = f"{_RE_PARTIAL_TIME}{_RE_TIME_OFFSET}"

_RE_DATE = re.compile(
    rf"^{_RE_FULL_DATE}$",
    re.ASCII,
)
_RE_DATE_TIME = re.compile(
    rf"^{_RE_FULL_DATE}T{_RE_FULL_TIME}$",
    re.ASCII,
)


@dataclass
class FormatChecker:
    """
    A ``format`` property checker.

    JSON Schema does not mandate that the ``format`` property actually do any
    validation. If validation is desired however, instances of this class can
    be hooked into validators to enable format validation.

    `FormatChecker` objects always return ``True`` when asked about
    formats that they do not know how to validate.

    To add a check for a custom format use the `FormatChecker.checks`
    decorator.

    Arguments:

        formats:

            The known formats to validate. This argument can be used to
            limit which formats will be used during validation.
    """

    checkers: dict[
        str,
        tuple[_FormatCheckCallable, _RaisesType],
    ] = field(default_factory=dict)

    def __repr__(self):
        return f"<FormatChecker checkers={sorted(self.checkers)}>"

    def check(self, instance: object, format: str) -> None:
        """
        Check whether the instance conforms to the given format.

        Arguments:

            instance (*any primitive type*, i.e. str, number, bool):

                The instance to check

            format:

                The format that instance should conform to

        Raises:

            FormatError:

                if the instance does not conform to ``format``
        """
        if format not in self.checkers:
            return

        func, raises = self.checkers[format]
        result, cause = None, None
        try:
            result = func(instance)
        except raises as e:
            cause = e
        if not result:
            raise FormatError(f"{instance!r} is not a {format!r}", cause=cause)


def is_email(instance: object) -> bool:
    if not isinstance(instance, str):
        return True
    return "@" in instance


def is_ipv4(instance: object) -> bool:
    if not isinstance(instance, str):
        return True
    try:
        return bool(ipaddress.IPv4Address(instance))
    except ipaddress.AddressValueError:
        return False


def is_ipv4_network(instance: object) -> bool:
    if not isinstance(instance, str):
        return True
    try:
        return bool(ipaddress.IPv4Network(instance))
    except (ipaddress.AddressValueError, ValueError):
        return False


def is_ipv6(instance: object) -> bool:
    if not isinstance(instance, str):
        return True
    try:
        address = ipaddress.IPv6Address(instance)
        return not getattr(address, "scope_id", "")
    except ipaddress.AddressValueError:
        return False


def is_ipv6_network(instance: object) -> bool:
    if not isinstance(instance, str):
        return True
    try:
        return bool(ipaddress.IPv6Network(instance))
    except (ipaddress.AddressValueError, ValueError):
        return False


def is_datetime(instance: object) -> bool:
    if not isinstance(instance, str):
        return True
    return bool(_RE_DATE_TIME.fullmatch(instance))


def is_time(instance: object) -> bool:
    if not isinstance(instance, str):
        return True
    return bool(_RE_DATE_TIME.fullmatch(f"1970-01-01T{instance}"))


def is_regex(instance: object) -> bool:
    if not isinstance(instance, str):
        return True
    return bool(re.compile(instance))


def is_date(instance: object) -> bool:
    if not isinstance(instance, str):
        return True
    return bool(_RE_DATE.fullmatch(instance) and datetime.date.fromisoformat(instance))


cfn_format_checker = FormatChecker(
    {
        "date": (is_date, ()),
        "date-time": (is_datetime, ()),
        "email": (is_email, ()),
        "ipv4": (is_ipv4, ipaddress.AddressValueError),
        "ipv4-network": (is_ipv4_network, ipaddress.AddressValueError),
        "ipv6": (is_ipv6, ipaddress.AddressValueError),
        "ipv6-network": (is_ipv6_network, ipaddress.AddressValueError),
        "regex": (is_regex, re.error),
        "time": (is_time, ()),
    }
)
