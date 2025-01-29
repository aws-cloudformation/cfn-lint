from __future__ import annotations

# pylint: disable=too-many-lines
types: list[str] = [
    "AWS::ACMPCA::Certificate",
    "AWS::ACMPCA::CertificateAuthority",
    "AWS::ACMPCA::CertificateAuthorityActivation",
    "AWS::ACMPCA::Permission",
    "AWS::ARCZonalShift::AutoshiftObserverNotificationStatus",
    "AWS::ARCZonalShift::ZonalAutoshiftConfiguration",
    "AWS::AccessAnalyzer::Analyzer",
    "AWS::ApiGateway::Account",
    "AWS::ApiGateway::ApiKey",
    "AWS::ApiGateway::Authorizer",
    "AWS::ApiGateway::BasePathMapping",
    "AWS::ApiGateway::ClientCertificate",
    "AWS::ApiGateway::Deployment",
    "AWS::ApiGateway::DocumentationPart",
    "AWS::ApiGateway::DocumentationVersion",
    "AWS::ApiGateway::DomainName",
    "AWS::ApiGateway::GatewayResponse",
    "AWS::ApiGateway::Method",
    "AWS::ApiGateway::Model",
    "AWS::ApiGateway::RequestValidator",
    "AWS::ApiGateway::Resource",
    "AWS::ApiGateway::RestApi",
    "AWS::ApiGateway::Stage",
    "AWS::ApiGateway::UsagePlan",
    "AWS::ApiGateway::UsagePlanKey",
    "AWS::ApiGateway::VpcLink",
    "AWS::AppConfig::Application",
    "AWS::AppConfig::ConfigurationProfile",
    "AWS::AppConfig::Deployment",
    "AWS::AppConfig::DeploymentStrategy",
    "AWS::AppConfig::Environment",
    "AWS::AppConfig::Extension",
    "AWS::AppConfig::ExtensionAssociation",
    "AWS::AppConfig::HostedConfigurationVersion",
    "AWS::ApplicationAutoScaling::ScalableTarget",
    "AWS::ApplicationAutoScaling::ScalingPolicy",
    "AWS::AutoScaling::AutoScalingGroup",
    "AWS::AutoScaling::LaunchConfiguration",
    "AWS::AutoScaling::LifecycleHook",
    "AWS::AutoScaling::ScalingPolicy",
    "AWS::AutoScaling::ScheduledAction",
    "AWS::AutoScaling::WarmPool",
    "AWS::Backup::BackupPlan",
    "AWS::Backup::BackupSelection",
    "AWS::Backup::BackupVault",
    "AWS::Batch::ComputeEnvironment",
    "AWS::Batch::JobDefinition",
    "AWS::Batch::JobQueue",
    "AWS::Batch::SchedulingPolicy",
    "AWS::CDK::Metadata",
    "AWS::CertificateManager::Certificate",
    "AWS::CloudFormation::CustomResource",
    "AWS::CloudFormation::Macro",
    "AWS::CloudFormation::ResourceDefaultVersion",
    "AWS::CloudFormation::ResourceVersion",
    "AWS::CloudFormation::Stack",
    "AWS::CloudFormation::StackSet",
    "AWS::CloudFormation::WaitCondition",
    "AWS::CloudFormation::WaitConditionHandle",
    "AWS::CloudFront::AnycastIpList",
    "AWS::CloudFront::CachePolicy",
    "AWS::CloudFront::CloudFrontOriginAccessIdentity",
    "AWS::CloudFront::ContinuousDeploymentPolicy",
    "AWS::CloudFront::Distribution",
    "AWS::CloudFront::Function",
    "AWS::CloudFront::KeyGroup",
    "AWS::CloudFront::KeyValueStore",
    "AWS::CloudFront::MonitoringSubscription",
    "AWS::CloudFront::OriginAccessControl",
    "AWS::CloudFront::OriginRequestPolicy",
    "AWS::CloudFront::PublicKey",
    "AWS::CloudFront::RealtimeLogConfig",
    "AWS::CloudFront::ResponseHeadersPolicy",
    "AWS::CloudTrail::Trail",
    "AWS::CloudWatch::Alarm",
    "AWS::CloudWatch::AnomalyDetector",
    "AWS::CloudWatch::CompositeAlarm",
    "AWS::CloudWatch::InsightRule",
    "AWS::CodeDeploy::Application",
    "AWS::CodeDeploy::DeploymentConfig",
    "AWS::CodeDeploy::DeploymentGroup",
    "AWS::CodePipeline::CustomActionType",
    "AWS::CodePipeline::Pipeline",
    "AWS::Config::ConfigRule",
    "AWS::Config::ConfigurationRecorder",
    "AWS::Config::DeliveryChannel",
    "AWS::DLM::LifecyclePolicy",
    "AWS::DataPipeline::Pipeline",
    "AWS::DataSync::Agent",
    "AWS::DataSync::LocationAzureBlob",
    "AWS::DataSync::LocationEFS",
    "AWS::DataSync::LocationHDFS",
    "AWS::DataSync::LocationNFS",
    "AWS::DataSync::LocationObjectStorage",
    "AWS::DataSync::LocationS3",
    "AWS::DataSync::LocationSMB",
    "AWS::DataSync::Task",
    "AWS::DirectoryService::MicrosoftAD",
    "AWS::DirectoryService::SimpleAD",
    "AWS::DynamoDB::GlobalTable",
    "AWS::DynamoDB::Table",
    "AWS::EC2::CapacityReservation",
    "AWS::EC2::CustomerGateway",
    "AWS::EC2::DHCPOptions",
    "AWS::EC2::EC2Fleet",
    "AWS::EC2::EIP",
    "AWS::EC2::EIPAssociation",
    "AWS::EC2::EgressOnlyInternetGateway",
    "AWS::EC2::FlowLog",
    "AWS::EC2::GatewayRouteTableAssociation",
    "AWS::EC2::Host",
    "AWS::EC2::Instance",
    "AWS::EC2::InternetGateway",
    "AWS::EC2::KeyPair",
    "AWS::EC2::LaunchTemplate",
    "AWS::EC2::NatGateway",
    "AWS::EC2::NetworkAcl",
    "AWS::EC2::NetworkAclEntry",
    "AWS::EC2::NetworkInterface",
    "AWS::EC2::NetworkInterfaceAttachment",
    "AWS::EC2::NetworkInterfacePermission",
    "AWS::EC2::PlacementGroup",
    "AWS::EC2::PrefixList",
    "AWS::EC2::Route",
    "AWS::EC2::RouteTable",
    "AWS::EC2::SecurityGroup",
    "AWS::EC2::SecurityGroupEgress",
    "AWS::EC2::SecurityGroupIngress",
    "AWS::EC2::SecurityGroupVpcAssociation",
    "AWS::EC2::SpotFleet",
    "AWS::EC2::Subnet",
    "AWS::EC2::SubnetCidrBlock",
    "AWS::EC2::SubnetNetworkAclAssociation",
    "AWS::EC2::SubnetRouteTableAssociation",
    "AWS::EC2::TrafficMirrorFilter",
    "AWS::EC2::TrafficMirrorFilterRule",
    "AWS::EC2::TrafficMirrorSession",
    "AWS::EC2::TrafficMirrorTarget",
    "AWS::EC2::TransitGateway",
    "AWS::EC2::TransitGatewayAttachment",
    "AWS::EC2::TransitGatewayMulticastDomain",
    "AWS::EC2::TransitGatewayMulticastDomainAssociation",
    "AWS::EC2::TransitGatewayMulticastGroupMember",
    "AWS::EC2::TransitGatewayMulticastGroupSource",
    "AWS::EC2::TransitGatewayRoute",
    "AWS::EC2::TransitGatewayRouteTable",
    "AWS::EC2::TransitGatewayRouteTableAssociation",
    "AWS::EC2::TransitGatewayRouteTablePropagation",
    "AWS::EC2::TransitGatewayVpcAttachment",
    "AWS::EC2::VPC",
    "AWS::EC2::VPCBlockPublicAccessExclusion",
    "AWS::EC2::VPCBlockPublicAccessOptions",
    "AWS::EC2::VPCCidrBlock",
    "AWS::EC2::VPCDHCPOptionsAssociation",
    "AWS::EC2::VPCEndpoint",
    "AWS::EC2::VPCEndpointConnectionNotification",
    "AWS::EC2::VPCEndpointService",
    "AWS::EC2::VPCEndpointServicePermissions",
    "AWS::EC2::VPCGatewayAttachment",
    "AWS::EC2::VPCPeeringConnection",
    "AWS::EC2::VPNConnection",
    "AWS::EC2::VPNConnectionRoute",
    "AWS::EC2::VPNGateway",
    "AWS::EC2::VPNGatewayRoutePropagation",
    "AWS::EC2::Volume",
    "AWS::EC2::VolumeAttachment",
    "AWS::ECR::PullThroughCacheRule",
    "AWS::ECR::RegistryPolicy",
    "AWS::ECR::ReplicationConfiguration",
    "AWS::ECR::Repository",
    "AWS::ECR::RepositoryCreationTemplate",
    "AWS::ECS::CapacityProvider",
    "AWS::ECS::Cluster",
    "AWS::ECS::ClusterCapacityProviderAssociations",
    "AWS::ECS::PrimaryTaskSet",
    "AWS::ECS::Service",
    "AWS::ECS::TaskDefinition",
    "AWS::ECS::TaskSet",
    "AWS::EFS::AccessPoint",
    "AWS::EFS::FileSystem",
    "AWS::EFS::MountTarget",
    "AWS::EKS::AccessEntry",
    "AWS::EKS::Addon",
    "AWS::EKS::Cluster",
    "AWS::EKS::IdentityProviderConfig",
    "AWS::EKS::Nodegroup",
    "AWS::EKS::PodIdentityAssociation",
    "AWS::EMR::Cluster",
    "AWS::EMR::InstanceFleetConfig",
    "AWS::EMR::InstanceGroupConfig",
    "AWS::EMR::SecurityConfiguration",
    "AWS::EMR::Step",
    "AWS::ElastiCache::CacheCluster",
    "AWS::ElastiCache::ParameterGroup",
    "AWS::ElastiCache::ReplicationGroup",
    "AWS::ElastiCache::SecurityGroup",
    "AWS::ElastiCache::SecurityGroupIngress",
    "AWS::ElastiCache::SubnetGroup",
    "AWS::ElastiCache::User",
    "AWS::ElastiCache::UserGroup",
    "AWS::ElasticBeanstalk::Application",
    "AWS::ElasticBeanstalk::ApplicationVersion",
    "AWS::ElasticBeanstalk::ConfigurationTemplate",
    "AWS::ElasticBeanstalk::Environment",
    "AWS::ElasticLoadBalancing::LoadBalancer",
    "AWS::ElasticLoadBalancingV2::Listener",
    "AWS::ElasticLoadBalancingV2::ListenerCertificate",
    "AWS::ElasticLoadBalancingV2::ListenerRule",
    "AWS::ElasticLoadBalancingV2::LoadBalancer",
    "AWS::ElasticLoadBalancingV2::TargetGroup",
    "AWS::ElasticLoadBalancingV2::TrustStore",
    "AWS::ElasticLoadBalancingV2::TrustStoreRevocation",
    "AWS::Elasticsearch::Domain",
    "AWS::Events::EventBus",
    "AWS::Events::Rule",
    "AWS::GameLift::Alias",
    "AWS::GameLift::Build",
    "AWS::GameLift::Fleet",
    "AWS::IAM::AccessKey",
    "AWS::IAM::Group",
    "AWS::IAM::GroupPolicy",
    "AWS::IAM::InstanceProfile",
    "AWS::IAM::ManagedPolicy",
    "AWS::IAM::OIDCProvider",
    "AWS::IAM::Policy",
    "AWS::IAM::Role",
    "AWS::IAM::RolePolicy",
    "AWS::IAM::SAMLProvider",
    "AWS::IAM::ServerCertificate",
    "AWS::IAM::ServiceLinkedRole",
    "AWS::IAM::User",
    "AWS::IAM::UserPolicy",
    "AWS::IAM::UserToGroupAddition",
    "AWS::IoT::Certificate",
    "AWS::IoT::Policy",
    "AWS::IoT::PolicyPrincipalAttachment",
    "AWS::IoT::Thing",
    "AWS::IoT::ThingPrincipalAttachment",
    "AWS::IoT::TopicRule",
    "AWS::KMS::Alias",
    "AWS::KMS::Key",
    "AWS::KMS::ReplicaKey",
    "AWS::Kinesis::ResourcePolicy",
    "AWS::Kinesis::Stream",
    "AWS::Kinesis::StreamConsumer",
    "AWS::KinesisFirehose::DeliveryStream",
    "AWS::Lambda::Alias",
    "AWS::Lambda::EventInvokeConfig",
    "AWS::Lambda::EventSourceMapping",
    "AWS::Lambda::Function",
    "AWS::Lambda::LayerVersion",
    "AWS::Lambda::LayerVersionPermission",
    "AWS::Lambda::Permission",
    "AWS::Lambda::Version",
    "AWS::Logs::Destination",
    "AWS::Logs::LogGroup",
    "AWS::Logs::LogStream",
    "AWS::Logs::MetricFilter",
    "AWS::Logs::QueryDefinition",
    "AWS::Logs::ResourcePolicy",
    "AWS::Logs::SubscriptionFilter",
    "AWS::Oam::Link",
    "AWS::Oam::Sink",
    "AWS::OpenSearchService::Domain",
    "AWS::OpsWorks::App",
    "AWS::OpsWorks::ElasticLoadBalancerAttachment",
    "AWS::OpsWorks::Instance",
    "AWS::OpsWorks::Layer",
    "AWS::OpsWorks::Stack",
    "AWS::OpsWorks::UserProfile",
    "AWS::OpsWorks::Volume",
    "AWS::Organizations::Account",
    "AWS::Organizations::Organization",
    "AWS::Organizations::OrganizationalUnit",
    "AWS::Organizations::Policy",
    "AWS::Organizations::ResourcePolicy",
    "AWS::RAM::ResourceShare",
    "AWS::RDS::DBCluster",
    "AWS::RDS::DBClusterParameterGroup",
    "AWS::RDS::DBInstance",
    "AWS::RDS::DBParameterGroup",
    "AWS::RDS::DBSecurityGroup",
    "AWS::RDS::DBSecurityGroupIngress",
    "AWS::RDS::DBSubnetGroup",
    "AWS::RDS::EventSubscription",
    "AWS::RDS::GlobalCluster",
    "AWS::RDS::OptionGroup",
    "AWS::Redshift::Cluster",
    "AWS::Redshift::ClusterParameterGroup",
    "AWS::Redshift::ClusterSecurityGroup",
    "AWS::Redshift::ClusterSecurityGroupIngress",
    "AWS::Redshift::ClusterSubnetGroup",
    "AWS::Redshift::EndpointAccess",
    "AWS::Redshift::EndpointAuthorization",
    "AWS::Redshift::EventSubscription",
    "AWS::Redshift::ScheduledAction",
    "AWS::ResourceGroups::Group",
    "AWS::RolesAnywhere::CRL",
    "AWS::RolesAnywhere::Profile",
    "AWS::RolesAnywhere::TrustAnchor",
    "AWS::Route53::HealthCheck",
    "AWS::Route53::HostedZone",
    "AWS::Route53::RecordSet",
    "AWS::Route53::RecordSetGroup",
    "AWS::Route53Resolver::ResolverConfig",
    "AWS::Route53Resolver::ResolverEndpoint",
    "AWS::Route53Resolver::ResolverRule",
    "AWS::Route53Resolver::ResolverRuleAssociation",
    "AWS::S3::AccessPoint",
    "AWS::S3::Bucket",
    "AWS::S3::BucketPolicy",
    "AWS::S3ObjectLambda::AccessPoint",
    "AWS::S3ObjectLambda::AccessPointPolicy",
    "AWS::SDB::Domain",
    "AWS::SNS::Subscription",
    "AWS::SNS::Topic",
    "AWS::SNS::TopicInlinePolicy",
    "AWS::SNS::TopicPolicy",
    "AWS::SQS::Queue",
    "AWS::SQS::QueueInlinePolicy",
    "AWS::SQS::QueuePolicy",
    "AWS::SSM::Association",
    "AWS::SSM::Document",
    "AWS::SSM::MaintenanceWindow",
    "AWS::SSM::MaintenanceWindowTarget",
    "AWS::SSM::MaintenanceWindowTask",
    "AWS::SSM::Parameter",
    "AWS::SSM::PatchBaseline",
    "AWS::SSM::ResourceDataSync",
    "AWS::SecretsManager::ResourcePolicy",
    "AWS::SecretsManager::RotationSchedule",
    "AWS::SecretsManager::Secret",
    "AWS::SecretsManager::SecretTargetAttachment",
    "AWS::ServiceDiscovery::HttpNamespace",
    "AWS::ServiceDiscovery::Instance",
    "AWS::ServiceDiscovery::PrivateDnsNamespace",
    "AWS::ServiceDiscovery::PublicDnsNamespace",
    "AWS::ServiceDiscovery::Service",
    "AWS::StepFunctions::Activity",
    "AWS::StepFunctions::StateMachine",
    "AWS::StepFunctions::StateMachineAlias",
    "AWS::StepFunctions::StateMachineVersion",
    "AWS::Synthetics::Canary",
    "AWS::WAF::ByteMatchSet",
    "AWS::WAF::IPSet",
    "AWS::WAF::Rule",
    "AWS::WAF::SizeConstraintSet",
    "AWS::WAF::SqlInjectionMatchSet",
    "AWS::WAF::WebACL",
    "AWS::WAF::XssMatchSet",
    "AWS::WorkSpaces::Workspace",
    "AWS::XRay::Group",
    "AWS::XRay::ResourcePolicy",
    "AWS::XRay::SamplingRule",
    "Module",
]

