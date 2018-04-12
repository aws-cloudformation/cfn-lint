# CloudFormation Linter

Python code to create a binary that can be used to lint check CloudFormation templates.  

### Warning
This is an attempt to provide validation for CloudFormation templates properties and
their values.  For values things can get pretty complicated (mappings, joins, splits,
conditions, and nesting those functions inside each other) so its a best effort to
validate those values but the promise is to not fail if we can't understand or translate
all the things that could be going on.

## Install
From a command prompt run `python setup.py clean --all` then `python setup.py install`

## Parameters
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

## Examples
### Basic usage
```cfn-lint --template template.yaml```

### Test a template based on multiple regions
```cfn-lint --regions us-east-1 ap-south-1 --template template.yaml```

> E3001 Invalid Type AWS::Batch::ComputeEnvironment for resource testBatch in ap-south-1


## Credit
Will Thames and ansible-lint at https://github.com/willthames/ansible-lint
