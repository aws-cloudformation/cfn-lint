crate::extension_schema_rule!(
    E3712,
    id: "E3712",
    description: "TargetTrackingScaling policy requires ASG MaxSize greater than MinSize",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::AutoScaling::ScalingPolicy",
    schema_path: "../../../../data/schemas/extensions/aws_autoscaling_scalingpolicy/policy_target_tracking_asg.json",
    regional: false
);
