crate::extension_schema_rule!(
    E3714,
    id: "E3714",
    description: "Validate LaunchTemplate SecurityGroup and Subnet are in the same VPC",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::EC2::LaunchTemplate",
    schema_path: "../../../../data/schemas/extensions/aws_ec2_launchtemplate/launch_template_sg_subnet_vpc.json",
    regional: false
);