# pylint: disable=too-many-lines
cached: list[str] = [
    "Module",
    "aws-accessanalyzer-analyzer.json",
    "aws-acmpca-certificate.json",
    "aws-acmpca-certificateauthority.json",
    "aws-acmpca-certificateauthorityactivation.json",
    "aws-acmpca-permission.json",
    "aws-apigateway-account.json",
    "aws-apigateway-apikey.json",
    "aws-apigateway-authorizer.json",
    "aws-apigateway-basepathmapping.json",
    "aws-apigateway-clientcertificate.json",
    "aws-apigateway-deployment.json",
    "aws-apigateway-documentationpart.json",
    "aws-apigateway-documentationversion.json",
    "aws-apigateway-gatewayresponse.json",
    "aws-apigateway-method.json",
    "aws-apigateway-model.json",
    "aws-apigateway-requestvalidator.json",
    "aws-apigateway-resource.json",
    "aws-apigateway-stage.json",
    "aws-apigateway-usageplan.json",
    "aws-apigateway-usageplankey.json",
    "aws-apigateway-vpclink.json",
    "aws-appconfig-application.json",
    "aws-appconfig-configurationprofile.json",
    "aws-appconfig-environment.json",
    "aws-appconfig-extension.json",
    "aws-appconfig-extensionassociation.json",
    "aws-appconfig-hostedconfigurationversion.json",
    "aws-arczonalshift-autoshiftobservernotificationstatus.json",
    "aws-arczonalshift-zonalautoshiftconfiguration.json",
    "aws-autoscaling-autoscalinggroup.json",
    "aws-autoscaling-warmpool.json",
    "aws-backup-backupplan.json",
    "aws-backup-backupselection.json",
    "aws-backup-backupvault.json",
    "aws-batch-computeenvironment.json",
    "aws-batch-jobdefinition.json",
    "aws-batch-jobqueue.json",
    "aws-batch-schedulingpolicy.json",
    "aws-certificatemanager-certificate.json",
    "aws-cloudformation-customresource.json",
    "aws-cloudformation-macro.json",
    "aws-cloudformation-resourcedefaultversion.json",
    "aws-cloudformation-resourceversion.json",
    "aws-cloudformation-stackset.json",
    "aws-cloudformation-waitconditionhandle.json",
    "aws-cloudfront-anycastiplist.json",
    "aws-cloudfront-cachepolicy.json",
    "aws-cloudfront-cloudfrontoriginaccessidentity.json",
    "aws-cloudfront-continuousdeploymentpolicy.json",
    "aws-cloudfront-distribution.json",
    "aws-cloudfront-function.json",
    "aws-cloudfront-keygroup.json",
    "aws-cloudfront-keyvaluestore.json",
    "aws-cloudfront-monitoringsubscription.json",
    "aws-cloudfront-originaccesscontrol.json",
    "aws-cloudfront-originrequestpolicy.json",
    "aws-cloudfront-publickey.json",
    "aws-cloudfront-realtimelogconfig.json",
    "aws-cloudfront-responseheaderspolicy.json",
    "aws-cloudtrail-trail.json",
    "aws-cloudwatch-alarm.json",
    "aws-cloudwatch-anomalydetector.json",
    "aws-cloudwatch-compositealarm.json",
    "aws-cloudwatch-insightrule.json",
    "aws-codedeploy-deploymentgroup.json",
    "aws-config-configurationrecorder.json",
    "aws-config-deliverychannel.json",
    "aws-datasync-agent.json",
    "aws-datasync-locationazureblob.json",
    "aws-datasync-locationhdfs.json",
    "aws-datasync-locationnfs.json",
    "aws-datasync-locationobjectstorage.json",
    "aws-datasync-locations3.json",
    "aws-datasync-locationsmb.json",
    "aws-datasync-task.json",
    "aws-dlm-lifecyclepolicy.json",
    "aws-dynamodb-globaltable.json",
    "aws-dynamodb-table.json",
    "aws-ec2-capacityreservation.json",
    "aws-ec2-dhcpoptions.json",
    "aws-ec2-ec2fleet.json",
    "aws-ec2-egressonlyinternetgateway.json",
    "aws-ec2-flowlog.json",
    "aws-ec2-gatewayroutetableassociation.json",
    "aws-ec2-internetgateway.json",
    "aws-ec2-keypair.json",
    "aws-ec2-launchtemplate.json",
    "aws-ec2-natgateway.json",
    "aws-ec2-networkacl.json",
    "aws-ec2-networkaclentry.json",
    "aws-ec2-networkinterface.json",
    "aws-ec2-placementgroup.json",
    "aws-ec2-prefixlist.json",
    "aws-ec2-route.json",
    "aws-ec2-routetable.json",
    "aws-ec2-securitygroup.json",
    "aws-ec2-securitygroupegress.json",
    "aws-ec2-securitygroupingress.json",
    "aws-ec2-securitygroupvpcassociation.json",
    "aws-ec2-spotfleet.json",
    "aws-ec2-subnet.json",
    "aws-ec2-subnetcidrblock.json",
    "aws-ec2-subnetroutetableassociation.json",
    "aws-ec2-trafficmirrorfilter.json",
    "aws-ec2-trafficmirrorfilterrule.json",
    "aws-ec2-trafficmirrortarget.json",
    "aws-ec2-transitgateway.json",
    "aws-ec2-transitgatewayattachment.json",
    "aws-ec2-transitgatewaymulticastdomain.json",
    "aws-ec2-transitgatewaymulticastdomainassociation.json",
    "aws-ec2-transitgatewaymulticastgroupmember.json",
    "aws-ec2-transitgatewaymulticastgroupsource.json",
    "aws-ec2-transitgatewayroute.json",
    "aws-ec2-transitgatewayroutetable.json",
    "aws-ec2-transitgatewayroutetableassociation.json",
    "aws-ec2-transitgatewayroutetablepropagation.json",
    "aws-ec2-transitgatewayvpcattachment.json",
    "aws-ec2-vpc.json",
    "aws-ec2-vpcblockpublicaccessexclusion.json",
    "aws-ec2-vpcblockpublicaccessoptions.json",
    "aws-ec2-vpccidrblock.json",
    "aws-ec2-vpcdhcpoptionsassociation.json",
    "aws-ec2-vpcendpoint.json",
    "aws-ec2-vpcendpointconnectionnotification.json",
    "aws-ec2-vpcendpointservice.json",
    "aws-ec2-vpcendpointservicepermissions.json",
    "aws-ec2-vpcpeeringconnection.json",
    "aws-ec2-vpngatewayroutepropagation.json",
    "aws-ecr-pullthroughcacherule.json",
    "aws-ecr-registrypolicy.json",
    "aws-ecr-replicationconfiguration.json",
    "aws-ecr-repository.json",
    "aws-ecr-repositorycreationtemplate.json",
    "aws-ecs-capacityprovider.json",
    "aws-ecs-cluster.json",
    "aws-ecs-clustercapacityproviderassociations.json",
    "aws-ecs-primarytaskset.json",
    "aws-ecs-service.json",
    "aws-ecs-taskdefinition.json",
    "aws-ecs-taskset.json",
    "aws-efs-accesspoint.json",
    "aws-efs-filesystem.json",
    "aws-efs-mounttarget.json",
    "aws-eks-accessentry.json",
    "aws-eks-addon.json",
    "aws-eks-cluster.json",
    "aws-eks-identityproviderconfig.json",
    "aws-eks-nodegroup.json",
    "aws-eks-podidentityassociation.json",
    "aws-elasticache-cachecluster.json",
    "aws-elasticache-replicationgroup.json",
    "aws-elasticache-securitygroup.json",
    "aws-elasticache-securitygroupingress.json",
    "aws-elasticache-user.json",
    "aws-elasticache-usergroup.json",
    "aws-elasticloadbalancing-loadbalancer.json",
    "aws-elasticloadbalancingv2-listener.json",
    "aws-elasticloadbalancingv2-listenercertificate.json",
    "aws-elasticloadbalancingv2-listenerrule.json",
    "aws-elasticloadbalancingv2-loadbalancer.json",
    "aws-elasticloadbalancingv2-targetgroup.json",
    "aws-elasticloadbalancingv2-truststore.json",
    "aws-elasticloadbalancingv2-truststorerevocation.json",
    "aws-elasticsearch-domain.json",
    "aws-emr-cluster.json",
    "aws-emr-instancefleetconfig.json",
    "aws-emr-instancegroupconfig.json",
    "aws-events-eventbus.json",
    "aws-events-rule.json",
    "aws-iam-group.json",
    "aws-iam-grouppolicy.json",
    "aws-iam-instanceprofile.json",
    "aws-iam-managedpolicy.json",
    "aws-iam-oidcprovider.json",
    "aws-iam-policy.json",
    "aws-iam-role.json",
    "aws-iam-rolepolicy.json",
    "aws-iam-samlprovider.json",
    "aws-iam-servercertificate.json",
    "aws-iam-servicelinkedrole.json",
    "aws-iam-user.json",
    "aws-iam-userpolicy.json",
    "aws-iam-usertogroupaddition.json",
    "aws-kinesis-resourcepolicy.json",
    "aws-kinesis-stream.json",
    "aws-kms-alias.json",
    "aws-kms-key.json",
    "aws-kms-replicakey.json",
    "aws-lambda-eventinvokeconfig.json",
    "aws-lambda-eventsourcemapping.json",
    "aws-lambda-function.json",
    "aws-lambda-layerversionpermission.json",
    "aws-lambda-permission.json",
    "aws-lambda-version.json",
    "aws-logs-destination.json",
    "aws-logs-loggroup.json",
    "aws-logs-logstream.json",
    "aws-logs-metricfilter.json",
    "aws-logs-querydefinition.json",
    "aws-logs-resourcepolicy.json",
    "aws-logs-subscriptionfilter.json",
    "aws-oam-link.json",
    "aws-oam-sink.json",
    "aws-opensearchservice-domain.json",
    "aws-opsworks-app.json",
    "aws-opsworks-elasticloadbalancerattachment.json",
    "aws-opsworks-userprofile.json",
    "aws-opsworks-volume.json",
    "aws-organizations-account.json",
    "aws-organizations-organization.json",
    "aws-organizations-organizationalunit.json",
    "aws-organizations-policy.json",
    "aws-organizations-resourcepolicy.json",
    "aws-rds-dbcluster.json",
    "aws-rds-dbclusterparametergroup.json",
    "aws-rds-dbinstance.json",
    "aws-rds-dbparametergroup.json",
    "aws-rds-dbsecuritygroup.json",
    "aws-rds-dbsecuritygroupingress.json",
    "aws-rds-dbsubnetgroup.json",
    "aws-rds-eventsubscription.json",
    "aws-rds-globalcluster.json",
    "aws-rds-optiongroup.json",
    "aws-redshift-cluster.json",
    "aws-redshift-clusterparametergroup.json",
    "aws-redshift-clustersecuritygroup.json",
    "aws-redshift-clustersecuritygroupingress.json",
    "aws-redshift-clustersubnetgroup.json",
    "aws-redshift-endpointaccess.json",
    "aws-redshift-endpointauthorization.json",
    "aws-redshift-eventsubscription.json",
    "aws-redshift-scheduledaction.json",
    "aws-resourcegroups-group.json",
    "aws-rolesanywhere-crl.json",
    "aws-rolesanywhere-profile.json",
    "aws-rolesanywhere-trustanchor.json",
    "aws-route53-recordset.json",
    "aws-route53-recordsetgroup.json",
    "aws-route53resolver-resolverconfig.json",
    "aws-route53resolver-resolverendpoint.json",
    "aws-route53resolver-resolverrule.json",
    "aws-route53resolver-resolverruleassociation.json",
    "aws-s3-accesspoint.json",
    "aws-s3-bucketpolicy.json",
    "aws-s3objectlambda-accesspoint.json",
    "aws-s3objectlambda-accesspointpolicy.json",
    "aws-sdb-domain.json",
    "aws-secretsmanager-resourcepolicy.json",
    "aws-secretsmanager-rotationschedule.json",
    "aws-secretsmanager-secret.json",
    "aws-secretsmanager-secrettargetattachment.json",
    "aws-servicediscovery-httpnamespace.json",
    "aws-servicediscovery-instance.json",
    "aws-servicediscovery-privatednsnamespace.json",
    "aws-servicediscovery-publicdnsnamespace.json",
    "aws-servicediscovery-service.json",
    "aws-sns-topic.json",
    "aws-sns-topicinlinepolicy.json",
    "aws-sns-topicpolicy.json",
    "aws-sqs-queue.json",
    "aws-sqs-queueinlinepolicy.json",
    "aws-sqs-queuepolicy.json",
    "aws-ssm-association.json",
    "aws-ssm-document.json",
    "aws-ssm-maintenancewindow.json",
    "aws-ssm-maintenancewindowtarget.json",
    "aws-ssm-maintenancewindowtask.json",
    "aws-ssm-parameter.json",
    "aws-ssm-patchbaseline.json",
    "aws-ssm-resourcedatasync.json",
    "aws-stepfunctions-activity.json",
    "aws-stepfunctions-statemachine.json",
    "aws-stepfunctions-statemachinealias.json",
    "aws-stepfunctions-statemachineversion.json",
    "aws-synthetics-canary.json",
    "aws-waf-bytematchset.json",
    "aws-waf-sqlinjectionmatchset.json",
    "aws-workspaces-workspace.json",
    "aws-xray-group.json",
    "aws-xray-resourcepolicy.json",
    "aws-xray-samplingrule.json",
    "module.json",
]
