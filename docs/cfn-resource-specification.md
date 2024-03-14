# CloudFormation Resource Specification
The core linting of `cfn-lint` is based on the [CloudFormation Resource Specification](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.html). The AWS CloudFormation resource specifications are JSON-formatted text files that defines the resources and properties that AWS CloudFormation supports.

These specification files contain information about the supported resources (per region) and information about the layout of these resources and it's properties.

## Rules based on the Specifications
There are multiple rules that are based on information from the specification files.

### Required
The Required rule ([`E3003`](/docs/rules.md#E3003)) checks if properties that are marked as required in the [property specifications](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification-format.html#cfn-resource-specification-format-propertytypes) are specified.

### ValuePrimitiveType
The ValuePrimitiveType rule ([`E3012`](/docs/rules.md#E3012)) checks if the value of a property is of the same type as specified in the [property specifications](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification-format.html#cfn-resource-specification-format-propertytypes) thus enforcing strict typing of CloudFormation templates. In short this means a number is a number, string is a string, etc. By default, strict typing is **NOT** enforced.

Although there are situations in which a warning would be sufficient (Python/YAML does implicit conversions) this could also result in errors (More information in issues [42](https://github.com/aws-cloudformation/cfn-python-lint/issues/42) and [180](https://github.com/aws-cloudformation/cfn-python-lint/issues/180)). Since the Specification contains a mapping to the underlying API's this is out of control of cfn-lint. cfn-lint doesn't have an exception process so all instances of this issue are considered errors.

### Properties
The Properties rule ([`E3002`](/docs/rules.md#E3002)) checks if the basic property configuration of resources is correct. It checks the properties from the [Resource Specification](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification-format.html#cfn-resource-specification-format-resourcetype) and [property specifications](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification-format.html#cfn-resource-specification-format-propertytypes) to check if the specified properties are valid and performs basic checks on the Type (e.g. sub-properties and Lists).

### AllowedValue
There are properties that need to specified with a specific enumerator, like the [Lambda Runtime](https://docs.aws.amazon.com/lambda/latest/dg/API_CreateFunction.html#SSS-CreateFunction-request-Runtime). This information is not part of the default Specification.
The linter extends the specification with these allowed values. The AllowedValue rule ([E3030](/docs/rules.md#E3030)) checks if specified values contain allowed values.

### AllowedPattern
There are properties that are restricted with a pattern ([Regular Expression](https://en.wikipedia.org/wiki/Regular_expression)), like the [Cognito Userpool EmailVerificationMessage](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_CreateUserPool.html#CognitoUserPools-CreateUserPool-request-EmailVerificationMessage). This information is not part of the default specification.
The Linter extends the specification with these patterns in a generic rule. The AllowedPattern rule ([E3031](/docs/rules.md#E3031)) checks if specific values adhere to the specified regex.
*Since regular expression can be complex to read, the rules also supports the specification of a "human readable" value that is used in the error message*
