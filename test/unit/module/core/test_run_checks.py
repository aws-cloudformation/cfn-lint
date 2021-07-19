"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
import cfnlint.core
import cfnlint.helpers  # pylint: disable=E0401
from mock import patch


class TestRunChecks(BaseTestCase):
    """Test Run Checks """

    def test_good_template(self):
        """Test success run"""

        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames([
            '--template', filename])

        results = []
        for filename in filenames:
            (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
            results.extend(
                cfnlint.core.run_checks(
                    filename, template, rules, ['us-east-1']))

        assert(results == [])

    def test_bad_template(self):
        """Test bad template"""

        filename = 'test/fixtures/templates/quickstart/nat-instance.json'
        (args, filenames, _) = cfnlint.core.get_args_filenames([
            '--template', filename])
        results = []
        for filename in filenames:
            (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
            results.extend(
                cfnlint.core.run_checks(
                    filename, template, rules, ['us-east-1']))

        assert(results[0].rule.id == 'W2506')
        assert(results[1].rule.id == 'W2001')

    def test_bad_region(self):
        """Test bad region"""
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        err = None
        try:
            cfnlint.core.run_checks(filename, template, rules, ['not-a-region'])
        except cfnlint.core.InvalidRegionException as e:
            err = e
        assert(type(err) == cfnlint.core.InvalidRegionException)

    def test_bad_registry_type(self):
        """Test bad registry type"""
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        err = None
        try:
            cfnlint.core.run_checks(filename, template, rules, ['us-east-1'], None, ['not-a-registry-type'])
        except cfnlint.core.InvalidRegistryTypesException as e:
            err = e
        assert(type(err) == cfnlint.core.InvalidRegistryTypesException)

    @patch('cfnlint.schema_manager.SchemaManager.check_folders')
    def test_valid_registry_type(self, check_folders):
        """Test valid registry type"""
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        results = []
        results.extend(cfnlint.core.run_checks(filename, template, rules, ['us-east-1'], None, ['MODULE']))
        assert (results == [])
