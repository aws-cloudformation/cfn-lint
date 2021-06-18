import logging

import cfnlint.core
import cfnlint.schemaManager
from test.testlib.testcase import BaseTestCase

import botocore.exceptions
from botocore.stub import Stubber
import boto3

LOGGER = logging.getLogger('cfnlint')


class TestAWSCallRegistry(BaseTestCase):
    """Test AWS call registry """

    def test_aws_call(self):
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(filename, template, ['us-east-1'])

        stubbed_client = boto3.client('cloudformation')
        stubber = Stubber(stubbed_client)
        stubber.add_response("describe_type", {'TypeName': 'AWS::TEST::MODULE', 'Type': 'MODULE'})
        stubber.activate()

        self.assertEqual(schema_manager.aws_call_registry(stubbed_client, 'AWS::TEST::MODULE', 'MODULE'),
                         {'TypeName': 'AWS::TEST::MODULE', 'Type': 'MODULE'})

    def test_aws_call_registry_exception(self):
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(filename, template, ['us-east-1'])

        stubbed_client = boto3.client('cloudformation')
        stubber = Stubber(stubbed_client)
        stubber.add_client_error("describe_type", service_error_code='CFNRegistryException')
        stubber.activate()

        err = schema_manager.aws_call_registry(stubbed_client, 'AWS::TEST::MODULE', 'MODULE')
        assert (err is None)


    def test_aws_call_type_not_found(self):
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(filename, template, ['us-east-1'])

        stubbed_client = boto3.client('cloudformation')
        stubber = Stubber(stubbed_client)
        stubber.add_client_error("describe_type", service_error_code='TypeNotFoundException')
        stubber.activate()

        err = schema_manager.aws_call_registry(stubbed_client, 'AWS::TEST::MODULE', 'MODULE')
        assert (err is None)
