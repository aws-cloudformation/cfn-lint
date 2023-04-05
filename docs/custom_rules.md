# Custom Rules
The Custom Rules feature allows any customer to create simple rules using a pre-defined set of operators. These rules support any resource property comparisons.

# Syntax
Each rule has been designed to be easy to write, and thus the syntax is very flexible in regards to grammar. Each rule is always one line long, and follows a set structure in regards to syntax.

The template used for each custom rules have been included below. Angle brackets specify required values, while square brackets indicate optional values.

`<Resource Type> <Property[*]> <Operator> <Value> [Error Level] [Custom Error Message]`


### General Guidelines

* The ruleID is auto-generated based on the line number. The E9XXX and W9XXX blocks are allocated towards custom rules.
    * As an example, custom rule on line 4 of the rules file which has error level “ERROR” would become E9004
* Comments are supported through the use of the # symbol at the beginning of a line (e.g `#This is a comment`)
* The syntax is "quote-flexible" and will support all permutations shown below
```
AWS::EC2::Instance Property EQUALS "Cloud Formation"
AWS::EC2::Instance Property EQUALS Cloud Formation
AWS::EC2::Instance Property EQUALS Cloud Formation WARN "Custom Error"
AWS::EC2::Instance Property EQUALS Cloud Formation WARN Custom Error
```

#### Resource Type

Name of the resource type as specified within the template. (e.g `AWS::EC2::Instance`)


#### Property

Any property of a resource. Dot notation may be used to specify lower-level properties. (e.g `AssumeRolePolicyDocument.Version`)

#### Operator

The specified operator to be used for this rule. The supported values are defined below.

| Operator          | Function |
| --------------------- | ------------- |
| EQUALS | Checks the specified property is equal to the value given |
| == | Identical to `EQUALS` |
| NOT_EQUALS | Checks the specified property is not equal to the value given |
| != | Identical to `NOT_EQUALS` |
| IN | Checks the specified property is equal to or contained by the array value |
| NOT_IN | Checks the specified property is not equal to or not contained by the array value |
| \>= | Checks the specified property is greater than or equal to the value given |
| <= | Checks the specified property is less than or equal to the value given |
| IS | Checks the specified property is defined or not defined, the value must be one of DEFINED or NOT_DEFINED |

#### Value

The value which the operator is comparing against (e.g `CompareMe`).

Multi-word inputs are accepted  (e.g `Compare Me`). Array inputs are also accepted for set operations (e.g `[Apples, Oranges, Pears]`).

For operator `IS`, the value must be one of `DEFINED` or `NOT_DEFINED`.

#### Error Level (Optional)

To specify the error level any breach of this rule is categorized. The supported values include all existing error levels (e.g `ERROR` or `WARN`)

#### Custom Error Message (Optional, Pre-requisites)

Pre-Requisites: The Custom Error Message requires an error level to be specified.

A custom error message can be used to override the existing fallback messages. (e.g `Show me this custom message`)

## Example
This following example shows how a you can create a custom rule.
 
This rule validates all EC2 instances in a template aren’t using the instance type “p3.2xlarge”.

```
AWS::EC2::Instance InstanceType != "p3.2xlarge"
```

This rule specify all lambda function in a template must specify environment variable `NODE_ENV`.

```
AWS::Lambda::Function Environment.Variables.NODE_ENV IS DEFINED
```

To include this rules, include your custom rules text file using the `-z custom_rules.txt` argument when running cfn-lint.


