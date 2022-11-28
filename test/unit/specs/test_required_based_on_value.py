"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import test.fixtures.schemas
from test.testlib.testcase import BaseTestCase

from jsonschema import validate

import cfnlint.helpers

LOGGER = logging.getLogger("cfnlint.maintenance")
LOGGER.addHandler(logging.NullHandler())


class TestRequiredBasedOnValueSpec(BaseTestCase):
    def test_validate_additional_specs_schema(self):
        spec = cfnlint.helpers.load_resource(
            cfnlint.data.AdditionalSpecs, "BasedOnValue.json"
        )
        schema = cfnlint.helpers.load_resource(
            test.fixtures.schemas, "BasedOnValue.json"
        )
        validate(instance=spec, schema=schema)
