import logging

import cfnlint.core
import cfnlint.schemaManager
from test.testlib.testcase import BaseTestCase

from botocore.stub import Stubber
import boto3

LOGGER = logging.getLogger('cfnlint')


class TestGetRegistryVersionId(BaseTestCase):
    """Test get registry version id """

    def test_get_registry_version_id(self):
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(['us-east-1'])

        stubbed_client = boto3.client('cloudformation')
        stubber = Stubber(stubbed_client)
        stubber.add_response("list_types", {
            "TypeSummaries": [
                {
                    "TypeName": "AWS::TEST::MODULE",
                    "DefaultVersionId": "00000001"
                }
            ]
        })
        stubber.activate()

        self.assertEqual(schema_manager.get_registry_version_id(stubbed_client, 'AWS::TEST::MODULE'),
                         "00000001")

    def test_registry_version_id_registry_exception(self):
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(['us-east-1'])

        stubbed_client = boto3.client('cloudformation')
        stubber = Stubber(stubbed_client)
        stubber.add_client_error("list_types", service_error_code='CFNRegistryException')
        stubber.activate()

        err = schema_manager.get_registry_version_id(stubbed_client, 'AWS::TEST::MODULE')
        assert (err is None)

