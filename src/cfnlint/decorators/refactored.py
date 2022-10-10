"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import warnings


def refactored(message):
    """Decorator for refactoring classes"""

    def cls_wrapper(cls):
        """Wrapper Class"""

        class Wrapped(cls):
            """Wrapped Class"""

            def __init__(self, *args, **kwargs):
                warnings.warn(message, FutureWarning)
                super().__init__(*args, **kwargs)

        return Wrapped

    return cls_wrapper
