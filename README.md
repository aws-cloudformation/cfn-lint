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
| --ignore-checks | ignore_checks | [IGNORE_CHECKS [IGNORE_CHECKS ...]] | Only check rules whose id do not match these values |
| --log-level | log_level | {info, debug} | Log Level |
| --update-specs | | | Update the CloudFormation Specs.  You may need sudo to run this.  You will need internet access when running this command |
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
```cfn-lint --template template.yaml```

### Test a template based on multiple regions
```cfn-lint --regions us-east-1 ap-south-1 --template template.yaml```

> E3001 Invalid Type AWS::Batch::ComputeEnvironment for resource testBatch in ap-south-1


## Rule IDs

### Errors
Errors will start with the letter E.  Errors should result in a hard failure of the template being run.

### Warnings
Warnings start with the letter W.  Warnings alert you when the template doesn't follow best practices but should still function.  *Example: If you use a parameter for a RDS master password you should have the parameter property NoEcho set to true.*


| Rule Numbers  | Category |
| ------------- | ------------- |
| (E&#124;W)0XXX  | Basic Template Errors. Examples: Not parseable, main sections (Outputs, Resources, etc.)  |
| (E&#124;W)1XXX  | Functions (Ref, GetAtt, etc.)  |
| (E&#124;W)2XXX  | Parameters |
| (E&#124;W)3XXX  | Resources |
| (E&#124;W)4XXX  | Metadata |
| (E&#124;W)6xxx  | Outputs |
| (E&#124;W)7xxx  | Mappings |
| (E&#124;W)8xxx  | Conditions |
| (E&#124;W)9xxx  | Reserved for users rules |


## Credit
Will Thames and ansible-lint at https://github.com/willthames/ansible-lint
