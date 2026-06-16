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

The precision of the linter depends on having up-to-date resource schemas that model the properties accurately. The rules use this property data for all the validations.

### Schema source

Schemas are sourced from the [resource-provider-enhanced-schemas](https://github.com/aws-cloudformation/resource-provider-enhanced-schemas) repository. That repository takes the raw CloudFormation resource provider schemas, applies patches (smithy-derived constraints, manual fixes, extensions), and publishes a release artifact (`schemas-cfn-lint.zip`).

### Updating schemas

Schemas are downloaded at runtime via:

```shell
cfn-lint --update-specs
```

This downloads the latest `schemas-cfn-lint.zip` from the enhanced-schemas release and extracts it into `src/cfnlint/data/schemas/providers/` (region JSON files) and `src/cfnlint/data/schemas/resources/` (schema JSON files by hash). These directories are gitignored.

Use `--force` to re-download even if the local copy is current:

```shell
cfn-lint --update-specs --force
```

### Folder structure

#### Schemas

##### Extensions

Extensions are used to extend the provider schemas. We use these schemas for specific tests where it can be hard to nest it in the resource provider schema. Using extensions allow us to create separate rule IDs for each extension which allows the customer to ignore the error or for us to change the rule level (example: warning).

##### Other

The other folder has any schema used for validation that isn't under a resources properties. This includes schemas for the overall template structure of a CloudFormation template, IAM policy schemas, CFN Init schemas, and more.

#### AdditionalSpecs

If we push changes to these files, customers will have to update their version of `cfn-lint`. They support the following syntax:

[`AdditionalSpecs/RdsProperties.json`](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/src/cfnlint/data/AdditionalSpecs/RdsProperties.json) is written by [`scripts/update_specs_from_pricing.py`](https://github.com/aws-cloudformation/cfn-python-lint/blob/cc6ac28ff7deba86cb82813733cceec4bdff68a2/scripts/update_specs_from_pricing.py#L189) and used by rule [E3025](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/src/cfnlint/rules/resources/rds/InstanceSize.py) and [`AdditionalSpecs/Policies.json`](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/src/cfnlint/data/AdditionalSpecs/Policies.json) is written by [`cfn-lint --update-iam-policies`](https://github.com/aws-cloudformation/cfn-python-lint/blob/cc6ac28ff7deba86cb82813733cceec4bdff68a2/src/cfnlint/maintenance.py#L173) and used by rule [W3037](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/src/cfnlint/rules/resources/iam/Permissions.py).
