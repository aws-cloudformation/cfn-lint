# pylint: disable=too-many-lines
types = [
    "AWS::CDK::Metadata",
    "AWS::ApiGatewayV2::Integration",
    "AWS::ApiGatewayV2::ApiMapping",
    "AWS::SSO::Assignment",
    "AWS::Glue::Partition",
    "AWS::EC2::TransitGatewayRouteTablePropagation",
    "AWS::SSM::ResourcePolicy",
    "AWS::ApiGateway::BasePathMapping",
    "AWS::GuardDuty::Filter",
    "AWS::ECS::Service",
    "AWS::ServiceCatalog::PortfolioPrincipalAssociation",
    "AWS::RAM::ResourceShare",
    "AWS::DynamoDB::Table",
    "AWS::AmazonMQ::ConfigurationAssociation",
    "AWS::EC2::SecurityGroupEgress",
    "AWS::EC2::LocalGatewayRouteTableVPCAssociation",
    "AWS::Config::OrganizationConfigRule",
    "AWS::Config::ConfigurationRecorder",
    "AWS::Greengrass::DeviceDefinition",
    "AWS::AppConfig::ExtensionAssociation",
    "AWS::S3Outposts::AccessPoint",
    "AWS::EC2::IPAMPoolCidr",
    "AWS::IoT::TopicRuleDestination",
    "AWS::Redshift::ClusterSubnetGroup",
    "AWS::RDS::DBInstance",
    "AWS::EC2::VPCDHCPOptionsAssociation",
    "AWS::ApiGateway::Model",
    "AWS::ApiGatewayV2::IntegrationResponse",
    "AWS::EC2::NetworkAcl",
    "AWS::Lambda::EventSourceMapping",
    "AWS::Logs::ResourcePolicy",
    "AWS::ServiceCatalog::LaunchNotificationConstraint",
    "AWS::IoT::CACertificate",
    "AWS::EC2::NetworkAclEntry",
    "AWS::Transfer::Certificate",
    "AWS::ApiGateway::DocumentationPart",
    "AWS::CloudWatch::CompositeAlarm",
    "AWS::Route53Resolver::FirewallDomainList",
    "AWS::AppConfig::Application",
    "AWS::OpsWorks::Stack",
    "AWS::GameLift::Fleet",
    "AWS::DataSync::LocationFSxWindows",
    "AWS::GameLift::Build",
    "AWS::ApiGateway::RequestValidator",
    "AWS::AutoScaling::WarmPool",
    "AWS::ApplicationAutoScaling::ScalableTarget",
    "AWS::ApiGatewayV2::Model",
    "AWS::Config::StoredQuery",
    "AWS::ACMPCA::Permission",
    "AWS::Neptune::DBSubnetGroup",
    "AWS::Cassandra::Keyspace",
    "AWS::Transfer::Server",
    "AWS::ApiGateway::DomainName",
    "AWS::ECS::PrimaryTaskSet",
    "AWS::AutoScaling::AutoScalingGroup",
    "AWS::WAFv2::RegexPatternSet",
    "AWS::EC2::TransitGatewayRouteTable",
    "AWS::Route53::RecordSet",
    "AWS::ElastiCache::SecurityGroup",
    "AWS::OpsWorks::Layer",
    "AWS::KinesisFirehose::DeliveryStream",
    "AWS::ImageBuilder::Component",
    "AWS::Glue::Connection",
    "AWS::IAM::Group",
    "AWS::Organizations::ResourcePolicy",
    "AWS::EC2::TransitGatewayMulticastGroupSource",
    "AWS::Transfer::Profile",
    "AWS::GameLift::Alias",
    "AWS::ApiGateway::UsagePlanKey",
    "AWS::Greengrass::FunctionDefinition",
    "AWS::DataSync::LocationHDFS",
    "AWS::MSK::Cluster",
    "AWS::EC2::VPCEndpointConnectionNotification",
    "AWS::CodePipeline::Pipeline",
    "AWS::OpsWorks::Instance",
    "AWS::Config::ConfigurationAggregator",
    "AWS::ImageBuilder::ImagePipeline",
    "AWS::ElasticLoadBalancingV2::ListenerCertificate",
    "AWS::CloudFormation::ModuleVersion",
    "AWS::Route53Resolver::ResolverRuleAssociation",
    "AWS::FSx::StorageVirtualMachine",
    "AWS::Greengrass::ConnectorDefinitionVersion",
    "AWS::Synthetics::Canary",
    "AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption",
    "AWS::SNS::Subscription",
    "AWS::EC2::NatGateway",
    "AWS::Greengrass::ConnectorDefinition",
    "AWS::Transfer::Workflow",
    "AWS::AppConfig::DeploymentStrategy",
    "AWS::Glue::DevEndpoint",
    "AWS::ElastiCache::UserGroup",
    "AWS::IoT::ThingGroup",
    "AWS::ImageBuilder::ImageRecipe",
    "AWS::ApiGateway::RestApi",
    "AWS::OpsWorks::ElasticLoadBalancerAttachment",
    "AWS::S3ObjectLambda::AccessPointPolicy",
    "AWS::NetworkManager::TransitGatewayRegistration",
    "AWS::ElastiCache::ReplicationGroup",
    "AWS::Cassandra::Table",
    "AWS::CloudFormation::ModuleDefaultVersion",
    "AWS::SSO::PermissionSet",
    "AWS::Glue::Job",
    "AWS::ServiceCatalog::CloudFormationProvisionedProduct",
    "AWS::Route53::HostedZone",
    "AWS::Glue::Table",
    "AWS::Logs::MetricFilter",
    "AWS::Lambda::Function",
    "AWS::SNS::Topic",
    "AWS::Backup::BackupSelection",
    "AWS::DataSync::LocationFSxLustre",
    "AWS::EC2::VPCGatewayAttachment",
    "AWS::CloudTrail::Trail",
    "AWS::EC2::VPNConnectionRoute",
    "AWS::EC2::InternetGateway",
    "AWS::EC2::GatewayRouteTableAssociation",
    "AWS::WAFv2::IPSet",
    "AWS::Greengrass::SubscriptionDefinition",
    "AWS::Greengrass::Group",
    "AWS::SSM::Document",
    "AWS::IAM::Role",
    "AWS::DMS::Endpoint",
    "AWS::ApiGateway::ApiKey",
    "AWS::AutoScaling::LaunchConfiguration",
    "AWS::ApiGateway::ClientCertificate",
    "AWS::KinesisAnalyticsV2::Application",
    "AWS::Lambda::Alias",
    "AWS::WAF::IPSet",
    "AWS::EC2::TransitGatewayMulticastDomainAssociation",
    "AWS::S3Outposts::Endpoint",
    "AWS::WAF::SizeConstraintSet",
    "AWS::EC2::TransitGatewayRouteTableAssociation",
    "AWS::AppConfig::Environment",
    "AWS::ImageBuilder::Image",
    "AWS::ElastiCache::SecurityGroupIngress",
    "AWS::CloudWatch::Dashboard",
    "AWS::CloudWatch::Alarm",
    "AWS::IoT::ThingType",
    "AWS::GuardDuty::Member",
    "AWS::CloudFormation::CustomResource",
    "AWS::KinesisAnalytics::ApplicationOutput",
    "AWS::WAFv2::RuleGroup",
    "AWS::ElastiCache::ParameterGroup",
    "AWS::NetworkFirewall::LoggingConfiguration",
    "AWS::Glue::Classifier",
    "AWS::CodeDeploy::DeploymentGroup",
    "AWS::CloudFormation::StackSet",
    "AWS::EC2::Route",
    "AWS::FIS::ExperimentTemplate",
    "AWS::CodeCommit::Repository",
    "AWS::CloudFormation::HookVersion",
    "AWS::IoT::ResourceSpecificLogging",
    "AWS::ServiceCatalog::LaunchTemplateConstraint",
    "AWS::WAFv2::LoggingConfiguration",
    "AWS::DynamoDB::GlobalTable",
    "AWS::Backup::BackupPlan",
    "AWS::ImageBuilder::DistributionConfiguration",
    "AWS::Glue::DataCatalogEncryptionSettings",
    "AWS::IdentityStore::Group",
    "AWS::RAM::Permission",
    "AWS::DataSync::Task",
    "AWS::ECS::TaskDefinition",
    "AWS::AppStream::AppBlock",
    "AWS::IdentityStore::GroupMembership",
    "AWS::EC2::SpotFleet",
    "AWS::Glue::SchemaVersion",
    "AWS::IoT::PolicyPrincipalAttachment",
    "AWS::MSK::BatchScramSecret",
    "AWS::DMS::Certificate",
    "AWS::S3::Bucket",
    "AWS::GuardDuty::IPSet",
    "AWS::ServiceDiscovery::HttpNamespace",
    "AWS::EMR::SecurityConfiguration",
    "AWS::CloudWatch::InsightRule",
    "AWS::ApiGateway::UsagePlan",
    "AWS::Batch::SchedulingPolicy",
    "AWS::IoT::Authorizer",
    "AWS::ApiGatewayV2::VpcLink",
    "AWS::IoT::JobTemplate",
    "AWS::ServiceCatalog::PortfolioProductAssociation",
    "AWS::Athena::WorkGroup",
    "AWS::ApiGatewayV2::Api",
    "AWS::Detective::Graph",
    "AWS::ServiceCatalog::PortfolioShare",
    "AWS::ApiGateway::VpcLink",
    "AWS::NetworkManager::CustomerGatewayAssociation",
    "AWS::IAM::ServerCertificate",
    "AWS::IoT::SecurityProfile",
    "AWS::Events::EventBus",
    "AWS::SSM::MaintenanceWindowTarget",
    "AWS::ApiGateway::Authorizer",
    "AWS::BackupGateway::Hypervisor",
    "AWS::IAM::Policy",
    "AWS::RDS::DBSecurityGroupIngress",
    "AWS::EC2::TransitGatewayMulticastGroupMember",
    "AWS::EC2::VolumeAttachment",
    "AWS::Glue::SecurityConfiguration",
    "AWS::ApplicationInsights::Application",
    "AWS::ECS::ClusterCapacityProviderAssociations",
    "AWS::AppConfig::ConfigurationProfile",
    "AWS::Route53Resolver::FirewallRuleGroup",
    "AWS::MSK::Configuration",
    "AWS::EC2::TransitGateway",
    "AWS::EC2::VPCEndpointServicePermissions",
    "AWS::SSM::MaintenanceWindowTask",
    "AWS::EC2::TransitGatewayMulticastDomain",
    "AWS::EKS::Cluster",
    "AWS::CodeBuild::Project",
    "AWS::EFS::FileSystem",
    "AWS::Logs::QueryDefinition",
    "AWS::IAM::InstanceProfile",
    "AWS::IoT::BillingGroup",
    "AWS::AppStream::Application",
    "AWS::DataSync::LocationNFS",
    "AWS::KinesisAnalyticsV2::ApplicationOutput",
    "AWS::Greengrass::CoreDefinitionVersion",
    "AWS::CertificateManager::Certificate",
    "AWS::Glue::SchemaVersionMetadata",
    "AWS::SDB::Domain",
    "AWS::EC2::SubnetRouteTableAssociation",
    "AWS::ServiceCatalog::ServiceActionAssociation",
    "AWS::ImageBuilder::ContainerRecipe",
    "AWS::EFS::AccessPoint",
    "AWS::Redshift::ClusterSecurityGroupIngress",
    "AWS::ServiceCatalogAppRegistry::AttributeGroupAssociation",
    "AWS::ElasticLoadBalancingV2::LoadBalancer",
    "AWS::OpenSearchService::Domain",
    "AWS::ServiceDiscovery::Instance",
    "AWS::Elasticsearch::Domain",
    "AWS::KinesisAnalytics::Application",
    "AWS::ApiGatewayV2::Deployment",
    "AWS::ServiceCatalog::StackSetConstraint",
    "AWS::EC2::NetworkInterfacePermission",
    "AWS::ServiceCatalog::TagOption",
    "AWS::ServiceDiscovery::PrivateDnsNamespace",
    "AWS::ServiceCatalog::LaunchRoleConstraint",
    "AWS::IoT::RoleAlias",
    "AWS::SecretsManager::ResourcePolicy",
    "AWS::CloudFormation::HookDefaultVersion",
    "AWS::Config::ConfigRule",
    "AWS::EC2::ClientVpnRoute",
    "AWS::ECS::TaskSet",
    "AWS::ACMPCA::CertificateAuthorityActivation",
    "AWS::GuardDuty::ThreatIntelSet",
    "AWS::EC2::VPC",
    "AWS::MSK::VpcConnection",
    "AWS::Logs::LogStream",
    "AWS::DMS::ReplicationSubnetGroup",
    "AWS::S3Outposts::Bucket",
    "AWS::Route53::RecordSetGroup",
    "AWS::AppStream::ApplicationEntitlementAssociation",
    "AWS::KinesisAnalytics::ApplicationReferenceDataSource",
    "AWS::EC2::LocalGatewayRoute",
    "AWS::OpsWorks::App",
    "AWS::Kinesis::Stream",
    "AWS::Greengrass::CoreDefinition",
    "AWS::Batch::JobDefinition",
    "AWS::IAM::SAMLProvider",
    "AWS::EC2::NetworkInterfaceAttachment",
    "AWS::EC2::TransitGatewayAttachment",
    "AWS::CodeDeploy::DeploymentConfig",
    "AWS::NetworkManager::GlobalNetwork",
    "AWS::ServiceCatalogAppRegistry::Application",
    "AWS::NetworkManager::Site",
    "AWS::Glue::Database",
    "AWS::Neptune::DBCluster",
    "AWS::Backup::BackupVault",
    "AWS::EC2::CustomerGateway",
    "AWS::WAF::ByteMatchSet",
    "AWS::Neptune::DBClusterParameterGroup",
    "AWS::EC2::Host",
    "AWS::DMS::ReplicationTask",
    "AWS::EC2::RouteTable",
    "AWS::DataSync::LocationSMB",
    "AWS::Redshift::ClusterParameterGroup",
    "AWS::Organizations::Policy",
    "AWS::Glue::Trigger",
    "AWS::EC2::VPCPeeringConnection",
    "AWS::SNS::TopicPolicy",
    "AWS::ElastiCache::GlobalReplicationGroup",
    "AWS::NetworkFirewall::RuleGroup",
    "AWS::KMS::Key",
    "AWS::Route53Resolver::ResolverDNSSECConfig",
    "AWS::ServiceCatalog::AcceptedPortfolioShare",
    "AWS::Route53Resolver::FirewallRuleGroupAssociation",
    "AWS::Route53Resolver::ResolverQueryLoggingConfig",
    "AWS::EC2::Subnet",
    "AWS::S3ObjectLambda::AccessPoint",
    "AWS::WAF::Rule",
    "AWS::ElasticBeanstalk::ConfigurationTemplate",
    "AWS::SQS::QueuePolicy",
    "AWS::ApiGateway::Account",
    "AWS::WAFv2::WebACL",
    "AWS::EC2::TransitGatewayConnect",
    "AWS::EC2::SecurityGroup",
    "AWS::OpsWorks::Volume",
    "AWS::IAM::UserToGroupAddition",
    "AWS::Events::Rule",
    "AWS::EC2::VPNGatewayRoutePropagation",
    "AWS::Glue::Crawler",
    "AWS::ApiGateway::Method",
    "AWS::SSM::PatchBaseline",
    "AWS::ServiceDiscovery::Service",
    "AWS::EFS::MountTarget",
    "AWS::EC2::VPNConnection",
    "AWS::WAF::WebACL",
    "AWS::IAM::User",
    "AWS::EMR::InstanceGroupConfig",
    "AWS::StepFunctions::Activity",
    "AWS::Synthetics::Group",
    "AWS::EC2::LocalGatewayRouteTableVirtualInterfaceGroupAssociation",
    "AWS::S3::BucketPolicy",
    "AWS::IoT::CustomMetric",
    "AWS::Redshift::Cluster",
    "AWS::CodeBuild::SourceCredential",
    "AWS::EMR::InstanceFleetConfig",
    "AWS::EMR::Cluster",
    "AWS::CodePipeline::Webhook",
    "AWS::ApiGatewayV2::DomainName",
    "AWS::RDS::DBCluster",
    "AWS::ServiceCatalog::ResourceUpdateConstraint",
    "AWS::Transfer::Agreement",
    "AWS::ElastiCache::SubnetGroup",
    "AWS::NetworkFirewall::Firewall",
    "AWS::KMS::ReplicaKey",
    "AWS::Redshift::ClusterSecurityGroup",
    "AWS::Glue::MLTransform",
    "AWS::AppConfig::HostedConfigurationVersion",
    "AWS::DataSync::LocationEFS",
    "AWS::EC2::LocalGatewayRouteTable",
    "AWS::ApiGateway::Resource",
    "AWS::ElasticLoadBalancingV2::TargetGroup",
    "AWS::ApplicationAutoScaling::ScalingPolicy",
    "AWS::CloudFormation::Macro",
    "AWS::Lambda::LayerVersionPermission",
    "AWS::SecretsManager::Secret",
    "AWS::Route53Resolver::ResolverConfig",
    "AWS::ElastiCache::User",
    "AWS::Neptune::DBInstance",
    "AWS::Logs::SubscriptionFilter",
    "AWS::CodeDeploy::Application",
    "AWS::DMS::EventSubscription",
    "AWS::IoT::TopicRule",
    "AWS::DataSync::LocationS3",
    "AWS::AutoScaling::LifecycleHook",
    "AWS::FSx::DataRepositoryAssociation",
    "AWS::EC2::NetworkInterface",
    "AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation",
    "AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource",
    "AWS::Lambda::EventInvokeConfig",
    "AWS::Lambda::LayerVersion",
    "AWS::RDS::OptionGroup",
    "AWS::OpsWorks::UserProfile",
    "AWS::Glue::Schema",
    "AWS::ServiceCatalog::Portfolio",
    "AWS::IoT::Policy",
    "AWS::EC2::TransitGatewayRoute",
    "AWS::SSM::MaintenanceWindow",
    "AWS::EC2::IPAMResourceDiscovery",
    "AWS::GreengrassV2::ComponentVersion",
    "AWS::ImageBuilder::InfrastructureConfiguration",
    "AWS::IoT::Logging",
    "AWS::CloudFormation::WaitCondition",
    "AWS::Route53Resolver::ResolverEndpoint",
    "AWS::IoT::ScheduledAudit",
    "AWS::NetworkManager::Link",
    "AWS::SSO::InstanceAccessControlAttributeConfiguration",
    "AWS::CloudWatch::AnomalyDetector",
    "AWS::EC2::SubnetNetworkAclAssociation",
    "AWS::ServiceCatalog::ServiceAction",
    "AWS::AppStream::Entitlement",
    "AWS::IoT::MitigationAction",
    "AWS::SecretsManager::RotationSchedule",
    "AWS::Lambda::Permission",
    "AWS::NetworkFirewall::FirewallPolicy",
    "AWS::EKS::IdentityProviderConfig",
    "AWS::EC2::IPAMResourceDiscoveryAssociation",
    "AWS::ServiceCatalogAppRegistry::AttributeGroup",
    "AWS::EC2::ClientVpnTargetNetworkAssociation",
    "AWS::EC2::EgressOnlyInternetGateway",
    "AWS::EC2::VPCCidrBlock",
    "AWS::IAM::VirtualMFADevice",
    "AWS::Neptune::DBParameterGroup",
    "AWS::ACMPCA::CertificateAuthority",
    "AWS::AutoScaling::ScheduledAction",
    "AWS::ApiGatewayV2::Route",
    "AWS::Detective::MemberInvitation",
    "AWS::EC2::IPAMScope",
    "AWS::DirectoryService::SimpleAD",
    "AWS::EC2::VPCEndpoint",
    "AWS::RDS::EventSubscription",
    "AWS::Config::AggregationAuthorization",
    "AWS::DataSync::Agent",
    "AWS::IoT::Dimension",
    "AWS::Logs::LogGroup",
    "AWS::ECS::Cluster",
    "AWS::EC2::TrafficMirrorFilterRule",
    "AWS::EC2::PlacementGroup",
    "AWS::ECR::Repository",
    "AWS::IoT::FleetMetric",
    "AWS::Greengrass::SubscriptionDefinitionVersion",
    "AWS::AppConfig::Extension",
    "AWS::ElasticLoadBalancingV2::ListenerRule",
    "AWS::Glue::Registry",
    "AWS::EC2::KeyPair",
    "AWS::FSx::FileSystem",
    "AWS::AppStream::ApplicationFleetAssociation",
    "AWS::EC2::EIPAssociation",
    "AWS::ElasticBeanstalk::Application",
    "AWS::IoT::ThingPrincipalAttachment",
    "AWS::DLM::LifecyclePolicy",
    "AWS::EC2::CapacityReservation",
    "AWS::ElasticLoadBalancing::LoadBalancer",
    "AWS::Transfer::User",
    "AWS::EC2::TrafficMirrorTarget",
    "AWS::StepFunctions::StateMachine",
    "AWS::RDS::DBClusterParameterGroup",
    "AWS::WAF::XssMatchSet",
    "AWS::AppStream::DirectoryConfig",
    "AWS::Inspector::AssessmentTarget",
    "AWS::FSx::Snapshot",
    "AWS::Config::RemediationConfiguration",
    "AWS::Greengrass::LoggerDefinition",
    "AWS::Greengrass::DeviceDefinitionVersion",
    "AWS::Athena::DataCatalog",
    "AWS::Greengrass::FunctionDefinitionVersion",
    "AWS::Glue::Workflow",
    "AWS::ApiGatewayV2::Authorizer",
    "AWS::IoT::AccountAuditConfiguration",
    "AWS::EC2::PrefixList",
    "AWS::EC2::Instance",
    "AWS::NetworkManager::Device",
    "AWS::EC2::SubnetCidrBlock",
    "AWS::ElasticBeanstalk::ApplicationVersion",
    "AWS::WAF::SqlInjectionMatchSet",
    "AWS::EC2::TransitGatewayVpcAttachment",
    "AWS::EC2::FlowLog",
    "AWS::AmazonMQ::Broker",
    "AWS::EMR::Step",
    "AWS::SSM::Association",
    "AWS::EC2::ClientVpnEndpoint",
    "AWS::MSK::ClusterPolicy",
    "AWS::GuardDuty::Master",
    "AWS::KMS::Alias",
    "AWS::Route53Resolver::ResolverRule",
    "AWS::Transfer::Connector",
    "AWS::ApiGateway::DocumentationVersion",
    "AWS::LicenseManager::Grant",
    "AWS::WAFv2::WebACLAssociation",
    "AWS::CodeBuild::ReportGroup",
    "AWS::ApiGateway::GatewayResponse",
    "AWS::EC2::ClientVpnAuthorizationRule",
    "AWS::EC2::EnclaveCertificateIamRoleAssociation",
    "AWS::FSx::Volume",
    "AWS::ACMPCA::Certificate",
    "AWS::EC2::IPAMAllocation",
    "AWS::WorkSpaces::Workspace",
    "AWS::Inspector::AssessmentTemplate",
    "AWS::DirectoryService::MicrosoftAD",
    "AWS::DataSync::LocationObjectStorage",
    "AWS::ECS::CapacityProvider",
    "AWS::ElastiCache::CacheCluster",
    "AWS::Logs::Destination",
    "AWS::EKS::Nodegroup",
    "AWS::Organizations::OrganizationalUnit",
    "AWS::SQS::Queue",
    "AWS::EC2::SecurityGroupIngress",
    "AWS::GuardDuty::Detector",
    "AWS::IoT::ProvisioningTemplate",
    "AWS::ApiGateway::Stage",
    "AWS::Batch::ComputeEnvironment",
    "AWS::DataPipeline::Pipeline",
    "AWS::IoT::Thing",
    "AWS::Route53::HealthCheck",
    "AWS::Events::EventBusPolicy",
    "AWS::Athena::NamedQuery",
    "AWS::EC2::TrafficMirrorFilter",
    "AWS::ApiGateway::Deployment",
    "AWS::Inspector::ResourceGroup",
    "AWS::GreengrassV2::Deployment",
    "AWS::AutoScaling::ScalingPolicy",
    "AWS::Redshift::ScheduledAction",
    "AWS::RDS::DBSecurityGroup",
    "AWS::ApiGatewayV2::RouteResponse",
    "AWS::SSM::Parameter",
    "AWS::ApiGatewayV2::ApiGatewayManagedOverrides",
    "AWS::Config::DeliveryChannel",
    "AWS::CertificateManager::Account",
    "AWS::IAM::OIDCProvider",
    "AWS::ServiceCatalogAppRegistry::ResourceAssociation",
    "AWS::EC2::VPNGateway",
    "AWS::CloudFormation::Stack",
    "AWS::ResourceGroups::Group",
    "AWS::Greengrass::LoggerDefinitionVersion",
    "AWS::ServiceCatalog::TagOptionAssociation",
    "AWS::EC2::IPAM",
    "AWS::EC2::TransitGatewayPeeringAttachment",
    "AWS::IAM::AccessKey",
    "AWS::RDS::DBSubnetGroup",
    "AWS::SecretsManager::SecretTargetAttachment",
    "AWS::AmazonMQ::Configuration",
    "AWS::AppConfig::Deployment",
    "AWS::CodePipeline::CustomActionType",
    "AWS::AccessAnalyzer::Analyzer",
    "AWS::EC2::EC2Fleet",
    "AWS::Greengrass::ResourceDefinition",
    "AWS::DMS::ReplicationInstance",
    "AWS::ServiceCatalog::CloudFormationProduct",
    "AWS::EC2::VPCEndpointService",
    "AWS::IAM::ManagedPolicy",
    "AWS::EC2::LaunchTemplate",
    "AWS::DataSync::LocationFSxONTAP",
    "AWS::NetworkManager::LinkAssociation",
    "AWS::ElasticBeanstalk::Environment",
    "AWS::Lambda::Version",
    "AWS::EC2::DHCPOptions",
    "AWS::EC2::IPAMPool",
    "AWS::Kinesis::StreamConsumer",
    "AWS::IAM::ServiceLinkedRole",
    "AWS::CloudFormation::HookTypeConfig",
    "AWS::EC2::Volume",
    "AWS::LicenseManager::License",
    "AWS::IoT::Certificate",
    "AWS::EC2::EIP",
    "AWS::Greengrass::ResourceDefinitionVersion",
    "AWS::ApiGatewayV2::Stage",
    "AWS::RDS::DBParameterGroup",
    "AWS::SecurityHub::Hub",
    "AWS::S3::AccessPoint",
    "AWS::Greengrass::GroupVersion",
    "AWS::EC2::TrafficMirrorSession",
    "AWS::S3Outposts::BucketPolicy",
    "AWS::Batch::JobQueue",
    "AWS::ElasticLoadBalancingV2::Listener",
    "AWS::Redshift::EventSubscription",
    "AWS::CloudFormation::WaitConditionHandle",
    "AWS::EKS::Addon",
]

