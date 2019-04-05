# CloudFormation Linter

<img alt="[cfn-lint logo]" src="https://github.com/aws-cloudformation/cfn-python-lint/blob/master/logo.png?raw=true" width="150" align="right">

[![Build Status](https://travis-ci.com/aws-cloudformation/cfn-python-lint.svg?branch=master)](https://travis-ci.com/aws-cloudformation/cfn-python-lint)
[![PyPI version](https://badge.fury.io/py/cfn-lint.svg)](https://badge.fury.io/py/cfn-lint)
[![codecov](https://codecov.io/gh/aws-cloudformation/cfn-python-lint/branch/master/graph/badge.svg)](https://codecov.io/gh/aws-cloudformation/cfn-python-lint)

Validate CloudFormation yaml/json templates against the CloudFormation spec and additional
checks.  Includes checking valid values for resource properties and best practices.

### Warning

This is an attempt to provide validation for CloudFormation templates properties and
their values.  For values things can get pretty complicated (mappings, joins, splits,
conditions, and nesting those functions inside each other) so its a best effort to
validate those values but the promise is to not fail if we can't understand or translate
all the things that could be going on.

#### Serverless Application Model

The Serverless Application Model (SAM) is supported by the linter. The template is
transformed using AWS SAM [https://github.com/awslabs/serverless-application-model](https://github.com/awslabs/serverless-application-model)
before the linter processes the template.

## Install

Python 2.7+ and 3.4+ are supported.

### Pip Install

`pip install cfn-lint`. If pip is not available, run
`python setup.py clean --all` then `python setup.py install`.

### Editor Plugins

There are IDE plugins available to get direct linter feedback from you favorite editor:

* [Atom](https://atom.io/packages/atom-cfn-lint)
* NeoVim 0.2.0+/Vim 8
  * [ALE](https://github.com/w0rp/ale#supported-languages)
  * [Syntastic](https://github.com/speshak/vim-cfn)
* [Sublime](https://packagecontrol.io/packages/SublimeLinter-contrib-cloudformation)
* [Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=kddejong.vscode-cfn-lint)
* [IntelliJ IDEA](https://plugins.jetbrains.com/plugin/10973-cfn-lint/update/48247)

## Basic Usage

- `cfn-lint template.yaml`
- `cfn-lint -t template.yaml`

##### Lint multiple files

Multiple files can be linted by either specifying multiple specific files:

- `cfn-lint template1.yaml template2.yaml`
- `cfn-lint -t template1.yaml template2.yaml`

Multiple files can also be specified using wildcards (globbing):

Lint all `yaml` files in `path`:

- `cfn-lint path/*.yaml`

Lint all `yaml` files in `path` and all subdirectories (recursive):

- `cfn-lint path/to/templates/**/*.yaml`

*Note*: Glob in Python 3.5 supports recursive searching `**/*.yaml`.  If you are using an earlier version of Python you will have to handle this manually (`folder1/*.yaml`, `folder2/*.yaml`, etc).

##### Specifying the template as an input stream

The template to be linted can also be passed using standard input:

- `cat path/template.yaml | cfn-lint -`

##### Specifying the template with other parameters

- `cfn-lint -r us-east-1 ap-south-1 -- template.yaml`
- `cfn-lint -r us-east-1 ap-south-1 -t template.yaml`

## Configuration

### Command Line

From a command prompt run `cfn-lint <path to yaml template>` to run standard linting of the template.

### Config File

You can define a yaml file in your project or home folder called `.cfnlintrc`.  In that file you can specify settings from the parameter section below.

Example:

```yaml
templates:
- test/fixtures/templates/good/**/*.yaml
ignore_templates:
- codebuild.yaml
include_checks:
- I
```

### Parameters

Optional parameters:

| Command Line  | Metadata | Options | Description |
| ------------- | ------------- | ------------- | ------------- |
| -h, --help  |   | | Get description of cfn-lint |
| -t, --template  |   | filename | Alternative way to specify Template file path to the file that needs to be tested by cfn-lint |
| -f, --format    | format | quiet, parseable, json | Output format |
| -l, --list-rules | | | List all the rules |
| -r, --regions | regions | [REGIONS [REGIONS ...]]  | Test the template against many regions.  [Supported regions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.html) |
| -b, --ignore-bad-template | ignore_bad_template | | Ignores bad template errors |
| --ignore-templates | IGNORE_TEMPLATES [IGNORE_TEMPLATES ...] | Ignore templates from being scanned
| -a, --append-rules | append_rules | [RULESDIR [RULESDIR ...]] | Specify one or more rules directories using one or more --append-rules arguments. |
| -i, --ignore-checks | ignore_checks | [IGNORE_CHECKS [IGNORE_CHECKS ...]] | Only check rules whose ID do not match or prefix these values.  Examples: <br />- A value of `W` will disable all warnings<br />- `W2` disables all Warnings for Parameter rules.<br />- `W2001` will disable rule `W2001` |
| -e, --include-experimental | include_experimental | | Whether rules that still in an experimental state should be included in the checks |
| -c, --include-checks | INCLUDE_CHECKS [INCLUDE_CHECKS ...] | Include rules whose id match these values
| -d, --debug |  |  | Specify to enable debug logging |
| -u, --update-specs | | | Update the CloudFormation Specs.  You may need sudo to run this.  You will need internet access when running this command |
| -o, --override-spec | | filename | Spec-style file containing custom definitions. Can be used to override CloudFormation specifications. More info [here](#customize-specifications) |
| -v, --version | | | Version of cfn-lint |

### Info Rules

To maintain backwards compatibility `info` rules are not included by default.  To include these rules you will need to include `-c I` or `--include-checks I`

### Metadata

Inside the root level Metadata key you can configure cfn-lint using the supported parameters.

```yaml
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

### Getting Started Guides

There are [getting started guides](/docs/getting_started) available in the documentation section to help with integrating `cfn-lint` or creating rules.

## Rules

This linter checks the CloudFormation by processing a collection of Rules, where every rules handles a specific function check or validation of the template.

This collection of rules can be extended with custom rules using the `--append-rules` argument.

More information describing how rules are set up and an overview of all the Rules that are applied by this linter are documented [here](docs/rules.md)

## Customize specifications

The linter follows the [CloudFormation specifications](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.html) by default. However, for your use case specific requirements might exist. For example, within your organisation it might be mandatory to use [Tagging](https://aws.amazon.com/answers/account-management/aws-tagging-strategies/).

The linter provides the possibility to implement these customized specifications using the `--override-spec` argument.

More information about how this feature works is documented [here](docs/customize_specifications.md)

## pre-commit

If you'd like cfn-lint to be run automatically when making changes to files in your Git repository, you can install [pre-commit](https://pre-commit.com/) and add the following text to your repositories' `.pre-commit-config.yaml`:

```yaml
repos:
-   repo: https://github.com/aws-cloudformation/cfn-python-lint
    rev: v0.18.1  # The version of cfn-lint to use
    hooks:
    -   id: cfn-python-lint
        files: path/to/cfn/dir/.*\.(json|yml|yaml)$
```

* If you exclude the `files:` line above, every json/yml/yaml file will be checked.
* You can see available cfn-lint versions on the [releases page](https://github.com/aws-cloudformation/cfn-python-lint/releases).

----
**PyPi:**

[![PyPI - Downloads](https://img.shields.io/pypi/dw/cfn-lint.svg)](https://pypi.org/project/cfn-lint/#history)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/cfn-lint.svg)](https://pypi.org/project/cfn-lint/#history)
