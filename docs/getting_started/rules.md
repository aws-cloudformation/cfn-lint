# Creating Rules
This getting started guide describes how create a new rule to be used by `cfn-lint`.

## Introduction to rules
A rule is a standalone Python class (inherited from the base rule: `CloudFormationLintRule`) that checks the given CloudFormation template for invalid JSON/YAML syntaxes, deployment errors, best practices, unused resources and other (possible) issues in the template.

An overview of all the rules that are currently supported can be found [**here**](./rules.md).

Besides the rules from `cfn-lint` itself, it can also process external rules (by using the `-a/--append-rules` argument), making it possible to integrate custom rulesets.

### Rules of the rules
When creating a rule for `cfn-lint`, keep the following rules in mind:

* A rule has to be applicable to *ALL* users of the toolkit by default. If a rule contains specific business logic, create a custom rule.
* A rule typically covers a single specific use case. It's not an exact science, but create multiple rules if you think it's needed.
* A rule is an `Error` (blocking) or `Warning` (not blocking). Create multiple specific rules if a rule can be both.
* A rule should focus on it's own requirements. Missing a required property? That's handled by an [existing rule](./rules.md#E3003) already.

These rules don't apply to custom rules sets, you're free to build your own rules in the way they suit you best.

### Rule Matches
A rule returns it findings by returning a list of `RuleMatch` object. A `RuleMatch` is an object containing information about the finding:

* Path to the resource. Used for returning line/column information of the finding in the file.
* The message about the finding. This is a specific error message that can be formatted to contain detailed information about the error (It's not the Rule's description)

See the [code snippets](#code_snippets) section for an example on how to [add a finding](#add_a_ruleMatch) .

## Creating a new rule
The following steps describe the basics on how to create a new rule.

*As an example we use `MyNewRule` as the rule to be added.*

### Select a new Rule ID
Go to the [rules documentation](./rules.md) and find an appropriate available Rule ID, based on the correct [category](./rules.md#categories).

### Create new Rule
Based on the use case and [rule category](./rules.md#categories), create a new Python file in the correct namespace of the [rules folder](/src/cfnlint/rules). Use the name of the Rule, so the filename of `MyNewRule` is `mynewrule.py`.

Use the following skeleton code as a starting point of your new rule:

```python
"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class MyNewRule(CloudFormationLintRule):
    """Rule description """
    id = '' # New Rule ID
    shortdesc = '' # A short description about the rule
    description = '' # (Longer) description about the rule
    source_url = '' # A url to the source of the rule, e.g. documentation, AWS Blog posts etc
    tags = [] # A set of tags (strings) for searching

    def match(self, cfn):
        """Basic Rule Matching"""

        matches = []

        # Your Rule code goes here

        return matches
```
Fill in the Meta data (`id`, `shortdesc`, `description`, `source_url`, `tags`) of your new rule, these are required attributes needed for processing the rule.

Since `cfn-lint` loads all rules from the `rules` folder as a plugin, the file and Class name must be the same.

*At this point your new rule is already part of the linter's ruleset!*

See the [code snippets](#code_snippets) section below for some examples of an implemention.

### Test your new Rule
You can test your new rule by just running `cfn-lint`, but preferably your new Rule is validated by unit tests. In this way the working is guaranteed for the future, and different use-cases can be validated automatically.

#### Fixtures
Fixture templates are created under the [test/templates/good](/test/templates/good) (for templates with valid CloudFormation code) or [test/templates/bad](/test/templates/bad) (for template with invalid CloudFormation code) folders.  
Use `YAML` for the CloudFormation templates for readability and the ability to add comments in the template

#### Test class
Create a `test_mynewrule.py` at the appropriate location in the [`test/rules/`](/test/rules) folder.

Use the following skeleton code as a starting point of your new rule:

```python
"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from cfnlint.rules.MyNewRule import MyNewRule  # pylint: disable=E0401
from .. import BaseRuleTestCase


class TestMyNewRule(BaseRuleTestCase):
    """Test template parameter configurations"""
    def setUp(self):
        """Setup"""
        super(TestMyNewRule, self).setUp()
        self.collection.register(MyNewRule())

    def atest_file_positive(self):
        """Test Positive"""
        self.helper_file_positive() # By default, a set of "correct" templates are checked

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('fixtures/templates/bad/mynewrule.yaml', 1) # Amount of expected matches
```

As you can see `test_file_negative()` in this unit test makes specific use of a CloudFormation template from the Fixtures folder. It's important to provide examples of templates which pass your new rule, and also templates which generate the expected warning/error.

#### Running the Tests
The unit tests (and `pylint` for linting the Python code) are processed by [`Tox`](https://tox.readthedocs.io/en/latest/).

Make sure Tox is installed and then run Tox by just calling it:

```bash
# Install Tox
$ pip install tox

# Run all test suites. Same command as used when validating a Pull Request
$ tox

# Run a specific test suite:
$ tox -e py36 # Run all unit tests again Python 3.6
```
Tox test suites available:
* **py27**: Unit tests (Python 2.7)
* **pylint27**: Python syntax check (Python 2.7)
* **py36**: Unit tests (Python 3.6)
* **pylint36**: Python syntax check (Python 3.6)

## Code Snippets
The skeleton code mention in the [Create new Rule](#create_new_rule) step contains no real code to keep it as simple as possible.

This section contains a few simple and straightforward snippets to get you started. For more complex solutions, take a deep-dive in the code of the [existing rules](/src/cfnlint/rules)!

### Add a RuleMatch
The following snippet is a simple example on how to return a finding for every resource in the template:

```python
# Get all resources
resources = cfn.get_resources()

matches = []
# Loop over all the found resources
for resource_name, resource in resources.items():
    # The path is used to determine the line/column number when returning the Match information.
    path = ['Resources', resource_name]
    # The error message with specific error information
    message = 'An error message about resource {0}'
    matches.append(RuleMatch(path, message.format(resource_name)))

return matches
```

### Check specific resource types
The following snippet is a simple example on checking a specific resource type:

```python
# Get all EC2 instances from the template
resources = cfn.get_resources(['AWS::EC2::Instance'])

matches = []
# Loop over all the found resources
for resource_name, resource in resources.items():
    # Check the InstanceType setting
    properties = resource.get('Properties')

    # Only check what we need. Other rules handle misconfigurations
    if properties:
        # Check the instance type specified
        if properties.get('InstanceType') == 't2.small':

          # The path is used to determine the line/column number when returning the Match information.
          path = ['Resources', resource_name, 'Properties', 'InstanceType']
          message = 'Please do not use t2.small'
          matches.append(RuleMatch(path, message.format(resource_name)))

return matches
```

### Check property values
The following snippet is a simple example on checking specific property values:

```python
def check_value(self, value, path):
    """Check SecurityGroup descriptions"""
    matches = []

    # Check max length
    if len(value) > 255:
        message = 'GroupDescription length ({0}) exceeds the limit (255) at {1}'
        full_path = '/'.join(str(x) for x in path)
        matches.append(RuleMatch(path, message.format(len(value), full_path)))

    return matches

def match(self, cfn):
    """Check SecurityGroup descriptions"""

    resources = cfn.get_resources(['AWS::EC2::SecurityGroup'])
    matches = []
    for resource_name, resource in resources.items():
        path = ['Resources', resource_name, 'Properties']

        properties = resource.get('Properties')
        if properties:
            matches.extend(
                cfn.check_value(
                    properties, 'GroupDescription', path,
                    check_value=self.check_value
                )
            )

    return matches
```
The `check_value` method in the `Template` class is a helper function to check values in a quick and simple way. It supports the handling of multiple values:

```python
def check_value(self, obj, key, path,
                check_value=None, check_ref=None,
                check_find_in_map=None, check_split=None, check_join=None,
                check_import_value=None, check_sub=None,
                **kwargs):
...
```
