"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import fnmatch
import json
import os
from unittest import TestCase

import jsonpatch

import cfnlint
import cfnlint.core
from cfnlint.helpers import format_json_string

modules = [
    "ExtendedSpecs",
    "AdditionalSpecs",
    "CfnLintCli",
    "Serverless",
]

for module in modules:
    append_dir = os.path.join(
        os.path.dirname(cfnlint.__file__),
        "data",
        module,
    )
    for dirpath, _, filenames in os.walk(append_dir):
        for filename in fnmatch.filter(filenames, "*.json"):
            string_content = ""
            with open(os.path.join(dirpath, filename), encoding="utf8") as input_file:
                string_content = "".join(input_file.readlines())

            pretty_content = format_json_string(json.loads(string_content))
            with open(
                os.path.join(dirpath, filename), encoding="utf8", mode="w"
            ) as output_file:
                output_file.write(pretty_content)
