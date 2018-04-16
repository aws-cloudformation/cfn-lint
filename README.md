# CloudFormation Linter

Validate CloudFormation yaml/json templates against the CloudFormation spec and additional
checks.  Includes checking valid values for resource properties and best practices.

### Warning
This is an attempt to provide validation for CloudFormation templates properties and
their values.  For values things can get pretty complicated (mappings, joins, splits,
conditions, and nesting those functions inside each other) so its a best effort to
validate those values but the promise is to not fail if we can't understand or translate
all the things that could be going on.

## Install
From a command prompt run `python setup.py clean --all` then `python setup.py install`

### Pip Install
Working on the pip package currently.

## Uninstall
If you have pip installed you can uninstall using `pip uninstall cfn-lint`.  You
may need to manually remove the cfn-lint binary.

## Configuration
### Parameters

| Command Line  | Metadata | Options | Description |
| ------------- | ------------- |
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


## Credit
Will Thames and ansible-lint at https://github.com/willthames/ansible-lint