# pylint: disable=too-many-lines
cached = [
    "aws-apigatewayv2-integration.json",
    "aws-apigatewayv2-apimapping.json",
    "aws-sso-assignment.json",
    "aws-glue-partition.json",
    "aws-ec2-transitgatewayroutetablepropagation.json",
    "aws-ssm-resourcepolicy.json",
    "aws-guardduty-filter.json",
    "aws-ecs-service.json",
    "aws-ram-resourceshare.json",
    "aws-dynamodb-table.json",
    "aws-ec2-securitygroupegress.json",
    "aws-ec2-localgatewayroutetablevpcassociation.json",
    "aws-config-organizationconfigrule.json",
    "aws-config-configurationrecorder.json",
    "aws-appconfig-extensionassociation.json",
    "aws-s3outposts-accesspoint.json",
    "aws-ec2-ipampoolcidr.json",
    "aws-iot-topicruledestination.json",
    "aws-redshift-clustersubnetgroup.json",
    "aws-ec2-networkacl.json",
    "aws-logs-resourcepolicy.json",
    "aws-servicecatalog-launchnotificationconstraint.json",
    "aws-iot-cacertificate.json",
    "aws-ec2-networkaclentry.json",
    "aws-transfer-certificate.json",
    "aws-cloudwatch-compositealarm.json",
    "aws-route53resolver-firewalldomainlist.json",
    "aws-appconfig-application.json",
    "aws-opsworks-stack.json",
    "aws-datasync-locationfsxwindows.json",
    "aws-autoscaling-warmpool.json",
    "aws-applicationautoscaling-scalabletarget.json",
    "aws-config-storedquery.json",
    "aws-acmpca-permission.json",
    "aws-neptune-dbsubnetgroup.json",
    "aws-cassandra-keyspace.json",
    "aws-transfer-server.json",
    "aws-apigateway-domainname.json",
    "aws-ecs-primarytaskset.json",
    "aws-autoscaling-autoscalinggroup.json",
    "aws-wafv2-regexpatternset.json",
    "aws-ec2-transitgatewayroutetable.json",
    "aws-route53-recordset.json",
    "aws-elasticache-securitygroup.json",
    "aws-opsworks-layer.json",
    "aws-imagebuilder-component.json",
    "aws-glue-connection.json",
    "aws-iam-group.json",
    "aws-ec2-transitgatewaymulticastgroupsource.json",
    "aws-transfer-profile.json",
    "aws-apigateway-usageplankey.json",
    "aws-datasync-locationhdfs.json",
    "aws-msk-cluster.json",
    "aws-opsworks-instance.json",
    "aws-config-configurationaggregator.json",
    "aws-imagebuilder-imagepipeline.json",
    "aws-elasticloadbalancingv2-listenercertificate.json",
    "aws-cloudformation-moduleversion.json",
    "aws-fsx-storagevirtualmachine.json",
    "aws-greengrass-connectordefinitionversion.json",
    "aws-synthetics-canary.json",
    "aws-sns-subscription.json",
    "aws-ec2-natgateway.json",
    "aws-transfer-workflow.json",
    "aws-appconfig-deploymentstrategy.json",
    "aws-glue-devendpoint.json",
    "aws-elasticache-usergroup.json",
    "aws-iot-thinggroup.json",
    "aws-imagebuilder-imagerecipe.json",
    "aws-opsworks-elasticloadbalancerattachment.json",
    "aws-s3objectlambda-accesspointpolicy.json",
    "aws-elasticache-replicationgroup.json",
    "aws-cassandra-table.json",
    "aws-cloudformation-moduledefaultversion.json",
    "aws-sso-permissionset.json",
    "aws-glue-job.json",
    "aws-servicecatalog-cloudformationprovisionedproduct.json",
    "aws-glue-table.json",
    "aws-lambda-function.json",
    "aws-backup-backupselection.json",
    "aws-datasync-locationfsxlustre.json",
    "aws-ec2-vpcgatewayattachment.json",
    "aws-cloudtrail-trail.json",
    "aws-ec2-gatewayroutetableassociation.json",
    "aws-wafv2-ipset.json",
    "aws-ssm-document.json",
    "aws-dms-endpoint.json",
    "aws-apigateway-apikey.json",
    "aws-kinesisanalyticsv2-application.json",
    "aws-lambda-alias.json",
    "aws-waf-ipset.json",
    "aws-ec2-transitgatewaymulticastdomainassociation.json",
    "aws-s3outposts-endpoint.json",
    "aws-waf-sizeconstraintset.json",
    "aws-ec2-transitgatewayroutetableassociation.json",
    "aws-appconfig-environment.json",
    "aws-imagebuilder-image.json",
    "aws-elasticache-securitygroupingress.json",
    "aws-cloudwatch-dashboard.json",
    "aws-cloudwatch-alarm.json",
    "aws-iot-thingtype.json",
    "aws-guardduty-member.json",
    "aws-cloudformation-customresource.json",
    "aws-kinesisanalytics-applicationoutput.json",
    "aws-wafv2-rulegroup.json",
    "aws-elasticache-parametergroup.json",
    "aws-networkfirewall-loggingconfiguration.json",
    "aws-glue-classifier.json",
    "aws-codedeploy-deploymentgroup.json",
    "aws-cloudformation-stackset.json",
    "aws-ec2-route.json",
    "aws-fis-experimenttemplate.json",
    "aws-codecommit-repository.json",
    "aws-cloudformation-hookversion.json",
    "aws-iot-resourcespecificlogging.json",
    "aws-servicecatalog-launchtemplateconstraint.json",
    "aws-wafv2-loggingconfiguration.json",
    "aws-dynamodb-globaltable.json",
    "aws-backup-backupplan.json",
    "aws-imagebuilder-distributionconfiguration.json",
    "aws-identitystore-group.json",
    "aws-ram-permission.json",
    "aws-datasync-task.json",
    "aws-ecs-taskdefinition.json",
    "aws-appstream-appblock.json",
    "aws-identitystore-groupmembership.json",
    "aws-ec2-spotfleet.json",
    "aws-glue-schemaversion.json",
    "aws-iot-policyprincipalattachment.json",
    "aws-msk-batchscramsecret.json",
    "aws-dms-certificate.json",
    "aws-s3-bucket.json",
    "aws-guardduty-ipset.json",
    "aws-servicediscovery-httpnamespace.json",
    "aws-cloudwatch-insightrule.json",
    "aws-apigateway-usageplan.json",
    "aws-batch-schedulingpolicy.json",
    "aws-iot-authorizer.json",
    "aws-iot-jobtemplate.json",
    "aws-athena-workgroup.json",
    "aws-detective-graph.json",
    "aws-servicecatalog-portfolioshare.json",
    "aws-networkmanager-customergatewayassociation.json",
    "aws-iam-servercertificate.json",
    "aws-iot-securityprofile.json",
    "aws-events-eventbus.json",
    "aws-ssm-maintenancewindowtarget.json",
    "aws-backupgateway-hypervisor.json",
    "aws-iam-policy.json",
    "aws-rds-dbsecuritygroupingress.json",
    "aws-ec2-transitgatewaymulticastgroupmember.json",
    "aws-ec2-volumeattachment.json",
    "aws-glue-securityconfiguration.json",
    "aws-applicationinsights-application.json",
    "aws-ecs-clustercapacityproviderassociations.json",
    "aws-appconfig-configurationprofile.json",
    "aws-route53resolver-firewallrulegroup.json",
    "aws-msk-configuration.json",
    "aws-ssm-maintenancewindowtask.json",
    "aws-ec2-transitgatewaymulticastdomain.json",
    "aws-eks-cluster.json",
    "aws-codebuild-project.json",
    "aws-logs-querydefinition.json",
    "aws-iot-billinggroup.json",
    "aws-appstream-application.json",
    "aws-datasync-locationnfs.json",
    "aws-kinesisanalyticsv2-applicationoutput.json",
    "aws-greengrass-coredefinitionversion.json",
    "aws-certificatemanager-certificate.json",
    "aws-glue-schemaversionmetadata.json",
    "aws-sdb-domain.json",
    "aws-servicecatalog-serviceactionassociation.json",
    "aws-imagebuilder-containerrecipe.json",
    "aws-efs-accesspoint.json",
    "aws-redshift-clustersecuritygroupingress.json",
    "aws-servicecatalogappregistry-attributegroupassociation.json",
    "aws-elasticloadbalancingv2-loadbalancer.json",
    "aws-opensearchservice-domain.json",
    "aws-servicediscovery-instance.json",
    "aws-elasticsearch-domain.json",
    "aws-servicecatalog-stacksetconstraint.json",
    "aws-ec2-networkinterfacepermission.json",
    "aws-servicecatalog-tagoption.json",
    "aws-servicediscovery-privatednsnamespace.json",
    "aws-servicecatalog-launchroleconstraint.json",
    "aws-iot-rolealias.json",
    "aws-secretsmanager-resourcepolicy.json",
    "aws-cloudformation-hookdefaultversion.json",
    "aws-config-configrule.json",
    "aws-ec2-clientvpnroute.json",
    "aws-ecs-taskset.json",
    "aws-acmpca-certificateauthorityactivation.json",
    "aws-guardduty-threatintelset.json",
    "aws-msk-vpcconnection.json",
    "aws-dms-replicationsubnetgroup.json",
    "aws-s3outposts-bucket.json",
    "aws-route53-recordsetgroup.json",
    "aws-appstream-applicationentitlementassociation.json",
    "aws-ec2-localgatewayroute.json",
    "aws-opsworks-app.json",
    "aws-batch-jobdefinition.json",
    "aws-iam-samlprovider.json",
    "aws-ec2-networkinterfaceattachment.json",
    "aws-ec2-transitgatewayattachment.json",
    "aws-networkmanager-globalnetwork.json",
    "aws-servicecatalogappregistry-application.json",
    "aws-networkmanager-site.json",
    "aws-neptune-dbcluster.json",
    "aws-backup-backupvault.json",
    "aws-waf-bytematchset.json",
    "aws-dms-replicationtask.json",
    "aws-datasync-locationsmb.json",
    "aws-redshift-clusterparametergroup.json",
    "aws-glue-trigger.json",
    "aws-sns-topicpolicy.json",
    "aws-elasticache-globalreplicationgroup.json",
    "aws-networkfirewall-rulegroup.json",
    "aws-kms-key.json",
    "aws-route53resolver-resolverdnssecconfig.json",
    "aws-route53resolver-firewallrulegroupassociation.json",
    "aws-route53resolver-resolverqueryloggingconfig.json",
    "aws-ec2-subnet.json",
    "aws-s3objectlambda-accesspoint.json",
    "aws-waf-rule.json",
    "aws-sqs-queuepolicy.json",
    "aws-wafv2-webacl.json",
    "aws-ec2-transitgatewayconnect.json",
    "aws-ec2-securitygroup.json",
    "aws-opsworks-volume.json",
    "aws-iam-usertogroupaddition.json",
    "aws-events-rule.json",
    "aws-ec2-vpngatewayroutepropagation.json",
    "aws-ssm-patchbaseline.json",
    "aws-servicediscovery-service.json",
    "aws-waf-webacl.json",
    "aws-iam-user.json",
    "aws-emr-instancegroupconfig.json",
    "aws-synthetics-group.json",
    "aws-ec2-localgatewayroutetablevirtualinterfacegroupassociation.json",
    "aws-s3-bucketpolicy.json",
    "aws-iot-custommetric.json",
    "aws-redshift-cluster.json",
    "aws-codebuild-sourcecredential.json",
    "aws-emr-instancefleetconfig.json",
    "aws-emr-cluster.json",
    "aws-codepipeline-webhook.json",
    "aws-apigatewayv2-domainname.json",
    "aws-servicecatalog-resourceupdateconstraint.json",
    "aws-transfer-agreement.json",
    "aws-networkfirewall-firewall.json",
    "aws-kms-replicakey.json",
    "aws-redshift-clustersecuritygroup.json",
    "aws-glue-mltransform.json",
    "aws-appconfig-hostedconfigurationversion.json",
    "aws-datasync-locationefs.json",
    "aws-ec2-localgatewayroutetable.json",
    "aws-applicationautoscaling-scalingpolicy.json",
    "aws-cloudformation-macro.json",
    "aws-lambda-layerversionpermission.json",
    "aws-elasticache-user.json",
    "aws-logs-subscriptionfilter.json",
    "aws-dms-eventsubscription.json",
    "aws-datasync-locations3.json",
    "aws-fsx-datarepositoryassociation.json",
    "aws-route53resolver-resolverqueryloggingconfigassociation.json",
    "aws-lambda-eventinvokeconfig.json",
    "aws-lambda-layerversion.json",
    "aws-rds-optiongroup.json",
    "aws-opsworks-userprofile.json",
    "aws-glue-schema.json",
    "aws-iot-policy.json",
    "aws-ec2-transitgatewayroute.json",
    "aws-ssm-maintenancewindow.json",
    "aws-ec2-ipamresourcediscovery.json",
    "aws-greengrassv2-componentversion.json",
    "aws-imagebuilder-infrastructureconfiguration.json",
    "aws-iot-logging.json",
    "aws-cloudformation-waitcondition.json",
    "aws-route53resolver-resolverendpoint.json",
    "aws-networkmanager-link.json",
    "aws-sso-instanceaccesscontrolattributeconfiguration.json",
    "aws-cloudwatch-anomalydetector.json",
    "aws-servicecatalog-serviceaction.json",
    "aws-appstream-entitlement.json",
    "aws-iot-mitigationaction.json",
    "aws-secretsmanager-rotationschedule.json",
    "aws-lambda-permission.json",
    "aws-networkfirewall-firewallpolicy.json",
    "aws-eks-identityproviderconfig.json",
    "aws-ec2-ipamresourcediscoveryassociation.json",
    "aws-servicecatalogappregistry-attributegroup.json",
    "aws-ec2-clientvpntargetnetworkassociation.json",
    "aws-ec2-egressonlyinternetgateway.json",
    "aws-ec2-vpccidrblock.json",
    "aws-iam-virtualmfadevice.json",
    "aws-acmpca-certificateauthority.json",
    "aws-detective-memberinvitation.json",
    "aws-ec2-ipamscope.json",
    "aws-rds-eventsubscription.json",
    "aws-datasync-agent.json",
    "aws-iot-dimension.json",
    "aws-ec2-trafficmirrorfilterrule.json",
    "aws-ecr-repository.json",
    "aws-iot-fleetmetric.json",
    "aws-appconfig-extension.json",
    "aws-glue-registry.json",
    "aws-ec2-keypair.json",
    "aws-fsx-filesystem.json",
    "aws-appstream-applicationfleetassociation.json",
    "aws-ec2-eipassociation.json",
    "aws-iot-thingprincipalattachment.json",
    "aws-dlm-lifecyclepolicy.json",
    "aws-ec2-capacityreservation.json",
    "aws-elasticloadbalancing-loadbalancer.json",
    "aws-transfer-user.json",
    "aws-ec2-trafficmirrortarget.json",
    "aws-stepfunctions-statemachine.json",
    "aws-waf-xssmatchset.json",
    "aws-appstream-directoryconfig.json",
    "aws-fsx-snapshot.json",
    "aws-config-remediationconfiguration.json",
    "aws-athena-datacatalog.json",
    "aws-glue-workflow.json",
    "aws-iot-accountauditconfiguration.json",
    "aws-ec2-prefixlist.json",
    "aws-ec2-instance.json",
    "aws-networkmanager-device.json",
    "aws-ec2-subnetcidrblock.json",
    "aws-waf-sqlinjectionmatchset.json",
    "aws-amazonmq-broker.json",
    "aws-emr-step.json",
    "aws-ssm-association.json",
    "aws-ec2-clientvpnendpoint.json",
    "aws-msk-clusterpolicy.json",
    "aws-kms-alias.json",
    "aws-transfer-connector.json",
    "aws-licensemanager-grant.json",
    "aws-wafv2-webaclassociation.json",
    "aws-codebuild-reportgroup.json",
    "aws-ec2-enclavecertificateiamroleassociation.json",
    "aws-fsx-volume.json",
    "aws-acmpca-certificate.json",
    "aws-ec2-ipamallocation.json",
    "aws-workspaces-workspace.json",
    "aws-directoryservice-microsoftad.json",
    "aws-datasync-locationobjectstorage.json",
    "aws-ecs-capacityprovider.json",
    "aws-elasticache-cachecluster.json",
    "aws-logs-destination.json",
    "aws-eks-nodegroup.json",
    "aws-ec2-securitygroupingress.json",
    "aws-guardduty-detector.json",
    "aws-iot-provisioningtemplate.json",
    "aws-batch-computeenvironment.json",
    "aws-events-eventbuspolicy.json",
    "aws-ec2-trafficmirrorfilter.json",
    "aws-greengrassv2-deployment.json",
    "aws-redshift-scheduledaction.json",
    "aws-rds-dbsecuritygroup.json",
    "aws-apigatewayv2-routeresponse.json",
    "aws-ssm-parameter.json",
    "aws-apigatewayv2-apigatewaymanagedoverrides.json",
    "aws-config-deliverychannel.json",
    "aws-certificatemanager-account.json",
    "aws-iam-oidcprovider.json",
    "aws-servicecatalogappregistry-resourceassociation.json",
    "aws-cloudformation-stack.json",
    "aws-resourcegroups-group.json",
    "aws-ec2-ipam.json",
    "aws-ec2-transitgatewaypeeringattachment.json",
    "aws-iam-accesskey.json",
    "aws-rds-dbsubnetgroup.json",
    "aws-amazonmq-configuration.json",
    "aws-appconfig-deployment.json",
    "aws-accessanalyzer-analyzer.json",
    "aws-ec2-ec2fleet.json",
    "aws-greengrass-resourcedefinition.json",
    "aws-dms-replicationinstance.json",
    "aws-servicecatalog-cloudformationproduct.json",
    "aws-iam-managedpolicy.json",
    "aws-datasync-locationfsxontap.json",
    "aws-networkmanager-linkassociation.json",
    "aws-lambda-version.json",
    "aws-ec2-dhcpoptions.json",
    "aws-ec2-ipampool.json",
    "aws-kinesis-streamconsumer.json",
    "aws-iam-servicelinkedrole.json",
    "aws-cloudformation-hooktypeconfig.json",
    "aws-licensemanager-license.json",
    "aws-iot-certificate.json",
    "aws-greengrass-resourcedefinitionversion.json",
    "aws-apigatewayv2-stage.json",
    "aws-rds-dbparametergroup.json",
    "aws-securityhub-hub.json",
    "aws-s3-accesspoint.json",
    "aws-greengrass-groupversion.json",
    "aws-ec2-trafficmirrorsession.json",
    "aws-s3outposts-bucketpolicy.json",
    "aws-batch-jobqueue.json",
    "aws-redshift-eventsubscription.json",
    "aws-cloudformation-waitconditionhandle.json",
    "aws-eks-addon.json",
]
