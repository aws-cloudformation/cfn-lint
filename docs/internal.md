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

```
pip3 install -e .
scripts/update_specs_from_pricing.py # requires Boto3 and Credentials
scripts/update_specs_services_from_ssm.py # requires Boto3 and Credentials
cfn-lint --update-specs
cfn-lint --update-iam-policies
cfn-lint --update-documentation
```

### Folder structure

The official resource specifications are one source of data, the other two are the "extended specs" which are "patches" to the spec that enforce more constraints, and the "additional specs" which are rules written in JSON format that are then picked up by their respective Python class.

#### CloudSpecs

The command `cfn-lint --update-specs` pulls down the official resource specifications into folder `CloudSpecs` and patches the JSON files with the contents of the files in `ExtendedSpecs`. The merged results are stored in `CloudSpecs`.

#### ExtendedSpecs

- [`ExtendedSpecs/$REGION/05_pricing_property_values.json`](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/src/cfnlint/data/ExtendedSpecs/all/05_pricing_property_values.json) written by [`scripts/update_specs_from_pricing.py`](https://github.com/aws-cloudformation/cfn-python-lint/blob/cc6ac28ff7deba86cb82813733cceec4bdff68a2/scripts/update_specs_from_pricing.py#L235)
- [`ExtendedSpecs/$REGION/06_ssm_service_removal.json`](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/src/cfnlint/data/ExtendedSpecs/us-gov-east-1/06_ssm_service_removal.json) written by [`scripts/update_specs_services_from_ssm.py`](https://github.com/aws-cloudformation/cfn-python-lint/blob/cc6ac28ff7deba86cb82813733cceec4bdff68a2/scripts/update_specs_services_from_ssm.py#L165)
- [`ExtendedSpecs/$REGION/07_ssm_service_addition.json`](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/src/cfnlint/data/ExtendedSpecs/us-gov-east-1/07_ssm_service_addition.json) written by [`scripts/update_specs_services_from_ssm.py`](https://github.com/aws-cloudformation/cfn-python-lint/blob/cc6ac28ff7deba86cb82813733cceec4bdff68a2/scripts/update_specs_services_from_ssm.py#L204)
- Allowed patterns:
https://github.com/aws-cloudformation/cfn-python-lint/blob/a46773c752247c51effef415bd3462eaec10ab0b/src/cfnlint/data/ExtendedSpecs/all/03_value_types.json#L33-L36
- Allowed values:
https://github.com/aws-cloudformation/cfn-python-lint/blob/6cce9222c89056f1546f6fee068ce6dc9dfa394e/src/cfnlint/data/ExtendedSpecs/all/03_value_types/aws_codebuild.json#L2-L11
- List size constraints:
https://github.com/aws-cloudformation/cfn-python-lint/blob/6cce9222c89056f1546f6fee068ce6dc9dfa394e/src/cfnlint/data/ExtendedSpecs/all/03_value_types/aws_iam.json#L71-L78
- Number size constraints:
https://github.com/aws-cloudformation/cfn-python-lint/blob/df8d065380e49e53dad9513dab41c2438e105f43/src/cfnlint/data/ExtendedSpecs/all/03_value_types/aws_sqs.json#L17-L24
- String size constraints:
https://github.com/aws-cloudformation/cfn-python-lint/blob/67fc5bb210b020e3226261f966a01726d574475d/src/cfnlint/data/ExtendedSpecs/all/03_value_types/aws_logs.json#L2-L9

There should be no functional difference, but [`src/cfnlint/data/ExtendedSpecs/all/03_value_types`](https://github.com/aws-cloudformation/cfn-python-lint/tree/master/src/cfnlint/data/ExtendedSpecs/all/03_value_types) and [`src/cfnlint/data/ExtendedSpecs/all/04_property_values`](https://github.com/aws-cloudformation/cfn-python-lint/tree/master/src/cfnlint/data/ExtendedSpecs/all/04_property_values) are more organized than [`src/cfnlint/data/ExtendedSpecs/all/03_value_types.json`](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/src/cfnlint/data/ExtendedSpecs/all/03_value_types.json) and [`src/cfnlint/data/ExtendedSpecs/all/04_property_values.json`](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/src/cfnlint/data/ExtendedSpecs/all/04_property_values.json), so they should be preferred locations for new constraints. 

If we push changes to these files, customers will have to update `cfn-lint`. The person changing the file(s) can also see the changes by running the following: 

```shell
pip3 install -e .
cfn-lint --update-specs # https://github.com/aws-cloudformation/cfn-python-lint/pull/1383#issuecomment-629891506
```

#### AdditionalSpecs

If we push changes to these files, customers will have to update their version of `cfn-lint`.

- [`AdditionalSpecs/RdsProperties.json`](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/src/cfnlint/data/AdditionalSpecs/RdsProperties.json) is written by [`scripts/update_specs_from_pricing.py`](https://github.com/aws-cloudformation/cfn-python-lint/blob/cc6ac28ff7deba86cb82813733cceec4bdff68a2/scripts/update_specs_from_pricing.py#L189) and used by rule [E3025](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/src/cfnlint/rules/resources/rds/InstanceSize.py)
- [`AdditionalSpecs/Policies.json`](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/src/cfnlint/data/AdditionalSpecs/Policies.json) is written by [`cfn-lint --update-iam-policies`](https://github.com/aws-cloudformation/cfn-python-lint/blob/cc6ac28ff7deba86cb82813733cceec4bdff68a2/src/cfnlint/maintenance.py#L173) and used by rule [W3037](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/src/cfnlint/rules/resources/iam/Permissions.py)
- At least one of these properties must be specified: 
https://github.com/aws-cloudformation/cfn-python-lint/blob/b788cc9bd3d49ed20d5f2e58602755a0ef37f52c/src/cfnlint/data/AdditionalSpecs/AtLeastOne.json#L20-L25, used by rule [E2522](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/src/cfnlint/rules/resources/properties/AtLeastOne.py)
- Only one of these properties may be specified:
https://github.com/aws-cloudformation/cfn-python-lint/blob/b788cc9bd3d49ed20d5f2e58602755a0ef37f52c/src/cfnlint/data/AdditionalSpecs/OnlyOne.json#L79-L84, used by rule [E2523](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/src/cfnlint/rules/resources/properties/OnlyOne.py)
- If this property (eg `SnapshotIdentifier`) is specified, these properties must be excluded:
https://github.com/aws-cloudformation/cfn-python-lint/blob/b788cc9bd3d49ed20d5f2e58602755a0ef37f52c/src/cfnlint/data/AdditionalSpecs/Exclusive.json#L102-L107, used by rule [E2520](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/src/cfnlint/rules/resources/properties/Exclusive.py)
- If this property (eg `VpcId`) is specified, these properties must be included:
https://github.com/aws-cloudformation/cfn-python-lint/blob/b788cc9bd3d49ed20d5f2e58602755a0ef37f52c/src/cfnlint/data/AdditionalSpecs/Inclusive.json#L48-L52, used by rule [E2521](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/src/cfnlint/rules/resources/properties/Inclusive.py)
