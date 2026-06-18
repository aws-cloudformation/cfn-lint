crate::extension_schema_rule!(
    E3706,
    id: "E3706",
    description: "AutoScaling MaxSize must be >= MinSize",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::AutoScaling::AutoScalingGroup",
    schema_path: "../../../../data/schemas/extensions/aws_autoscaling_autoscalinggroup/min_max_size.json",
    regional: false
);
