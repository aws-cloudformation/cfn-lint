# CloudFormation Resource Schemas

The core linting of `cfn-lint` is based on the [CloudFormation resource provider schemas](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resource-type-schemas.html). The AWS CloudFormation resource provider schemas are JSON documents that describe the shape of a resource, what actions are supported, and permissions for that resource to function. [More info](https://docs.aws.amazon.com/cloudformation-cli/latest/userguide/resource-type-schema.html)

Resource provider schemas are based on [JSON Schema](https://json-schema.org) and include modifications for the service to work with CloudFormation.

## Rules based on the Specifications

There are multiple rules that are based on information from the specification files. Every keyword in the [draft-07](https://json-schema.org/draft-07/json-schema-release-notes) are accounted for by cfn-lint. In a lot of scenarios we will remap those validators to cfn-lint rule IDs so the rules can be suppressed as needed.

## Changes to JSON schema validation

To improve the experience of validation we have made modifications to standard JSON schema so that it works better with CloudFormation.

### Type checking

CloudFormation allows types to work interchangeably as long as a conversion can be done (Example: "10" and 10 are equivalent). As a result we have modified type checking to validate the values are of the right type.

## Grouping functions

CloudFormation allows for a value of a property to be `{"Ref": "AWS:NoValue"}` which is equivalent to that property not being specified. JSON schema validators that work on a set of properties (object or array) are validated after the properties have been cleaned of these no values. This will allow validators like required and dependencies to work as intended.

### Intrinsic functions

When resource provider schemas are created they do not account for CloudFormation [intrinsic functions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference.html). cfn-lint will account for these intrinsic functions by validating the structure of the function. Additionally, if possible, the value will be resolved (Example: `{"Ref": "AWS::Region"}` will resolve to "us-east-1") and that value will be validated against the schema.

## Extending JSON schema validation

### Extending the schemas with AWS types

Certain resource properties represent a type that is common across many resource types (example: availaibility zones, AMIs, VPCs, IAM identity policies, etc.). To provide common validation of these types we have extended the resource provider schemas with a type of `awsType` the value for the keyword is the type name. For a list of supported types go here.

### Extending the schemas with more JSON schemas

Resource types may have complex rules to define what a valid resource configuration is (example: for RDS the properties you need to specify can change based on the engine and if you are restoring from a snapshot). cfn-lint extends the resource provider schema with the keyworkd `cfnLint` which will validate the appropriate level against additional schema documents. This mechanism allows cfn-lint rule writers to create a new rule ID for these additional schemas which then allow users of cfn-lint to disable these validations as needed.

### Extending the schemas with new keywords

To make schema writing easier across hundereds of resources we have extend the schemas to include some additional keywords. While these keywords can be covered under the JSON schema they have to be done with a combination of `if`s, `onlyOne`s, `anyOf`s, etc. By using these keywords we can extend the schema for common scenarios when writing CloudFormation schemas.

#### pattern

_pattern_ keyword is used to validate a string against a regular expression. [JSON Schema docs](https://json-schema.org/understanding-json-schema/reference/string#regexp)

#### enum

_enum_ is used to restrict a value to a fixed set of values. [JSON Schema docs](https://json-schema.org/understanding-json-schema/reference/string#enum)

#### number range

_minimum_ and _maximum_ is used to define the inclusive range for a number or integer.
_exclusiveMinimum_ and _exclusiveMaximum_ is used to define the exlusive range for a number or integer.

#### array length

_minItems_ and _maxItems_ is used to provide the inclusive length of an array.

#### properties

_properties_ provides the key names and a value that represents the schema to validate the property for an object. [JSON Schema Docs](https://json-schema.org/understanding-json-schema/reference/object#properties)

#### required

_required_ defines a list of required properties. [JSON Schema docs](https://json-schema.org/understanding-json-schema/reference/object#required)

#### requiredXor

_requiredXor_ is used to define when only one property from a set properties is required.

On the following defined object

```json
{
  "properties": {
    "a": true,
    "b": true,
    "c": true
  },
  "additionalProperties": false
}
```

The cfn-lint schema

```json
{
  "requiredXor": ["a", "b", "c"]
}
```

is equivalent to the JSON schema

```json
{
  "oneOf": [
    {
      "required": ["a"]
    },
    {
      "required": ["b"]
    },
    {
      "required": ["c"]
    }
  ]
}
```

#### propertiesNand

_propertiesNand_ is used to define when none or only one property from a set properties can be defined.

On the following defined object

```json
{
  "properties": {
    "a": true,
    "b": true,
    "c": true
  },
  "additionalProperties": false
}
```

The cfn-lint schema

```json
{
  "propertiesNand": ["a", "b", "c"]
}
```

is equivalent to the JSON schema

```json
{
  "oneOf": [
    {
      "required": ["a"]
    },
    {
      "required": ["b"]
    },
    {
      "required": ["c"]
    },
    {
      "properties": {
        "a": false,
        "b": false,
        "c": false
      }
    }
  ]
}
```

#### dependentRequired

_dependentRequired_ has been backported into cfn-lint. You can read the definition [here](https://json-schema.org/understanding-json-schema/reference/conditionals#dependentRequired)

#### dependentExcluded

_dependentExcluded_ is the opposite of dependentRequired. The list of properties should not be specified when the key property is specified.

On the following defined object

```json
{
  "properties": {
    "a": true,
    "b": true,
    "c": true
  },
  "additionalProperties": false
}
```

The cfn-lint schema

```json
{
  "dependentExcluded": {
    "a": ["b", "c"]
  }
}
```

is equivalent to the JSON schema

```json
{
  "dependencies": {
    "a": {
      "properties": {
        "b": false,
        "c": false
      }
    }
  }
}
```

#### prefixItems

_prefixItems_ is similar to the definition of [prefixItems](https://json-schema.org/understanding-json-schema/reference/array#tupleValidation) but doesn't actually do the prefix. The current resource schema doesn't support [items](https://json-schema.org/understanding-json-schema/reference/array#items) being an array. We use `prefixItems` to validate array items where ordering matters.

#### type

_type_ specifies the data type for a schema. [JSON Schema docs](https://json-schema.org/understanding-json-schema/reference/type)
