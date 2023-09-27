from typing import List

# pylint: disable=too-many-lines
types = [
    "AWS::CDK::Metadata",
    "AWS::Shield::DRTAccess",
    "AWS::SSO::Assignment",
    "AWS::EC2::TransitGatewayRouteTablePropagation",
    "AWS::Shield::ProactiveEngagement",
    "AWS::ApiGateway::BasePathMapping",
    "AWS::GuardDuty::Filter",
    "AWS::ECS::Service",
    "AWS::RAM::ResourceShare",
    "AWS::DMS::ReplicationConfig",
    "AWS::DynamoDB::Table",
    "AWS::AmazonMQ::ConfigurationAssociation",
    "AWS::EC2::SecurityGroupEgress",
    "AWS::EC2::LocalGatewayRouteTableVPCAssociation",
    "AWS::Config::ConfigurationRecorder",
    "AWS::EC2::NetworkPerformanceMetricSubscription",
    "AWS::CloudFront::ContinuousDeploymentPolicy",
    "AWS::ECR::ReplicationConfiguration",
    "AWS::AppConfig::ExtensionAssociation",
    "AWS::EC2::IPAMPoolCidr",
    "AWS::Redshift::ClusterSubnetGroup",
    "AWS::RDS::DBInstance",
    "AWS::EC2::VPCDHCPOptionsAssociation",
    "AWS::ApiGateway::Model",
    "AWS::EC2::NetworkAcl",
    "AWS::Lambda::EventSourceMapping",
    "AWS::Logs::ResourcePolicy",
    "AWS::EC2::NetworkAclEntry",
    "AWS::Transfer::Certificate",
    "AWS::ApiGateway::DocumentationPart",
    "AWS::Route53Resolver::FirewallDomainList",
    "AWS::AppConfig::Application",
    "AWS::OpsWorks::Stack",
    "AWS::Lambda::Url",
    "AWS::GameLift::Fleet",
    "AWS::DataSync::LocationFSxWindows",
    "AWS::GameLift::Build",
    "AWS::ApiGateway::RequestValidator",
    "AWS::AutoScaling::WarmPool",
    "AWS::ApplicationAutoScaling::ScalableTarget",
    "AWS::Config::StoredQuery",
    "AWS::ACMPCA::Permission",
    "AWS::Transfer::Server",
    "AWS::ApiGateway::DomainName",
    "AWS::ECS::PrimaryTaskSet",
    "AWS::AutoScaling::AutoScalingGroup",
    "AWS::WAFv2::RegexPatternSet",
    "AWS::EKS::FargateProfile",
    "AWS::Route53::DNSSEC",
    "AWS::EC2::TransitGatewayRouteTable",
    "AWS::ControlTower::EnabledControl",
    "AWS::Route53::RecordSet",
    "AWS::ElastiCache::SecurityGroup",
    "AWS::OpsWorks::Layer",
    "AWS::CloudTrail::EventDataStore",
    "AWS::KinesisFirehose::DeliveryStream",
    "AWS::PCAConnectorAD::DirectoryRegistration",
    "AWS::SageMaker::CodeRepository",
    "AWS::ImageBuilder::Component",
    "AWS::SES::ConfigurationSetEventDestination",
    "AWS::AppMesh::Route",
    "AWS::IAM::Group",
    "AWS::Organizations::ResourcePolicy",
    "AWS::EC2::TransitGatewayMulticastGroupSource",
    "AWS::Transfer::Profile",
    "AWS::GuardDuty::PublishingDestination",
    "AWS::GameLift::Alias",
    "AWS::AppSync::DomainName",
    "AWS::ApiGateway::UsagePlanKey",
    "AWS::FMS::Policy",
    "AWS::CloudFront::RealtimeLogConfig",
    "AWS::SageMaker::Pipeline",
    "AWS::CloudTrail::Channel",
    "AWS::LakeFormation::DataCellsFilter",
    "AWS::DataSync::LocationHDFS",
    "AWS::Events::Archive",
    "AWS::MSK::Cluster",
    "AWS::CodePipeline::Pipeline",
    "AWS::OpsWorks::Instance",
    "AWS::Config::ConfigurationAggregator",
    "AWS::ImageBuilder::ImagePipeline",
    "AWS::ElasticLoadBalancingV2::ListenerCertificate",
    "AWS::CloudFormation::ModuleVersion",
    "AWS::Synthetics::Canary",
    "AWS::SNS::Subscription",
    "AWS::AppMesh::Mesh",
    "AWS::EC2::NatGateway",
    "AWS::InternetMonitor::Monitor",
    "AWS::Transfer::Workflow",
    "AWS::AppConfig::DeploymentStrategy",
    "AWS::SageMaker::ModelPackage",
    "AWS::EventSchemas::Discoverer",
    "AWS::ElastiCache::UserGroup",
    "AWS::ImageBuilder::ImageRecipe",
    "AWS::ApiGateway::RestApi",
    "AWS::OpsWorks::ElasticLoadBalancerAttachment",
    "AWS::AppMesh::VirtualService",
    "AWS::S3ObjectLambda::AccessPointPolicy",
    "AWS::ElastiCache::ReplicationGroup",
    "AWS::StepFunctions::StateMachineAlias",
    "AWS::RDS::GlobalCluster",
    "AWS::CloudFormation::ModuleDefaultVersion",
    "AWS::SSO::PermissionSet",
    "AWS::ServiceCatalog::CloudFormationProvisionedProduct",
    "AWS::Route53::HostedZone",
    "AWS::Logs::MetricFilter",
    "AWS::Lambda::Function",
    "AWS::SNS::Topic",
    "AWS::Backup::BackupSelection",
    "AWS::DataSync::LocationFSxLustre",
    "AWS::SageMaker::App",
    "AWS::EC2::VPCGatewayAttachment",
    "AWS::CloudTrail::Trail",
    "AWS::EC2::VPNConnectionRoute",
    "AWS::EC2::InternetGateway",
    "AWS::EC2::GatewayRouteTableAssociation",
    "AWS::WAFv2::IPSet",
    "AWS::SSM::Document",
    "AWS::IAM::Role",
    "AWS::Events::ApiDestination",
    "AWS::CloudFront::CloudFrontOriginAccessIdentity",
    "AWS::SageMaker::EndpointConfig",
    "AWS::AppMesh::GatewayRoute",
    "AWS::ApiGateway::ApiKey",
    "AWS::AutoScaling::LaunchConfiguration",
    "AWS::ApiGateway::ClientCertificate",
    "AWS::KinesisAnalyticsV2::Application",
    "AWS::Lambda::Alias",
    "AWS::WAF::IPSet",
    "AWS::EC2::TransitGatewayMulticastDomainAssociation",
    "AWS::WAF::SizeConstraintSet",
    "AWS::EC2::TransitGatewayRouteTableAssociation",
    "AWS::AppConfig::Environment",
    "AWS::ImageBuilder::Image",
    "AWS::ElastiCache::SecurityGroupIngress",
    "AWS::RDS::DBProxyTargetGroup",
    "AWS::CloudWatch::Dashboard",
    "AWS::CloudWatch::Alarm",
    "AWS::GuardDuty::Member",
    "AWS::CloudFormation::CustomResource",
    "AWS::WAFv2::RuleGroup",
    "AWS::SageMaker::ModelPackageGroup",
    "AWS::SES::ConfigurationSet",
    "AWS::ElastiCache::ParameterGroup",
    "AWS::NetworkFirewall::LoggingConfiguration",
    "AWS::CodeDeploy::DeploymentGroup",
    "AWS::CloudFormation::StackSet",
    "AWS::EC2::Route",
    "AWS::CloudFormation::HookVersion",
    "AWS::RolesAnywhere::Profile",
    "AWS::XRay::ResourcePolicy",
    "AWS::WAFv2::LoggingConfiguration",
    "AWS::Backup::BackupPlan",
    "AWS::ImageBuilder::DistributionConfiguration",
    "AWS::LakeFormation::Permissions",
    "AWS::CloudFront::PublicKey",
    "AWS::PCAConnectorAD::Connector",
    "AWS::IdentityStore::Group",
    "AWS::RAM::Permission",
    "AWS::DataSync::Task",
    "AWS::ECS::TaskDefinition",
    "AWS::SageMaker::Model",
    "AWS::Shield::Protection",
    "AWS::SES::VdmAttributes",
    "AWS::IdentityStore::GroupMembership",
    "AWS::AppSync::FunctionConfiguration",
    "AWS::EC2::SpotFleet",
    "AWS::SageMaker::Space",
    "AWS::IoT::PolicyPrincipalAttachment",
    "AWS::FMS::NotificationChannel",
    "AWS::MSK::BatchScramSecret",
    "AWS::S3::Bucket",
    "AWS::GuardDuty::IPSet",
    "AWS::EMR::SecurityConfiguration",
    "AWS::CloudWatch::InsightRule",
    "AWS::ApiGateway::UsagePlan",
    "AWS::Batch::SchedulingPolicy",
    "AWS::Athena::WorkGroup",
    "AWS::SageMaker::ImageVersion",
    "AWS::ApiGateway::VpcLink",
    "AWS::IAM::ServerCertificate",
    "AWS::Events::EventBus",
    "AWS::SQS::QueueInlinePolicy",
    "AWS::Organizations::Organization",
    "AWS::SSM::MaintenanceWindowTarget",
    "AWS::ApiGateway::Authorizer",
    "AWS::IAM::Policy",
    "AWS::SES::ContactList",
    "AWS::RDS::DBSecurityGroupIngress",
    "AWS::EC2::TransitGatewayMulticastGroupMember",
    "AWS::EC2::VolumeAttachment",
    "AWS::ApplicationInsights::Application",
    "AWS::ECS::ClusterCapacityProviderAssociations",
    "AWS::AppConfig::ConfigurationProfile",
    "AWS::Route53Resolver::FirewallRuleGroup",
    "AWS::MSK::Configuration",
    "AWS::EC2::TransitGateway",
    "AWS::EC2::VPCEndpointServicePermissions",
    "AWS::SSM::MaintenanceWindowTask",
    "AWS::EC2::TransitGatewayMulticastDomain",
    "AWS::VerifiedPermissions::PolicyTemplate",
    "AWS::EKS::Cluster",
    "AWS::EFS::FileSystem",
    "AWS::Logs::QueryDefinition",
    "AWS::IAM::InstanceProfile",
    "AWS::DataSync::LocationNFS",
    "AWS::SageMaker::Domain",
    "AWS::CertificateManager::Certificate",
    "AWS::SDB::Domain",
    "AWS::EC2::SubnetRouteTableAssociation",
    "AWS::ServiceCatalog::ServiceActionAssociation",
    "AWS::ImageBuilder::ContainerRecipe",
    "AWS::EFS::AccessPoint",
    "AWS::Redshift::ClusterSecurityGroupIngress",
    "AWS::ServiceCatalogAppRegistry::AttributeGroupAssociation",
    "AWS::ElasticLoadBalancingV2::LoadBalancer",
    "AWS::OpenSearchService::Domain",
    "AWS::Elasticsearch::Domain",
    "AWS::EC2::NetworkInterfacePermission",
    "AWS::SecretsManager::ResourcePolicy",
    "AWS::CloudFormation::HookDefaultVersion",
    "AWS::Config::ConfigRule",
    "AWS::ECS::TaskSet",
    "AWS::AppSync::ApiKey",
    "AWS::ACMPCA::CertificateAuthorityActivation",
    "AWS::GuardDuty::ThreatIntelSet",
    "AWS::EC2::VPC",
    "AWS::MSK::VpcConnection",
    "AWS::DataSync::LocationAzureBlob",
    "AWS::Logs::LogStream",
    "AWS::Route53::RecordSetGroup",
    "AWS::EC2::LocalGatewayRoute",
    "AWS::OpsWorks::App",
    "AWS::Kinesis::Stream",
    "AWS::IAM::SAMLProvider",
    "AWS::CloudFront::KeyGroup",
    "AWS::EC2::NetworkInterfaceAttachment",
    "AWS::EC2::TransitGatewayAttachment",
    "AWS::CodeDeploy::DeploymentConfig",
    "AWS::StepFunctions::StateMachineVersion",
    "AWS::ServiceCatalogAppRegistry::Application",
    "AWS::Backup::BackupVault",
    "AWS::EC2::CustomerGateway",
    "AWS::IAM::GroupPolicy",
    "AWS::Scheduler::Schedule",
    "AWS::WAF::ByteMatchSet",
    "AWS::EC2::Host",
    "AWS::SystemsManagerSAP::Application",
    "AWS::EC2::RouteTable",
    "AWS::RDS::DBProxyEndpoint",
    "AWS::DataSync::LocationSMB",
    "AWS::SecurityHub::Standard",
    "AWS::RolesAnywhere::CRL",
    "AWS::SNS::TopicInlinePolicy",
    "AWS::Redshift::ClusterParameterGroup",
    "AWS::Organizations::Policy",
    "AWS::GlobalAccelerator::Listener",
    "AWS::VerifiedPermissions::PolicyStore",
    "AWS::EC2::VPCPeeringConnection",
    "AWS::SNS::TopicPolicy",
    "AWS::NetworkFirewall::RuleGroup",
    "AWS::KMS::Key",
    "AWS::Route53Resolver::FirewallRuleGroupAssociation",
    "AWS::Route53Resolver::ResolverQueryLoggingConfig",
    "AWS::EC2::Subnet",
    "AWS::CloudTrail::ResourcePolicy",
    "AWS::S3ObjectLambda::AccessPoint",
    "AWS::WAF::Rule",
    "AWS::ElasticBeanstalk::ConfigurationTemplate",
    "AWS::SQS::QueuePolicy",
    "AWS::AppSync::DomainNameApiAssociation",
    "AWS::ApiGateway::Account",
    "AWS::WAFv2::WebACL",
    "AWS::GlobalAccelerator::EndpointGroup",
    "AWS::EC2::TransitGatewayConnect",
    "AWS::EC2::SecurityGroup",
    "AWS::OpsWorks::Volume",
    "AWS::SES::EmailIdentity",
    "AWS::IAM::UserToGroupAddition",
    "AWS::Events::Rule",
    "AWS::EC2::VPNGatewayRoutePropagation",
    "AWS::CloudFront::Function",
    "AWS::ApiGateway::Method",
    "AWS::SSM::PatchBaseline",
    "AWS::CloudFront::MonitoringSubscription",
    "AWS::EFS::MountTarget",
    "AWS::EC2::VPNConnection",
    "AWS::WAF::WebACL",
    "AWS::Shield::ProtectionGroup",
    "AWS::IAM::User",
    "AWS::EMR::InstanceGroupConfig",
    "AWS::StepFunctions::Activity",
    "AWS::SageMaker::Project",
    "AWS::EC2::LocalGatewayRouteTableVirtualInterfaceGroupAssociation",
    "AWS::Logs::AccountPolicy",
    "AWS::S3::BucketPolicy",
    "AWS::AppSync::GraphQLSchema",
    "AWS::Redshift::Cluster",
    "AWS::EMR::InstanceFleetConfig",
    "AWS::EMR::Cluster",
    "AWS::RDS::DBCluster",
    "AWS::Transfer::Agreement",
    "AWS::Chatbot::SlackChannelConfiguration",
    "AWS::CloudFront::Distribution",
    "AWS::ElastiCache::SubnetGroup",
    "AWS::XRay::Group",
    "AWS::Oam::Link",
    "AWS::SageMaker::Endpoint",
    "AWS::NetworkFirewall::Firewall",
    "AWS::EventSchemas::Schema",
    "AWS::SES::Template",
    "AWS::KMS::ReplicaKey",
    "AWS::Redshift::ClusterSecurityGroup",
    "AWS::Route53::CidrCollection",
    "AWS::ECR::PullThroughCacheRule",
    "AWS::AppConfig::HostedConfigurationVersion",
    "AWS::DataSync::LocationEFS",
    "AWS::EC2::LocalGatewayRouteTable",
    "AWS::ApiGateway::Resource",
    "AWS::SageMaker::AppImageConfig",
    "AWS::ElasticLoadBalancingV2::TargetGroup",
    "AWS::ApplicationAutoScaling::ScalingPolicy",
    "AWS::Pipes::Pipe",
    "AWS::CloudFormation::Macro",
    "AWS::SageMaker::Workteam",
    "AWS::Lambda::LayerVersionPermission",
    "AWS::SecretsManager::Secret",
    "AWS::ElastiCache::User",
    "AWS::SageMaker::Image",
    "AWS::Logs::SubscriptionFilter",
    "AWS::CodeDeploy::Application",
    "AWS::IoT::TopicRule",
    "AWS::LakeFormation::PrincipalPermissions",
    "AWS::DataSync::LocationS3",
    "AWS::AutoScaling::LifecycleHook",
    "AWS::FSx::DataRepositoryAssociation",
    "AWS::EC2::NetworkInterface",
    "AWS::SageMaker::FeatureGroup",
    "AWS::AppSync::Resolver",
    "AWS::RolesAnywhere::TrustAnchor",
    "AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation",
    "AWS::Lambda::LayerVersion",
    "AWS::RDS::OptionGroup",
    "AWS::OpsWorks::UserProfile",
    "AWS::IoT::Policy",
    "AWS::EC2::TransitGatewayRoute",
    "AWS::SSM::MaintenanceWindow",
    "AWS::LakeFormation::TagAssociation",
    "AWS::EC2::IPAMResourceDiscovery",
    "AWS::ImageBuilder::InfrastructureConfiguration",
    "AWS::CloudFormation::WaitCondition",
    "AWS::SageMaker::NotebookInstance",
    "AWS::SSO::InstanceAccessControlAttributeConfiguration",
    "AWS::CloudWatch::AnomalyDetector",
    "AWS::EC2::SubnetNetworkAclAssociation",
    "AWS::ServiceCatalog::ServiceAction",
    "AWS::IAM::UserPolicy",
    "AWS::CloudFront::OriginAccessControl",
    "AWS::SecretsManager::RotationSchedule",
    "AWS::Lambda::Permission",
    "AWS::NetworkFirewall::FirewallPolicy",
    "AWS::EKS::IdentityProviderConfig",
    "AWS::EC2::IPAMResourceDiscoveryAssociation",
    "AWS::ServiceCatalogAppRegistry::AttributeGroup",
    "AWS::AppSync::GraphQLApi",
    "AWS::EC2::EgressOnlyInternetGateway",
    "AWS::EC2::VPCCidrBlock",
    "AWS::ACMPCA::CertificateAuthority",
    "AWS::Athena::PreparedStatement",
    "AWS::AutoScaling::ScheduledAction",
    "AWS::LakeFormation::Resource",
    "AWS::EC2::IPAMScope",
    "AWS::DirectoryService::SimpleAD",
    "AWS::EC2::VPCEndpoint",
    "AWS::RDS::EventSubscription",
    "AWS::Config::AggregationAuthorization",
    "AWS::DataSync::Agent",
    "AWS::Logs::LogGroup",
    "AWS::ECS::Cluster",
    "AWS::PCAConnectorAD::Template",
    "AWS::EC2::PlacementGroup",
    "AWS::Organizations::Account",
    "AWS::ECR::Repository",
    "AWS::SES::DedicatedIpPool",
    "AWS::AppConfig::Extension",
    "AWS::ElasticLoadBalancingV2::ListenerRule",
    "AWS::EC2::KeyPair",
    "AWS::FSx::FileSystem",
    "AWS::EC2::EIPAssociation",
    "AWS::ElasticBeanstalk::Application",
    "AWS::IoT::ThingPrincipalAttachment",
    "AWS::EC2::CapacityReservation",
    "AWS::ElasticLoadBalancing::LoadBalancer",
    "AWS::Transfer::User",
    "AWS::IAM::RolePolicy",
    "AWS::StepFunctions::StateMachine",
    "AWS::RDS::DBClusterParameterGroup",
    "AWS::WAF::XssMatchSet",
    "AWS::AppMesh::VirtualRouter",
    "AWS::Scheduler::ScheduleGroup",
    "AWS::Route53::KeySigningKey",
    "AWS::EventSchemas::Registry",
    "AWS::Config::RemediationConfiguration",
    "AWS::Events::Connection",
    "AWS::Athena::DataCatalog",
    "AWS::SageMaker::UserProfile",
    "AWS::EC2::PrefixList",
    "AWS::EC2::Instance",
    "AWS::EC2::SubnetCidrBlock",
    "AWS::ElasticBeanstalk::ApplicationVersion",
    "AWS::AppMesh::VirtualGateway",
    "AWS::WAF::SqlInjectionMatchSet",
    "AWS::EC2::TransitGatewayVpcAttachment",
    "AWS::EC2::FlowLog",
    "AWS::AmazonMQ::Broker",
    "AWS::EMR::Step",
    "AWS::SSM::Association",
    "AWS::CloudFront::ResponseHeadersPolicy",
    "AWS::SecurityHub::AutomationRule",
    "AWS::MSK::ClusterPolicy",
    "AWS::GuardDuty::Master",
    "AWS::KMS::Alias",
    "AWS::XRay::SamplingRule",
    "AWS::Transfer::Connector",
    "AWS::AppMesh::VirtualNode",
    "AWS::ApiGateway::DocumentationVersion",
    "AWS::WAFv2::WebACLAssociation",
    "AWS::Oam::Sink",
    "AWS::ApiGateway::GatewayResponse",
    "AWS::Route53Resolver::OutpostResolver",
    "AWS::ACMPCA::Certificate",
    "AWS::EC2::IPAMAllocation",
    "AWS::WorkSpaces::Workspace",
    "AWS::EC2::InstanceConnectEndpoint",
    "AWS::DirectoryService::MicrosoftAD",
    "AWS::AppSync::SourceApiAssociation",
    "AWS::DataSync::LocationObjectStorage",
    "AWS::ECS::CapacityProvider",
    "AWS::ElastiCache::CacheCluster",
    "AWS::SageMaker::ModelCard",
    "AWS::Logs::Destination",
    "AWS::EKS::Nodegroup",
    "AWS::Organizations::OrganizationalUnit",
    "AWS::AppSync::DataSource",
    "AWS::SQS::Queue",
    "AWS::EC2::SecurityGroupIngress",
    "AWS::GuardDuty::Detector",
    "AWS::ApiGateway::Stage",
    "AWS::Batch::ComputeEnvironment",
    "AWS::DataPipeline::Pipeline",
    "AWS::IoT::Thing",
    "AWS::Route53::HealthCheck",
    "AWS::Events::EventBusPolicy",
    "AWS::Athena::NamedQuery",
    "AWS::ApiGateway::Deployment",
    "AWS::LakeFormation::DataLakeSettings",
    "AWS::AutoScaling::ScalingPolicy",
    "AWS::ECR::RegistryPolicy",
    "AWS::RDS::DBSecurityGroup",
    "AWS::CloudWatch::MetricStream",
    "AWS::Config::DeliveryChannel",
    "AWS::IAM::OIDCProvider",
    "AWS::LakeFormation::Tag",
    "AWS::ServiceCatalogAppRegistry::ResourceAssociation",
    "AWS::EC2::VPNGateway",
    "AWS::CloudFormation::Stack",
    "AWS::ResourceGroups::Group",
    "AWS::CloudFormation::ResourceDefaultVersion",
    "AWS::SSM::ResourceDataSync",
    "AWS::EC2::IPAM",
    "AWS::PCAConnectorAD::TemplateGroupAccessControlEntry",
    "AWS::EC2::TransitGatewayPeeringAttachment",
    "AWS::CloudFront::CachePolicy",
    "AWS::IAM::AccessKey",
    "AWS::RDS::DBSubnetGroup",
    "AWS::SecretsManager::SecretTargetAttachment",
    "AWS::AmazonMQ::Configuration",
    "AWS::AppConfig::Deployment",
    "AWS::CodePipeline::CustomActionType",
    "AWS::AccessAnalyzer::Analyzer",
    "AWS::EC2::EC2Fleet",
    "AWS::EC2::VPCEndpointService",
    "AWS::IAM::ManagedPolicy",
    "AWS::EC2::LaunchTemplate",
    "AWS::CloudFront::OriginRequestPolicy",
    "AWS::DataSync::LocationFSxONTAP",
    "AWS::PCAConnectorAD::ServicePrincipalName",
    "AWS::ElasticBeanstalk::Environment",
    "AWS::Lambda::Version",
    "AWS::EC2::DHCPOptions",
    "AWS::EC2::IPAMPool",
    "AWS::IAM::ServiceLinkedRole",
    "AWS::CloudFormation::HookTypeConfig",
    "AWS::EC2::Volume",
    "AWS::IoT::Certificate",
    "AWS::EC2::EIP",
    "AWS::VerifiedPermissions::Policy",
    "AWS::CloudFormation::ResourceVersion",
    "AWS::Chatbot::MicrosoftTeamsChannelConfiguration",
    "AWS::RDS::DBProxy",
    "AWS::RDS::DBParameterGroup",
    "AWS::S3::AccessPoint",
    "AWS::Batch::JobQueue",
    "AWS::ElasticLoadBalancingV2::Listener",
    "AWS::CloudFormation::WaitConditionHandle",
    "AWS::GlobalAccelerator::Accelerator",
    "AWS::EKS::Addon",
]

