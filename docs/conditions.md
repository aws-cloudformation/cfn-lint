# Conditions

Conditions can be applied and used many laters of a template. cfn-lint does not use parameter values to determine the validaty of a template as we balance all the possible scenarios and deployment regions to validate the template.

# Using conditions

## Defining conditions


## Using conditions

Conditions can be used in two locations. 1/ Is the at the resource our output level defined by the property `Condition` 2/ Is using the function `Fn::If` under a resources `Properties`. `Fn::If` can be used at any layer as long as it is the only key in an object.



# Handling conditions

## 