"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.decode.mark import Mark
from cfnlint.decode.node import dict_node, list_node, str_node


def convert_dict(template, start_mark=Mark(0, 0), end_mark=Mark(0, 0)):
    """Convert dict to template"""
    if isinstance(template, dict):
        if not isinstance(template, dict_node):
            template = dict_node(template, start_mark, end_mark)
        for k, v in template.copy().items():
            k_start_mark = start_mark
            k_end_mark = end_mark
            if isinstance(k, str_node):
                k_start_mark = k.start_mark
                k_end_mark = k.end_mark
            new_k = str_node(k, k_start_mark, k_end_mark)
            del template[k]
            template[new_k] = convert_dict(v, k_start_mark, k_end_mark)
    elif isinstance(template, list):
        if not isinstance(template, list_node):
            template = list_node(template, start_mark, end_mark)
        for i, v in enumerate(template):
            template[i] = convert_dict(v, start_mark, end_mark)

    return template
