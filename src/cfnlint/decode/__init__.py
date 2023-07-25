"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.decode.decode import (
    create_match_file_error,
    create_match_json_parser_error,
    create_match_yaml_parser_error,
    decode,
    decode_str,
)
from cfnlint.decode.utils import convert_dict
