"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""


class Unpredictable(Exception):
    """
    We cannot resolve the value for this function
    """

    def __init__(self, instance):
        self.instance = instance

    def __str__(self):
        return f"Type {self.instance!r} cannot be resolved"
