# Integration
Besides using cfn-lint through the command line, cfn-lint is build as a standalone Python module, allowing it to be integrated in your own (existing) codebase. In this way you can extend your own toolkit or CI/CD solution with cfn-lint feedback.

## Getting Started
Following displays a basic implementation of cfn-lint to check a specific CloudFormation template:

```python
import cfnlint.core

# The path to the file to check
filename = 'test.yaml'

# Load the YAML file
template = cfnlint.decode.cfn_yaml.load(filename)

# Initialize the ruleset to be applied (no overrules, no excludes)
rules = cfnlint.core.get_rules([], [])

# Use us-east-1 region (spec file) for validation
regions = ['us-east-1']

# Process all the rules and gather the errors
matches = cfnlint.core.run_checks(
    filename,
    template,
    rules,
    regions)

# Print the output
print(matches)
```
