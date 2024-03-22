"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import sys


class color:
    error = "\033[31m"
    warning = "\033[33m"
    informational = "\033[34m"
    unknown = "\033[37m"
    green = "\033[32m"
    reset = "\033[0m"
    bold_reset = "\033[1:0m"
    underline_reset = "\033[4m"


def colored(s, c):
    """Takes in string s and outputs it with color"""
    if sys.stdout.isatty():
        return f"{c}{s}{color.reset}"

    return s