# pylint: disable=too-many-lines
cached: List[str] = [
    "aws-shield-drtaccess.json",
    "aws-sso-assignment.json",
    "aws-ec2-transitgatewayroutetablepropagation.json",
    "aws-shield-proactiveengagement.json",
    "aws-guardduty-filter.json",
    "aws-ecs-service.json",
    "aws-ram-resourceshare.json",
    "aws-dms-replicationconfig.json",
    "aws-dynamodb-table.json",
    "aws-ec2-securitygroupegress.json",
    "aws-ec2-localgatewayroutetablevpcassociation.json",
    "aws-config-configurationrecorder.json",
    "aws-ec2-networkperformancemetricsubscription.json",
    "aws-cloudfront-continuousdeploymentpolicy.json",
    "aws-ecr-replicationconfiguration.json",
    "aws-appconfig-extensionassociation.json",
    "aws-ec2-ipampoolcidr.json",
    "aws-rds-dbinstance.json",
    "aws-ec2-vpcdhcpoptionsassociation.json",
    "aws-ec2-networkacl.json",
    "aws-lambda-eventsourcemapping.json",
    "aws-logs-resourcepolicy.json",
    "aws-transfer-certificate.json",
    "aws-route53resolver-firewalldomainlist.json",
    "aws-appconfig-application.json",
    "aws-lambda-url.json",
    "aws-datasync-locationfsxwindows.json",
    "aws-autoscaling-warmpool.json",
    "aws-applicationautoscaling-scalabletarget.json",
    "aws-config-storedquery.json",
    "aws-acmpca-permission.json",
    "aws-transfer-server.json",
    "aws-ecs-primarytaskset.json",
    "aws-autoscaling-autoscalinggroup.json",
    "aws-wafv2-regexpatternset.json",
    "aws-eks-fargateprofile.json",
    "aws-route53-dnssec.json",
    "aws-ec2-transitgatewayroutetable.json",
    "aws-controltower-enabledcontrol.json",
    "aws-route53-recordset.json",
    "aws-elasticache-securitygroup.json",
    "aws-cloudtrail-eventdatastore.json",
    "aws-kinesisfirehose-deliverystream.json",
    "aws-pcaconnectorad-directoryregistration.json",
    "aws-sagemaker-coderepository.json",
    "aws-imagebuilder-component.json",
    "aws-ses-configurationseteventdestination.json",
    "aws-appmesh-route.json",
    "aws-organizations-resourcepolicy.json",
    "aws-ec2-transitgatewaymulticastgroupsource.json",
    "aws-transfer-profile.json",
    "aws-fms-policy.json",
    "aws-cloudfront-realtimelogconfig.json",
    "aws-sagemaker-pipeline.json",
    "aws-cloudtrail-channel.json",
    "aws-lakeformation-datacellsfilter.json",
    "aws-datasync-locationhdfs.json",
    "aws-events-archive.json",
    "aws-msk-cluster.json",
    "aws-codepipeline-pipeline.json",
    "aws-config-configurationaggregator.json",
    "aws-imagebuilder-imagepipeline.json",
    "aws-elasticloadbalancingv2-listenercertificate.json",
    "aws-cloudformation-moduleversion.json",
    "aws-synthetics-canary.json",
    "aws-sns-subscription.json",
    "aws-appmesh-mesh.json",
    "aws-ec2-natgateway.json",
    "aws-internetmonitor-monitor.json",
    "aws-transfer-workflow.json",
    "aws-appconfig-deploymentstrategy.json",
    "aws-sagemaker-modelpackage.json",
    "aws-eventschemas-discoverer.json",
    "aws-elasticache-usergroup.json",
    "aws-imagebuilder-imagerecipe.json",
    "aws-opsworks-elasticloadbalancerattachment.json",
    "aws-appmesh-virtualservice.json",
    "aws-s3objectlambda-accesspointpolicy.json",
    "aws-elasticache-replicationgroup.json",
    "aws-stepfunctions-statemachinealias.json",
    "aws-rds-globalcluster.json",
    "aws-cloudformation-moduledefaultversion.json",
    "aws-sso-permissionset.json",
    "aws-servicecatalog-cloudformationprovisionedproduct.json",
    "aws-logs-metricfilter.json",
    "aws-lambda-function.json",
    "aws-sns-topic.json",
    "aws-backup-backupselection.json",
    "aws-datasync-locationfsxlustre.json",
    "aws-sagemaker-app.json",
    "aws-ec2-vpcgatewayattachment.json",
    "aws-cloudtrail-trail.json",
    "aws-ec2-vpnconnectionroute.json",
    "aws-ec2-internetgateway.json",
    "aws-wafv2-ipset.json",
    "aws-ssm-document.json",
    "aws-events-apidestination.json",
    "aws-cloudfront-cloudfrontoriginaccessidentity.json",
    "aws-sagemaker-endpointconfig.json",
    "aws-appmesh-gatewayroute.json",
    "aws-autoscaling-launchconfiguration.json",
    "aws-kinesisanalyticsv2-application.json",
    "aws-lambda-alias.json",
    "aws-ec2-transitgatewaymulticastdomainassociation.json",
    "aws-ec2-transitgatewayroutetableassociation.json",
    "aws-appconfig-environment.json",
    "aws-imagebuilder-image.json",
    "aws-elasticache-securitygroupingress.json",
    "aws-rds-dbproxytargetgroup.json",
    "aws-cloudwatch-dashboard.json",
    "aws-cloudwatch-alarm.json",
    "aws-guardduty-member.json",
    "aws-cloudformation-customresource.json",
    "aws-wafv2-rulegroup.json",
    "aws-sagemaker-modelpackagegroup.json",
    "aws-ses-configurationset.json",
    "aws-elasticache-parametergroup.json",
    "aws-networkfirewall-loggingconfiguration.json",
    "aws-codedeploy-deploymentgroup.json",
    "aws-cloudformation-stackset.json",
    "aws-ec2-route.json",
    "aws-cloudformation-hookversion.json",
    "aws-rolesanywhere-profile.json",
    "aws-xray-resourcepolicy.json",
    "aws-wafv2-loggingconfiguration.json",
    "aws-backup-backupplan.json",
    "aws-imagebuilder-distributionconfiguration.json",
    "aws-lakeformation-permissions.json",
    "aws-cloudfront-publickey.json",
    "aws-pcaconnectorad-connector.json",
    "aws-identitystore-group.json",
    "aws-ram-permission.json",
    "aws-datasync-task.json",
    "aws-ecs-taskdefinition.json",
    "aws-sagemaker-model.json",
    "aws-shield-protection.json",
    "aws-ses-vdmattributes.json",
    "aws-identitystore-groupmembership.json",
    "aws-appsync-functionconfiguration.json",
    "aws-sagemaker-space.json",
    "aws-fms-notificationchannel.json",
    "aws-msk-batchscramsecret.json",
    "aws-guardduty-ipset.json",
    "aws-emr-securityconfiguration.json",
    "aws-cloudwatch-insightrule.json",
    "aws-batch-schedulingpolicy.json",
    "aws-athena-workgroup.json",
    "aws-sagemaker-imageversion.json",
    "aws-iam-servercertificate.json",
    "aws-events-eventbus.json",
    "aws-sqs-queueinlinepolicy.json",
    "aws-organizations-organization.json",
    "aws-ssm-maintenancewindowtarget.json",
    "aws-iam-policy.json",
    "aws-ses-contactlist.json",
    "aws-rds-dbsecuritygroupingress.json",
    "aws-ec2-transitgatewaymulticastgroupmember.json",
    "aws-ec2-volumeattachment.json",
    "aws-applicationinsights-application.json",
    "aws-ecs-clustercapacityproviderassociations.json",
    "aws-appconfig-configurationprofile.json",
    "aws-route53resolver-firewallrulegroup.json",
    "aws-msk-configuration.json",
    "aws-ec2-vpcendpointservicepermissions.json",
    "aws-ssm-maintenancewindowtask.json",
    "aws-ec2-transitgatewaymulticastdomain.json",
    "aws-verifiedpermissions-policytemplate.json",
    "aws-eks-cluster.json",
    "aws-efs-filesystem.json",
    "aws-logs-querydefinition.json",
    "aws-iam-instanceprofile.json",
    "aws-datasync-locationnfs.json",
    "aws-sagemaker-domain.json",
    "aws-certificatemanager-certificate.json",
    "aws-sdb-domain.json",
    "aws-ec2-subnetroutetableassociation.json",
    "aws-servicecatalog-serviceactionassociation.json",
    "aws-imagebuilder-containerrecipe.json",
    "aws-efs-accesspoint.json",
    "aws-redshift-clustersecuritygroupingress.json",
    "aws-servicecatalogappregistry-attributegroupassociation.json",
    "aws-opensearchservice-domain.json",
    "aws-elasticsearch-domain.json",
    "aws-secretsmanager-resourcepolicy.json",
    "aws-cloudformation-hookdefaultversion.json",
    "aws-config-configrule.json",
    "aws-ecs-taskset.json",
    "aws-appsync-apikey.json",
    "aws-acmpca-certificateauthorityactivation.json",
    "aws-guardduty-threatintelset.json",
    "aws-ec2-vpc.json",
    "aws-msk-vpcconnection.json",
    "aws-datasync-locationazureblob.json",
    "aws-logs-logstream.json",
    "aws-route53-recordsetgroup.json",
    "aws-ec2-localgatewayroute.json",
    "aws-opsworks-app.json",
    "aws-kinesis-stream.json",
    "aws-iam-samlprovider.json",
    "aws-cloudfront-keygroup.json",
    "aws-ec2-networkinterfaceattachment.json",
    "aws-ec2-transitgatewayattachment.json",
    "aws-codedeploy-deploymentconfig.json",
    "aws-stepfunctions-statemachineversion.json",
    "aws-servicecatalogappregistry-application.json",
    "aws-backup-backupvault.json",
    "aws-ec2-customergateway.json",
    "aws-iam-grouppolicy.json",
    "aws-scheduler-schedule.json",
    "aws-waf-bytematchset.json",
    "aws-systemsmanagersap-application.json",
    "aws-ec2-routetable.json",
    "aws-rds-dbproxyendpoint.json",
    "aws-datasync-locationsmb.json",
    "aws-securityhub-standard.json",
    "aws-rolesanywhere-crl.json",
    "aws-sns-topicinlinepolicy.json",
    "aws-organizations-policy.json",
    "aws-globalaccelerator-listener.json",
    "aws-verifiedpermissions-policystore.json",
    "aws-ec2-vpcpeeringconnection.json",
    "aws-sns-topicpolicy.json",
    "aws-networkfirewall-rulegroup.json",
    "aws-kms-key.json",
    "aws-route53resolver-firewallrulegroupassociation.json",
    "aws-route53resolver-resolverqueryloggingconfig.json",
    "aws-ec2-subnet.json",
    "aws-cloudtrail-resourcepolicy.json",
    "aws-s3objectlambda-accesspoint.json",
    "aws-elasticbeanstalk-configurationtemplate.json",
    "aws-sqs-queuepolicy.json",
    "aws-wafv2-webacl.json",
    "aws-globalaccelerator-endpointgroup.json",
    "aws-ec2-transitgatewayconnect.json",
    "aws-ec2-securitygroup.json",
    "aws-opsworks-volume.json",
    "aws-ses-emailidentity.json",
    "aws-iam-usertogroupaddition.json",
    "aws-cloudfront-function.json",
    "aws-ssm-patchbaseline.json",
    "aws-cloudfront-monitoringsubscription.json",
    "aws-efs-mounttarget.json",
    "aws-ec2-vpnconnection.json",
    "aws-shield-protectiongroup.json",
    "aws-iam-user.json",
    "aws-emr-instancegroupconfig.json",
    "aws-sagemaker-project.json",
    "aws-ec2-localgatewayroutetablevirtualinterfacegroupassociation.json",
    "aws-logs-accountpolicy.json",
    "aws-appsync-graphqlschema.json",
    "aws-emr-instancefleetconfig.json",
    "aws-emr-cluster.json",
    "aws-rds-dbcluster.json",
    "aws-transfer-agreement.json",
    "aws-chatbot-slackchannelconfiguration.json",
    "aws-cloudfront-distribution.json",
    "aws-elasticache-subnetgroup.json",
    "aws-xray-group.json",
    "aws-sagemaker-endpoint.json",
    "aws-eventschemas-schema.json",
    "aws-ses-template.json",
    "aws-kms-replicakey.json",
    "aws-redshift-clustersecuritygroup.json",
    "aws-route53-cidrcollection.json",
    "aws-ecr-pullthroughcacherule.json",
    "aws-appconfig-hostedconfigurationversion.json",
    "aws-datasync-locationefs.json",
    "aws-ec2-localgatewayroutetable.json",
    "aws-sagemaker-appimageconfig.json",
    "aws-elasticloadbalancingv2-targetgroup.json",
    "aws-pipes-pipe.json",
    "aws-cloudformation-macro.json",
    "aws-sagemaker-workteam.json",
    "aws-lambda-layerversionpermission.json",
    "aws-secretsmanager-secret.json",
    "aws-elasticache-user.json",
    "aws-sagemaker-image.json",
    "aws-codedeploy-application.json",
    "aws-lakeformation-principalpermissions.json",
    "aws-datasync-locations3.json",
    "aws-autoscaling-lifecyclehook.json",
    "aws-fsx-datarepositoryassociation.json",
    "aws-ec2-networkinterface.json",
    "aws-sagemaker-featuregroup.json",
    "aws-appsync-resolver.json",
    "aws-rolesanywhere-trustanchor.json",
    "aws-route53resolver-resolverqueryloggingconfigassociation.json",
    "aws-lambda-layerversion.json",
    "aws-rds-optiongroup.json",
    "aws-opsworks-userprofile.json",
    "aws-ssm-maintenancewindow.json",
    "aws-lakeformation-tagassociation.json",
    "aws-ec2-ipamresourcediscovery.json",
    "aws-imagebuilder-infrastructureconfiguration.json",
    "aws-sagemaker-notebookinstance.json",
    "aws-sso-instanceaccesscontrolattributeconfiguration.json",
    "aws-cloudwatch-anomalydetector.json",
    "aws-servicecatalog-serviceaction.json",
    "aws-iam-userpolicy.json",
    "aws-cloudfront-originaccesscontrol.json",
    "aws-secretsmanager-rotationschedule.json",
    "aws-networkfirewall-firewallpolicy.json",
    "aws-eks-identityproviderconfig.json",
    "aws-ec2-ipamresourcediscoveryassociation.json",
    "aws-servicecatalogappregistry-attributegroup.json",
    "aws-appsync-graphqlapi.json",
    "aws-ec2-egressonlyinternetgateway.json",
    "aws-ec2-vpccidrblock.json",
    "aws-acmpca-certificateauthority.json",
    "aws-athena-preparedstatement.json",
    "aws-autoscaling-scheduledaction.json",
    "aws-lakeformation-resource.json",
    "aws-ec2-ipamscope.json",
    "aws-ec2-vpcendpoint.json",
    "aws-rds-eventsubscription.json",
    "aws-config-aggregationauthorization.json",
    "aws-datasync-agent.json",
    "aws-logs-loggroup.json",
    "aws-pcaconnectorad-template.json",
    "aws-ec2-placementgroup.json",
    "aws-organizations-account.json",
    "aws-ecr-repository.json",
    "aws-ses-dedicatedippool.json",
    "aws-appconfig-extension.json",
    "aws-ec2-keypair.json",
    "aws-fsx-filesystem.json",
    "aws-ec2-eipassociation.json",
    "aws-elasticbeanstalk-application.json",
    "aws-ec2-capacityreservation.json",
    "aws-elasticloadbalancing-loadbalancer.json",
    "aws-transfer-user.json",
    "aws-iam-rolepolicy.json",
    "aws-stepfunctions-statemachine.json",
    "aws-rds-dbclusterparametergroup.json",
    "aws-appmesh-virtualrouter.json",
    "aws-scheduler-schedulegroup.json",
    "aws-route53-keysigningkey.json",
    "aws-eventschemas-registry.json",
    "aws-config-remediationconfiguration.json",
    "aws-events-connection.json",
    "aws-athena-datacatalog.json",
    "aws-sagemaker-userprofile.json",
    "aws-ec2-prefixlist.json",
    "aws-ec2-instance.json",
    "aws-ec2-subnetcidrblock.json",
    "aws-appmesh-virtualgateway.json",
    "aws-waf-sqlinjectionmatchset.json",
    "aws-ec2-transitgatewayvpcattachment.json",
    "aws-ec2-flowlog.json",
    "aws-amazonmq-broker.json",
    "aws-ssm-association.json",
    "aws-cloudfront-responseheaderspolicy.json",
    "aws-securityhub-automationrule.json",
    "aws-msk-clusterpolicy.json",
    "aws-kms-alias.json",
    "aws-xray-samplingrule.json",
    "aws-transfer-connector.json",
    "aws-appmesh-virtualnode.json",
    "aws-wafv2-webaclassociation.json",
    "aws-oam-sink.json",
    "aws-apigateway-gatewayresponse.json",
    "aws-route53resolver-outpostresolver.json",
    "aws-acmpca-certificate.json",
    "aws-ec2-ipamallocation.json",
    "aws-workspaces-workspace.json",
    "aws-ec2-instanceconnectendpoint.json",
    "aws-datasync-locationobjectstorage.json",
    "aws-ecs-capacityprovider.json",
    "aws-elasticache-cachecluster.json",
    "aws-sagemaker-modelcard.json",
    "aws-logs-destination.json",
    "aws-eks-nodegroup.json",
    "aws-organizations-organizationalunit.json",
    "aws-appsync-datasource.json",
    "aws-sqs-queue.json",
    "aws-ec2-securitygroupingress.json",
    "aws-guardduty-detector.json",
    "aws-batch-computeenvironment.json",
    "aws-events-eventbuspolicy.json",
    "aws-athena-namedquery.json",
    "aws-lakeformation-datalakesettings.json",
    "aws-autoscaling-scalingpolicy.json",
    "aws-rds-dbsecuritygroup.json",
    "aws-cloudwatch-metricstream.json",
    "aws-config-deliverychannel.json",
    "aws-iam-oidcprovider.json",
    "aws-lakeformation-tag.json",
    "aws-servicecatalogappregistry-resourceassociation.json",
    "aws-ec2-vpngateway.json",
    "aws-cloudformation-stack.json",
    "aws-resourcegroups-group.json",
    "aws-cloudformation-resourcedefaultversion.json",
    "aws-ec2-ipam.json",
    "aws-pcaconnectorad-templategroupaccesscontrolentry.json",
    "aws-ec2-transitgatewaypeeringattachment.json",
    "aws-cloudfront-cachepolicy.json",
    "aws-rds-dbsubnetgroup.json",
    "aws-amazonmq-configuration.json",
    "aws-appconfig-deployment.json",
    "aws-accessanalyzer-analyzer.json",
    "aws-ec2-ec2fleet.json",
    "aws-ec2-vpcendpointservice.json",
    "aws-iam-managedpolicy.json",
    "aws-ec2-launchtemplate.json",
    "aws-cloudfront-originrequestpolicy.json",
    "aws-datasync-locationfsxontap.json",
    "aws-pcaconnectorad-serviceprincipalname.json",
    "aws-elasticbeanstalk-environment.json",
    "aws-lambda-version.json",
    "aws-ec2-dhcpoptions.json",
    "aws-ec2-ipampool.json",
    "aws-iam-servicelinkedrole.json",
    "aws-cloudformation-hooktypeconfig.json",
    "aws-ec2-volume.json",
    "aws-ec2-eip.json",
    "aws-verifiedpermissions-policy.json",
    "aws-cloudformation-resourceversion.json",
    "aws-chatbot-microsoftteamschannelconfiguration.json",
    "aws-rds-dbproxy.json",
    "aws-rds-dbparametergroup.json",
    "aws-s3-accesspoint.json",
    "aws-batch-jobqueue.json",
    "aws-cloudformation-waitconditionhandle.json",
    "aws-globalaccelerator-accelerator.json",
    "aws-eks-addon.json",
]
