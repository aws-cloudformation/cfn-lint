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

<<<<<<< HEAD
## Configuration
### Parameters
=======
## Parameters
>>>>>>> 94ff4c302e43ba55fdc7d383297236ca17b853ab
From a command prompt run `cfn-lint --template <path to yaml template>`
optional arguments:
* -h, --help - Show this help message and exit
* --template TEMPLATE - CloudFormation Template
* --format {quiet,parseable,json} - Output Format
* --list-rules - List all the rules
* --regions [REGIONS [REGIONS ...]] - List the regions to validate against.
* --ignore-bad-template - Ignore failures with Bad template
* --append-rules [RULESDIR [RULESDIR ...]] - Specify one or more rules directories using one or more --append-rules arguments.
* --ignore-checks [IGNORE_CHECKS [IGNORE_CHECKS ...]] - Only check rules whose id do not match these values
* --log-level {info,debug} - Log Level
* --version - Version of cfn-lint

<<<<<<< HEAD
### Metadata
Inside the root level Metadata key you can configure cfn-lint using the same parameters as above.  The configurable values are equivalent to the parameters with underscores '\_' in place of '-'.
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

=======
>>>>>>> 94ff4c302e43ba55fdc7d383297236ca17b853ab
## Examples
### Basic usage
```cfn-lint --template template.yaml```

### Test a template based on multiple regions
```cfn-lint --regions us-east-1 ap-south-1 --template template.yaml```

> E3001 Invalid Type AWS::Batch::ComputeEnvironment for resource testBatch in ap-south-1


## Credit
Will Thames and ansible-lint at https://github.com/willthames/ansible-lint
