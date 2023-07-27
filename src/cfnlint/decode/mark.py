"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""


class Mark:
    """Mark of line and column"""

    line = 1
    column = 1

    def __init__(self, line, column):
        self.line = line
        self.column = column
