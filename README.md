# CloudFormation Linter

[![Build Status](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoibm1lNzczajZWcGw3UE5JRkhhcTBVZzBWTVRMYUtBU2lNcjdPNDVMK2JFM1RERGNDRjJlY2FQMVIrdFFpamx3M3ZaSDF5UCtrRGxkV1BrYU96YTdGNUE4PSIsIml2UGFyYW1ldGVyU3BlYyI6Im1DZklveUk5dXY0dTBucEsiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)](https://github.com/awslabs/cfn-python-lint)

Validate CloudFormation yaml/json templates against the CloudFormation spec and additional
checks.  Includes checking valid values for resource properties and best practices.

### Warning
This is an attempt to provide validation for CloudFormation templates properties and
their values.  For values things can get pretty complicated (mappings, joins, splits,
conditions, and nesting those functions inside each other) so its a best effort to
validate those values but the promise is to not fail if we can't understand or translate
all the things that could be going on.

## Install
### Command line
From a command prompt run `python setup.py clean --all` then `python setup.py install`

### Pip Install
`pip install cfn-lint`.  You may need to use sudo.

## Uninstall
If you have pip installed you can uninstall using `pip uninstall cfn-lint`.  You
may need to manually remove the cfn-lint binary.

## Configuration
### Parameters

| Command Line  | Metadata | Options | Description |
| ------------- | ------------- | ------------- | ------------- |
| -h, --help  |   | | Get description of cfn-lint |
| --template  |   | filename | Template file path to the file that needs to be tested by cfn-lint |
| --format    | format | quiet, parseable, json | Output format |
| --list-rules | | | List all the rules |
| --regions | regions | [REGIONS [REGIONS ...]]  | Test the template against many regions.  [Supported regions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.html) |
| --ignore-bad-template | ignore_bad_template | | Ignores bad template errors |
| --append-rules | append_rules | [RULESDIR [RULESDIR ...]] | Specify one or more rules directories using one or more --append-rules arguments. |
| --ignore-checks | ignore_checks | [IGNORE_CHECKS [IGNORE_CHECKS ...]] | Only check rules whose ID do not match or prefix these values.  Examples: <br />- A value of `W` will disable all warnings<br />- `W2` disables all Warnings for Parameter rules.<br />- `W2001` will disable rule `W2001` |
| --log-level | log_level | {info, debug} | Log Level |
| --update-specs | | | Update the CloudFormation Specs.  You may need sudo to run this.  You will need internet access when running this command |
| --override-spec | | filename | Spec-style file containing custom definitions. Can be used to override CloudFormation specifications. More info [here](#customise-specifications) |
| --version | | | Version of cfn-lint |

### Command Line
From a command prompt run `cfn-lint --template <path to yaml template>`

### Metadata
Inside the root level Metadata key you can configure cfn-lint using the supported parameters.
```
Metadata:
  cfn-lint:
    config:
      regions:
      - us-east-1
      - us-east-2
      ignore_checks:
      - E2530
```

### Precedence
cfn-lint applies the configuration from the CloudFormation Metadata first and then overrides those values with anything specified in the CLI.

## Examples
### Basic usage
`cfn-lint --template template.yaml`

### Test a template based on multiple regions
`cfn-lint --regions us-east-1 ap-south-1 --template template.yaml`

> E3001 Invalid Type AWS::Batch::ComputeEnvironment for resource testBatch in ap-south-1


## Rule IDs

### Errors
Errors will start with the letter E.  Errors should result in a hard failure of the template being run.

### Warnings
Warnings start with the letter W.  Warnings alert you when the template doesn't follow best practices but should still function.  *Example: If you use a parameter for a RDS master password you should have the parameter property NoEcho set to true.*

### Categories

| Rule Numbers    | Category |
| --------------- | ------------- |
| (E&#124;W)0XXX  | Basic Template Errors. Examples: Not parseable, main sections (Outputs, Resources, etc.)  |
| (E&#124;W)1XXX  | Functions (Ref, GetAtt, etc.)  |
| (E&#124;W)2XXX  | Parameters |
| (E&#124;W)3XXX  | Resources |
| (E&#124;W)4XXX  | Metadata |
| (E&#124;W)6xxx  | Outputs |
| (E&#124;W)7xxx  | Mappings |
| (E&#124;W)8xxx  | Conditions |
| (E&#124;W)9xxx  | Reserved for users rules |

*Warning* <br />
Rule `E3012` is used to check the types for value of a resource property.  A number is a number, string is a string, etc.  There are occasions where this could be just a warning and other times it could be an error.  cfn-lint didn't build an exception process so all instances of this issue is considered an error.  

## Customise specifications
The linter follows the [CloudFormation specifications](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.html) by default. However, for your use case specific requirements might exist. For example, within your organisation it might be mandatory to use [Tagging](https://aws.amazon.com/answers/account-management/aws-tagging-strategies/).

The linter provides the possibility to implement these customised specifications using the `--override-spec` parameter. This parameter should pass a (JSON) file in the same format as the [Specification](/src/cfnlint/data) files, this file is then merged into the Regional specification files that are used to process all the linting rules.

This makes it easy to apply your our rules on top of the CloudFormation rules without having to write your own checks in Python and use the power of the linter itself with a single file!

### Features
The `--override-spec` functionality currently supports the following features:

#### Whitelist/Blacklist resources
If you want to block the use of specific resources, you can easily disable them by using the Whitelist/Blacklist features. This can be done by specifying a list of `IncludedResourceTypes` and/or `ExcludedResourceTypes`.

* `IncludedResourceTypes`: List of resources that are supported. If specified, all resources that are not in this list are not allowed.
* `ExcludedResourceTypes`: List of resources that are not supported. Resources in this list are not allowed.

Wildcards (`*`) are supported in these lists, so `AWS::EC2::*` allows ALL EC2 ResourceTypes. Both lists can work in conjunction with each other.

The following example only allows the usage of all `EC2` resources, except for `AWS::EC2::SpotFleet`:
```
{
  "IncludeResourceTypes": [
    "AWS::EC2::*"
  ],
  "ExcludeResourceTypes": [
    "AWS::EC2::SpotFleet"
  ]
}
```

#### Alter Resource/Parameter specifications
The spec file overwrites values from the Regional spec files which give you the possible to alter the specifications for your own needs. A good example is making optional Parameters Required.

For example, to enforce tagging on an S3 bucket, the override file looks like this:
```
{
  "ResourceTypes": {
    "AWS::S3::Bucket": {
      "Properties": {
        "Tags": {
          "Required": true
        }
      }
    }
  }
}
```
**WARNING**
The file is checked for valid JSON syntax, but does not check the contents of the file before merging it into the Specifications. Be careful with your changes because it can possibly corrupt the Specifications and break the linting process.

## Credit
Will Thames and ansible-lint at https://github.com/willthames/ansible-lint
