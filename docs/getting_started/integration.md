# Integration
Besides using cfn-lint through the command line, cfn-lint is built as a standalone Python module, allowing it to be integrated in your own (existing) codebase. In this way you can extend your own toolkit or CI/CD solution with cfn-lint feedback.

## Getting Started
A simplified api is exposed by `cfnlint.api` which allows you to validate string CloudFormation templates on the fly.

We can use either `lint(s, config)` which validates a string `s` against the specified `config`, or we can use `lint_all(s)` which simply validates `s` against all rules and regions:

```python
from cfnlint.api import lint, lint_all, ManualArgs

# Note ServiceName is not defined anywhere here
s = '''AWSTemplateFormatVersion: 2010-09-09
Description: An example CloudFormation template for Fargate.
Resources:
  Cluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Join ['', [!Ref ServiceName, Cluster]]'''

config = ManualArgs(regions=["us-east-1"])

print(lint(s, config=config))
# [[E1012: Check if Refs exist] (Ref ServiceName not found as a resource or parameter) matched 7]

print(lint_all(s))
# [[I1022: Use Sub instead of Join] (Prefer using Fn::Sub over Fn::Join with an empty delimiter) matched 7, [E1012: Check if Refs exist] (Ref ServiceName not found as a resource or parameter) matched 7]
```
