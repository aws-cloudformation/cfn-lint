# The format keyword

The `format` keyword in JSON Schema is used to define a regular expression pattern that a string value should match. It provides a way to validate that a string adheres to a specific format or pattern.

In `cfn-lint`, we have extended the `format` keyword to support custom formats that are specific to AWS resources. These custom formats help validate values against specific patterns or constraints defined by AWS.

## Custom Formats

`cfn-lint` supports the following custom formats:

### AWS::EC2::VPC.Id

This format ensures that the value is a valid VPC ID, which is a string of the pattern `vpc-[0-9a-f]{8}` or `vpc-[0-9a-f]{17}`.

### AWS::EC2::SecurityGroup.GroupId

This format validates that the value is a valid Security Group ID, which is a string of the pattern `sg-[0-9a-f]{8}` or `sg-[0-9a-f]{17}`.

### AWS::EC2::SecurityGroup.GroupName

This format validates that the value is a valid Security Group Name, which must be a string of 1 to 255 characters, starting with a letter, and containing only letters, numbers, and certain special characters.

### AWS::EC2::Image.Id

This format validates that the value is a valid Amazon Machine Image (AMI), which is a string of the pattern `ami-[0-9a-f]{8}` or `ami-[0-9a-f]{17}`.  More info in [docs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/resource-ids.html)
