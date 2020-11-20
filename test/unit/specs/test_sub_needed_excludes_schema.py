"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import test.fixtures.schemas
from jsonschema import validate
from test.testlib.testcase import BaseTestCase
from cfnlint.data import AdditionalSpecs
import cfnlint.helpers


LOGGER = logging.getLogger('cfnlint.maintenance')
LOGGER.addHandler(logging.NullHandler())


class TestSubNeededExcludesSchema(BaseTestCase):


    def test_validate_additional_specs_schema(self):
        spec = cfnlint.helpers.load_resource(cfnlint.data.AdditionalSpecs, 'SubNeededExcludes.json')
        schema = cfnlint.helpers.load_resource(test.fixtures.schemas, 'SubNeededExcludes.json')
        validate(instance=spec, schema=schema)
