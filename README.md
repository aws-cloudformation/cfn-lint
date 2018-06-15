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

### Editor Plugins
There are IDE plugins available to get direct linter feedback from you favorite editor:

* [Atom](https://atom.io/packages/atom-cfn-lint)
* [Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=kddejong.vscode-cfn-lint)

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
| --override-spec | | filename | Spec-style file containing custom definitions. Can be used to override CloudFormation specifications. |
| --update-specs | | | Update the CloudFormation Specs.  You may need sudo to run this.  You will need internet access when running this command || --version | | | Version of cfn-lint |

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


## Rules
This linter checks the CloudFormation by processing a collection of Rules, where every rules handles a specific function check or validation of the template.

This collection of rules can be extended with custom rules using the `--append-rules` argument.

More information describing how rules are set up and an overview of all the Rules that are applied by this linter are documented [here](docs/rules.md)


## Customize specifications
The linter follows the [CloudFormation specifications](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.html) by default. However, for your use case specific requirements might exist. For example, within your organisation it might be mandatory to use [Tagging](https://aws.amazon.com/answers/account-management/aws-tagging-strategies/).

The linter provides the possibility to implement these customized specifications using the `--override-spec` argument.

More information about how this feature works is documented [here](docs/customize_specifications.md)

## Credit
Will Thames and ansible-lint at https://github.com/willthames/ansible-lint
