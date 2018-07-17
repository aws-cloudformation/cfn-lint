# CloudFormation Resource Specification
The core linting of `cfn-lint` is based on the [CloudFormation Resource Specification](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.html). The AWS CloudFormation resource specifications are JSON-formatted text files that defines the resources and properties that AWS CloudFormation supports.

These specification files contain information about the supported resources (per region) and information about the layout of these resources and it's properties.

## Rules based on the Specifications
There are multiple rules that are based on information from the specification files.

### Required
The required rule ([`E3003`](/docs/rules.md#E3003)) checks if properties that are marked as required in the [property specifications](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification-format.html#cfn-resource-specification-format-propertytypes) are specified.
