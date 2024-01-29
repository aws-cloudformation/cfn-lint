"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
import os
from test.integration import BaseCliTestCase

from jsonpatch import InvalidJsonPatch, JsonPatch


class TestPatches(BaseCliTestCase):
    """Test Patches"""

    def test_patches(self):
        """Test ignoring certain rules"""
        for root, _, files in os.walk(
            "src/cfnlint/data/ExtendedProviderSchemas", topdown=True
        ):
            for name in files:
                if name.endswith(".json"):
                    with open(os.path.join(root, name)) as fh:
                        patches = json.load(fh)
                        try:
                            JsonPatch(patches)
                        except InvalidJsonPatch:
                            raise Exception(f"Invalid patch: {name}")
