# CloudFormation Resource Specification
The core linting of `cfn-lint` is based on the [CloudFormation Resource Specification](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.html). The AWS CloudFormation resource specifications are JSON-formatted text files that defines the resources and properties that AWS CloudFormation supports.

These specification files contain information about the supported resources (per region) and information about the layout of these resources and it's properties.

## Rules based on the Specifications
There are multiple rules that are based on information from the specification files.

### Required
The Required rule ([`E3003`](/docs/rules.md#E3003)) checks if properties that are marked as required in the [property specifications](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification-format.html#cfn-resource-specification-format-propertytypes) are specified.

### ValuePrimitiveType
The ValuePrimitiveType rule ([`E3012`](/docs/rules.md#E3012)) checks if the value of a property is of the same type as specified in the [property specifications](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification-format.html#cfn-resource-specification-format-propertytypes) thus enforcing strict typing of CloudFormation templates. In short this means a number is a number, string is a string, etc.  

Although there are situations in which a warning would be sufficient (Python/YAML does implicit conversions) this could also result in errors (More information in issues [42](https://github.com/awslabs/cfn-python-lint/issues/42) and [180](https://github.com/awslabs/cfn-python-lint/issues/180)). Since the Specification contains a mapping to the underlying API's this is out of control of cfn-lint. cfn-lint doesn't have an exception process so all instances of this issue are considered errors.

### Properties
The Properties rule ([`E3002`](/docs/rules.md#E3002)) checks if the basic property configuration of resources is correct. It checks the properties from the [Resource Specification](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification-format.html#cfn-resource-specification-format-resourcetype) and [property specifications](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification-format.html#cfn-resource-specification-format-propertytypes) to check if the specified properties are valid and performs basic checks on the Type (e.g. sub-properties and Lists).
