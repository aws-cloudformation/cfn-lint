# Internal documentation

This documentation is meant for the maintainers and contributors of this project.

## Updating cfn-lint

- Supporting a new region: https://github.com/aws-cloudformation/cfn-python-lint/pull/1496
- Supporting a new availability zone: https://github.com/aws-cloudformation/cfn-python-lint/pull/1447
- Supporting a new Lambda runtime: https://github.com/aws-cloudformation/cfn-python-lint/pull/1469
- Supporting new EC2 instance types: https://github.com/aws-cloudformation/cfn-python-lint/pull/1535
- Supporting new Python versions: https://github.com/aws-cloudformation/cfn-python-lint/pull/1334
- Updating the SAM translator dependency: https://github.com/aws-cloudformation/cfn-python-lint/pull/1536
- Releasing a new version of cfn-lint: https://github.com/aws-cloudformation/cfn-python-lint/pull/1530
- Releasing a new version of the companion VS Code plugin: https://github.com/aws-cloudformation/aws-cfn-lint-visual-studio-code/pull/76

## Property data

The precision of the linter depends on having up-to-date resource specifications that model the properties accurately. The rules use this property data for all the validations.

### Updating it

The official resource specification is updated on a weekly basis (every Friday), so every week we update the property data by:

```shell
pip3 install -e .
scripts/update_specs_from_pricing.py # requires Boto3 and Credentials
scripts/update_specs_services_from_ssm.py # requires Boto3 and Credentials
cfn-lint --update-specs
cfn-lint --update-iam-policies
cfn-lint --update-documentation
```

### Folder structure

The official resource specifications are one source of data, the other two are the "extended specs" which are "patches" to the spec that enforce more constraints, and the "additional specs" which are rules written in JSON format that are then picked up by their respective Python class.

#### Schemas

The command `cfn-lint --update-specs` pulls down the official resource specifications into folder `schemas` and patches the JSON files with the contents of the files in `patches` folder. The merged results are stored in `providers`.

##### Extensions

Extensions are used to extend the provider schemas. We use these schemas for specific tests where it can be hard to nest it in the resource provider schema. Using extensions allow us to create separate rule IDs for each extension which allows the customer to ignore the error or for us to change the rule level (example: warning)

##### Other

The other folder has any schema used for validation that isn't under a resources properties. This includes schemas for the overall template structure of a CloudFormation template, IAM policy schemas, CFN Init schemas, and more.

##### Patches

Patches contain all the patches we apply to the provider schemas when they are downloaded. There are two folders inside patches. _providers_ patch issues in the provider schema itself and _extensions_ apply additions to the provider schema to create better linting results.

##### Providers

Providers stores all the regional resource provider schemas after they are patched. Files are deduplicated so that we are storing as little as possible. If you look at the `__init__.py` file you will see what resources are cached.

#### AdditionalSpecs

If we push changes to these files, customers will have to update their version of `cfn-lint`. They support the following syntax:

[`AdditionalSpecs/RdsProperties.json`](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/src/cfnlint/data/AdditionalSpecs/RdsProperties.json) is written by [`scripts/update_specs_from_pricing.py`](https://github.com/aws-cloudformation/cfn-python-lint/blob/cc6ac28ff7deba86cb82813733cceec4bdff68a2/scripts/update_specs_from_pricing.py#L189) and used by rule [E3025](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/src/cfnlint/rules/resources/rds/InstanceSize.py) and [`AdditionalSpecs/Policies.json`](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/src/cfnlint/data/AdditionalSpecs/Policies.json) is written by [`cfn-lint --update-iam-policies`](https://github.com/aws-cloudformation/cfn-python-lint/blob/cc6ac28ff7deba86cb82813733cceec4bdff68a2/src/cfnlint/maintenance.py#L173) and used by rule [W3037](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/src/cfnlint/rules/resources/iam/Permissions.py).
