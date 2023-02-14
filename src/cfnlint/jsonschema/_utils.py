"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

Originally taken from https://github.com/python-jsonschema/jsonschema/blob/main/jsonschema/_utils.py
adapted for CloudFormation usage
"""


class Unset:
    """
    An as-of-yet unset attribute or unprovided default parameter.
    """

    def __repr__(self):
        return "<unset>"


def unbool(element, true=object(), false=object()):
    if element is True:
        return true
    if element is False:
        return false
    return element
