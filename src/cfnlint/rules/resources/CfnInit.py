"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.data.schemas.other import cfn_init
from cfnlint.helpers import FUNCTIONS, load_resource
from cfnlint.rules import CloudFormationLintRule


class CfnInit(CloudFormationLintRule):
    """Check CloudFormation Init items"""

    id = "E3009"
    shortdesc = "Check CloudFormation init configuration"
    description = "Validate that the items in a CloudFormation init adhere to standards"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-init.html#aws-resource-cloudformation-init-syntax"
    tags = ["resources", "cloudformation init"]

    def __init__(self) -> None:
        super().__init__()
        self.cfn_init_commands = load_resource(cfn_init, "commands.json")
        self.cfn_init_files = load_resource(cfn_init, "files.json")
        self.cfn_init_groups = load_resource(cfn_init, "groups.json")
        self.cfn_init_packages = load_resource(cfn_init, "packages.json")
        self.cfn_init_services = load_resource(cfn_init, "services.json")
        self.cfn_init_sources = load_resource(cfn_init, "sources.json")
        self.cfn_init_users = load_resource(cfn_init, "users.json")

    def _validate(self, validator, mL, instance, schema):
        validator = validator.evolve(
            context=validator.context.evolve(functions=FUNCTIONS),
        )

        yield from validator.descend(
            instance,
            schema=schema,
        )

    # pylint: disable=unused-argument, arguments-renamed
    def cfninitcommands(self, validator, mL, instance, schema):
        yield from self._validate(validator, mL, instance, self.cfn_init_commands)

    # pylint: disable=unused-argument, arguments-renamed
    def cfninitfiles(self, validator, mL, instance, schema):
        yield from self._validate(validator, mL, instance, self.cfn_init_files)

    # pylint: disable=unused-argument, arguments-renamed
    def cfninitgroups(self, validator, mL, instance, schema):
        yield from self._validate(validator, mL, instance, self.cfn_init_groups)

    # pylint: disable=unused-argument, arguments-renamed
    def cfninitpackages(self, validator, mL, instance, schema):
        yield from self._validate(validator, mL, instance, self.cfn_init_packages)

    # pylint: disable=unused-argument, arguments-renamed
    def cfninitservices(self, validator, mL, instance, schema):
        yield from self._validate(validator, mL, instance, self.cfn_init_services)

    # pylint: disable=unused-argument, arguments-renamed
    def cfninitsources(self, validator, mL, instance, schema):
        yield from self._validate(validator, mL, instance, self.cfn_init_sources)

    # pylint: disable=unused-argument, arguments-renamed
    def cfninitusers(self, validator, mL, instance, schema):
        yield from self._validate(validator, mL, instance, self.cfn_init_users)
