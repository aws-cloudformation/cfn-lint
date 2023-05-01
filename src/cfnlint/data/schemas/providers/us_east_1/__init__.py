# pylint: disable=too-many-lines
types = [
    "AWS::CDK::Metadata",
    "AWS::ApiGatewayV2::Integration",
    "AWS::Pinpoint::App",
    "AWS::Connect::UserHierarchyGroup",
    "AWS::ApiGatewayV2::ApiMapping",
    "AWS::CE::AnomalySubscription",
    "AWS::SSO::Assignment",
    "AWS::Glue::Partition",
    "AWS::EC2::TransitGatewayRouteTablePropagation",
    "AWS::SSM::ResourcePolicy",
    "AWS::ApiGateway::BasePathMapping",
    "AWS::WAFRegional::GeoMatchSet",
    "AWS::RoboMaker::Robot",
    "AWS::GuardDuty::Filter",
    "AWS::ECS::Service",
    "AWS::ServiceCatalog::PortfolioPrincipalAssociation",
    "AWS::RAM::ResourceShare",
    "AWS::MemoryDB::Cluster",
    "AWS::DynamoDB::Table",
    "AWS::AmazonMQ::ConfigurationAssociation",
    "AWS::WAFRegional::IPSet",
    "AWS::RedshiftServerless::Namespace",
    "AWS::AppRunner::ObservabilityConfiguration",
    "AWS::EC2::SecurityGroupEgress",
    "AWS::EC2::LocalGatewayRouteTableVPCAssociation",
    "AWS::Config::OrganizationConfigRule",
    "AWS::Route53RecoveryReadiness::Cell",
    "AWS::NetworkManager::TransitGatewayPeering",
    "AWS::Config::ConfigurationRecorder",
    "AWS::EC2::NetworkPerformanceMetricSubscription",
    "AWS::MediaLive::Channel",
    "AWS::Greengrass::DeviceDefinition",
    "AWS::CloudFront::ContinuousDeploymentPolicy",
    "AWS::QuickSight::Analysis",
    "AWS::Kendra::Faq",
    "AWS::ECR::ReplicationConfiguration",
    "AWS::AppConfig::ExtensionAssociation",
    "AWS::VpcLattice::Service",
    "AWS::S3Outposts::AccessPoint",
    "AWS::MediaPackage::OriginEndpoint",
    "AWS::EC2::IPAMPoolCidr",
    "AWS::IoT::TopicRuleDestination",
    "AWS::Amplify::Branch",
    "AWS::Redshift::ClusterSubnetGroup",
    "AWS::RDS::DBInstance",
    "AWS::EC2::VPCDHCPOptionsAssociation",
    "AWS::Lightsail::Bucket",
    "AWS::ApiGateway::Model",
    "AWS::ApiGatewayV2::IntegrationResponse",
    "AWS::IoTEvents::Input",
    "AWS::EC2::NetworkAcl",
    "AWS::Lambda::EventSourceMapping",
    "AWS::Budgets::BudgetsAction",
    "AWS::Logs::ResourcePolicy",
    "AWS::Lex::BotVersion",
    "AWS::ServiceCatalog::LaunchNotificationConstraint",
    "AWS::OpenSearchServerless::VpcEndpoint",
    "AWS::QuickSight::DataSource",
    "AWS::IoT::CACertificate",
    "AWS::EC2::NetworkAclEntry",
    "AWS::RoboMaker::SimulationApplicationVersion",
    "AWS::EC2::NetworkInsightsAccessScopeAnalysis",
    "AWS::Transfer::Certificate",
    "AWS::Pinpoint::GCMChannel",
    "AWS::Connect::Instance",
    "AWS::ApiGateway::DocumentationPart",
    "AWS::CloudWatch::CompositeAlarm",
    "AWS::Route53Resolver::FirewallDomainList",
    "AWS::Redshift::EndpointAccess",
    "AWS::AppConfig::Application",
    "AWS::IVSChat::LoggingConfiguration",
    "AWS::IoTWireless::WirelessGateway",
    "AWS::OpsWorks::Stack",
    "AWS::Lambda::Url",
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
    "AWS::FMS::ResourceSet",
    "AWS::Cognito::UserPoolDomain",
    "AWS::AutoScaling::AutoScalingGroup",
    "AWS::WAFv2::RegexPatternSet",
    "AWS::EKS::FargateProfile",
    "AWS::Route53::DNSSEC",
    "AWS::Redshift::EndpointAuthorization",
    "AWS::EC2::TransitGatewayRouteTable",
    "AWS::ControlTower::EnabledControl",
    "AWS::NetworkManager::ConnectAttachment",
    "AWS::Lightsail::Container",
    "AWS::Macie::CustomDataIdentifier",
    "AWS::Cognito::IdentityPoolRoleAttachment",
    "AWS::PinpointEmail::ConfigurationSetEventDestination",
    "AWS::Route53::RecordSet",
    "AWS::MediaStore::Container",
    "AWS::IoTAnalytics::Datastore",
    "AWS::AmplifyUIBuilder::Form",
    "AWS::IVS::StreamKey",
    "AWS::ElastiCache::SecurityGroup",
    "AWS::Backup::Framework",
    "AWS::AppFlow::ConnectorProfile",
    "AWS::Pinpoint::EmailChannel",
    "AWS::Rekognition::Collection",
    "AWS::OpsWorks::Layer",
    "AWS::CloudTrail::EventDataStore",
    "AWS::KinesisFirehose::DeliveryStream",
    "AWS::EC2::NetworkInsightsAccessScope",
    "AWS::Cognito::UserPoolUserToGroupAttachment",
    "AWS::MediaConvert::Queue",
    "AWS::SageMaker::CodeRepository",
    "AWS::ImageBuilder::Component",
    "AWS::SES::ConfigurationSetEventDestination",
    "AWS::MediaPackage::PackagingConfiguration",
    "AWS::MediaConnect::FlowEntitlement",
    "AWS::OpenSearchServerless::AccessPolicy",
    "AWS::IoTAnalytics::Channel",
    "AWS::IoTWireless::MulticastGroup",
    "AWS::Glue::Connection",
    "AWS::AppMesh::Route",
    "AWS::CodeArtifact::Repository",
    "AWS::IAM::Group",
    "AWS::Macie::FindingsFilter",
    "AWS::Organizations::ResourcePolicy",
    "AWS::WAFRegional::WebACLAssociation",
    "AWS::EC2::TransitGatewayMulticastGroupSource",
    "AWS::Pinpoint::ApplicationSettings",
    "AWS::Lex::Bot",
    "AWS::Transfer::Profile",
    "AWS::Omics::Workflow",
    "AWS::DataBrew::Recipe",
    "AWS::GameLift::Alias",
    "AWS::AppSync::DomainName",
    "AWS::Pinpoint::PushTemplate",
    "AWS::ApiGateway::UsagePlanKey",
    "AWS::FMS::Policy",
    "AWS::Greengrass::FunctionDefinition",
    "AWS::Lightsail::StaticIp",
    "AWS::CloudFront::RealtimeLogConfig",
    "AWS::SageMaker::Pipeline",
    "AWS::CloudTrail::Channel",
    "AWS::DocDB::DBInstance",
    "AWS::LakeFormation::DataCellsFilter",
    "AWS::DataSync::LocationHDFS",
    "AWS::IoTSiteWise::Portal",
    "AWS::Events::Archive",
    "AWS::MSK::Cluster",
    "AWS::Route53RecoveryControl::Cluster",
    "AWS::EC2::VPCEndpointConnectionNotification",
    "AWS::CodePipeline::Pipeline",
    "AWS::OpsWorks::Instance",
    "AWS::Config::ConfigurationAggregator",
    "AWS::ImageBuilder::ImagePipeline",
    "AWS::ElasticLoadBalancingV2::ListenerCertificate",
    "AWS::CloudFormation::ModuleVersion",
    "AWS::Cloud9::EnvironmentEC2",
    "AWS::Rekognition::StreamProcessor",
    "AWS::Location::PlaceIndex",
    "AWS::Route53Resolver::ResolverRuleAssociation",
    "AWS::FSx::StorageVirtualMachine",
    "AWS::Greengrass::ConnectorDefinitionVersion",
    "AWS::Synthetics::Canary",
    "AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption",
    "AWS::SNS::Subscription",
    "AWS::AppMesh::Mesh",
    "AWS::EC2::NatGateway",
    "AWS::NimbleStudio::StreamingImage",
    "AWS::Greengrass::ConnectorDefinition",
    "AWS::InternetMonitor::Monitor",
    "AWS::Transfer::Workflow",
    "AWS::QLDB::Ledger",
    "AWS::AppConfig::DeploymentStrategy",
    "AWS::Glue::DevEndpoint",
    "AWS::SageMaker::ModelPackage",
    "AWS::CustomerProfiles::Integration",
    "AWS::WorkSpaces::ConnectionAlias",
    "AWS::WAFRegional::SizeConstraintSet",
    "AWS::EventSchemas::Discoverer",
    "AWS::NetworkManager::ConnectPeer",
    "AWS::ElastiCache::UserGroup",
    "AWS::ImageBuilder::ImageRecipe",
    "AWS::ApiGateway::RestApi",
    "AWS::OpsWorks::ElasticLoadBalancerAttachment",
    "AWS::MediaConvert::JobTemplate",
    "AWS::AppMesh::VirtualService",
    "AWS::S3ObjectLambda::AccessPointPolicy",
    "AWS::CodeGuruReviewer::RepositoryAssociation",
    "AWS::RoboMaker::SimulationApplication",
    "AWS::NetworkManager::TransitGatewayRegistration",
    "AWS::Amplify::App",
    "AWS::InspectorV2::Filter",
    "AWS::ElastiCache::ReplicationGroup",
    "AWS::Cassandra::Table",
    "AWS::Cognito::UserPoolResourceServer",
    "AWS::RDS::GlobalCluster",
    "AWS::SageMaker::Device",
    "AWS::SupportApp::AccountAlias",
    "AWS::CloudFormation::ModuleDefaultVersion",
    "AWS::CE::CostCategory",
    "AWS::SSO::PermissionSet",
    "AWS::Glue::Job",
    "AWS::ServiceCatalog::CloudFormationProvisionedProduct",
    "AWS::Route53::HostedZone",
    "AWS::ResourceExplorer2::Index",
    "AWS::Glue::Table",
    "AWS::WAFRegional::WebACL",
    "AWS::Logs::MetricFilter",
    "AWS::Lambda::Function",
    "AWS::SNS::Topic",
    "AWS::Backup::BackupSelection",
    "AWS::DataSync::LocationFSxLustre",
    "AWS::SageMaker::App",
    "AWS::EC2::VPCGatewayAttachment",
    "AWS::CloudTrail::Trail",
    "AWS::EC2::VPNConnectionRoute",
    "AWS::KafkaConnect::Connector",
    "AWS::GameLift::GameServerGroup",
    "AWS::AppStream::Stack",
    "AWS::EC2::InternetGateway",
    "AWS::EC2::GatewayRouteTableAssociation",
    "AWS::VpcLattice::Listener",
    "AWS::WAFv2::IPSet",
    "AWS::Greengrass::SubscriptionDefinition",
    "AWS::Greengrass::Group",
    "AWS::SSM::Document",
    "AWS::IAM::Role",
    "AWS::Events::ApiDestination",
    "AWS::DMS::Endpoint",
    "AWS::IoTSiteWise::Project",
    "AWS::CloudFront::CloudFrontOriginAccessIdentity",
    "AWS::CodeStarNotifications::NotificationRule",
    "AWS::SageMaker::EndpointConfig",
    "AWS::AppMesh::GatewayRoute",
    "AWS::ApiGateway::ApiKey",
    "AWS::GameLift::Location",
    "AWS::NetworkManager::TransitGatewayRouteTableAttachment",
    "AWS::AutoScaling::LaunchConfiguration",
    "AWS::ApiGateway::ClientCertificate",
    "AWS::KinesisAnalyticsV2::Application",
    "AWS::Lambda::Alias",
    "AWS::WAF::IPSet",
    "AWS::IoTTwinMaker::Workspace",
    "AWS::VpcLattice::ServiceNetworkServiceAssociation",
    "AWS::EC2::TransitGatewayMulticastDomainAssociation",
    "AWS::S3Outposts::Endpoint",
    "AWS::WAF::SizeConstraintSet",
    "AWS::EC2::TransitGatewayRouteTableAssociation",
    "AWS::AppConfig::Environment",
    "AWS::ImageBuilder::Image",
    "AWS::ElastiCache::SecurityGroupIngress",
    "AWS::WAFRegional::XssMatchSet",
    "AWS::VpcLattice::Rule",
    "AWS::RDS::DBProxyTargetGroup",
    "AWS::CloudWatch::Dashboard",
    "AWS::CloudWatch::Alarm",
    "AWS::FraudDetector::Variable",
    "AWS::EC2::CarrierGateway",
    "AWS::GuardDuty::Member",
    "AWS::GroundStation::MissionProfile",
    "AWS::CloudFormation::CustomResource",
    "AWS::RefactorSpaces::Route",
    "AWS::NimbleStudio::LaunchProfile",
    "AWS::KinesisAnalytics::ApplicationOutput",
    "AWS::Wisdom::Assistant",
    "AWS::WAFv2::RuleGroup",
    "AWS::SageMaker::ModelPackageGroup",
    "AWS::Evidently::Launch",
    "AWS::SES::ConfigurationSet",
    "AWS::ElastiCache::ParameterGroup",
    "AWS::NetworkFirewall::LoggingConfiguration",
    "AWS::Route53RecoveryControl::RoutingControl",
    "AWS::Glue::Classifier",
    "AWS::CodeDeploy::DeploymentGroup",
    "AWS::AmplifyUIBuilder::Component",
    "AWS::Location::TrackerConsumer",
    "AWS::VpcLattice::ServiceNetwork",
    "AWS::SageMaker::InferenceExperiment",
    "AWS::CloudFormation::StackSet",
    "AWS::EC2::Route",
    "AWS::Wisdom::AssistantAssociation",
    "AWS::Kendra::Index",
    "AWS::FIS::ExperimentTemplate",
    "AWS::CodeCommit::Repository",
    "AWS::CloudFormation::HookVersion",
    "AWS::RolesAnywhere::Profile",
    "AWS::RefactorSpaces::Environment",
    "AWS::XRay::ResourcePolicy",
    "AWS::IoT::ResourceSpecificLogging",
    "AWS::ServiceCatalog::LaunchTemplateConstraint",
    "AWS::DevOpsGuru::ResourceCollection",
    "AWS::HealthLake::FHIRDatastore",
    "AWS::WAFv2::LoggingConfiguration",
    "AWS::DynamoDB::GlobalTable",
    "Alexa::ASK::Skill",
    "AWS::Backup::BackupPlan",
    "AWS::Pinpoint::EventStream",
    "AWS::ImageBuilder::DistributionConfiguration",
    "AWS::LakeFormation::Permissions",
    "AWS::ResourceExplorer2::View",
    "AWS::Glue::DataCatalogEncryptionSettings",
    "AWS::CloudFront::PublicKey",
    "AWS::Evidently::Project",
    "AWS::Lex::BotAlias",
    "AWS::IdentityStore::Group",
    "AWS::RAM::Permission",
    "AWS::DataSync::Task",
    "AWS::ECS::TaskDefinition",
    "AWS::SageMaker::Model",
    "AWS::QuickSight::RefreshSchedule",
    "AWS::MemoryDB::ParameterGroup",
    "AWS::RoboMaker::RobotApplicationVersion",
    "AWS::AppStream::AppBlock",
    "AWS::IoTWireless::ServiceProfile",
    "AWS::SES::VdmAttributes",
    "AWS::IdentityStore::GroupMembership",
    "AWS::AppSync::FunctionConfiguration",
    "AWS::EC2::SpotFleet",
    "AWS::Omics::AnnotationStore",
    "AWS::VpcLattice::AuthPolicy",
    "AWS::Glue::SchemaVersion",
    "AWS::SageMaker::Space",
    "AWS::IoT::PolicyPrincipalAttachment",
    "AWS::Timestream::ScheduledQuery",
    "AWS::FraudDetector::List",
    "AWS::FMS::NotificationChannel",
    "AWS::MSK::BatchScramSecret",
    "AWS::Connect::HoursOfOperation",
    "AWS::DMS::Certificate",
    "AWS::IoTFleetWise::ModelManifest",
    "AWS::S3::Bucket",
    "AWS::GuardDuty::IPSet",
    "AWS::Route53RecoveryControl::SafetyRule",
    "AWS::ServiceDiscovery::HttpNamespace",
    "AWS::EMR::SecurityConfiguration",
    "AWS::CloudWatch::InsightRule",
    "AWS::ApiGateway::UsagePlan",
    "AWS::AppIntegrations::EventIntegration",
    "AWS::Batch::SchedulingPolicy",
    "AWS::IoT::Authorizer",
    "AWS::ApiGatewayV2::VpcLink",
    "AWS::IoT::JobTemplate",
    "AWS::IoTFleetWise::SignalCatalog",
    "AWS::ServiceCatalog::PortfolioProductAssociation",
    "AWS::DataBrew::Project",
    "AWS::VpcLattice::TargetGroup",
    "AWS::Athena::WorkGroup",
    "AWS::SageMaker::ImageVersion",
    "AWS::ApiGatewayV2::Api",
    "AWS::Detective::Graph",
    "AWS::CUR::ReportDefinition",
    "AWS::Location::RouteCalculator",
    "AWS::ServiceCatalog::PortfolioShare",
    "AWS::ApiGateway::VpcLink",
    "AWS::Connect::IntegrationAssociation",
    "AWS::NetworkManager::CustomerGatewayAssociation",
    "AWS::IAM::ServerCertificate",
    "AWS::CodeStarConnections::Connection",
    "AWS::IoT::SecurityProfile",
    "AWS::Events::EventBus",
    "AWS::AutoScalingPlans::ScalingPlan",
    "AWS::SSM::MaintenanceWindowTarget",
    "AWS::VoiceID::Domain",
    "AWS::ApiGateway::Authorizer",
    "AWS::AppStream::ImageBuilder",
    "AWS::BillingConductor::PricingRule",
    "AWS::Lightsail::Disk",
    "AWS::IAM::Policy",
    "AWS::DataBrew::Schedule",
    "AWS::AppRunner::Service",
    "AWS::Connect::ApprovedOrigin",
    "AWS::SES::ContactList",
    "AWS::Connect::SecurityKey",
    "AWS::CloudFormation::Publisher",
    "AWS::RDS::DBSecurityGroupIngress",
    "AWS::IoTEvents::DetectorModel",
    "AWS::AppStream::StackFleetAssociation",
    "AWS::SSMContacts::Contact",
    "AWS::EC2::TransitGatewayMulticastGroupMember",
    "AWS::RoboMaker::Fleet",
    "AWS::EC2::VolumeAttachment",
    "AWS::Glue::SecurityConfiguration",
    "AWS::OpenSearchServerless::Collection",
    "AWS::DataBrew::Ruleset",
    "AWS::GameLift::MatchmakingConfiguration",
    "AWS::ApplicationInsights::Application",
    "AWS::ECS::ClusterCapacityProviderAssociations",
    "AWS::AppConfig::ConfigurationProfile",
    "AWS::ManagedBlockchain::Node",
    "AWS::Route53Resolver::FirewallRuleGroup",
    "AWS::DocDBElastic::Cluster",
    "AWS::MSK::Configuration",
    "AWS::EC2::TransitGateway",
    "AWS::Cognito::UserPoolGroup",
    "AWS::EC2::VPCEndpointServicePermissions",
    "AWS::VpcLattice::ResourcePolicy",
    "AWS::SSM::MaintenanceWindowTask",
    "AWS::EC2::TransitGatewayMulticastDomain",
    "AWS::EKS::Cluster",
    "AWS::CodeBuild::Project",
    "AWS::EFS::FileSystem",
    "AWS::Pinpoint::APNSVoipSandboxChannel",
    "AWS::Config::OrganizationConformancePack",
    "AWS::Connect::QuickConnect",
    "AWS::Logs::QueryDefinition",
    "AWS::IAM::InstanceProfile",
    "AWS::IoTFleetWise::DecoderManifest",
    "AWS::AppStream::Application",
    "AWS::DataSync::LocationNFS",
    "AWS::Amplify::Domain",
    "AWS::KinesisAnalyticsV2::ApplicationOutput",
    "AWS::IVS::RecordingConfiguration",
    "AWS::MediaLive::InputSecurityGroup",
    "AWS::SageMaker::Domain",
    "AWS::Greengrass::CoreDefinitionVersion",
    "AWS::CertificateManager::Certificate",
    "AWS::Glue::SchemaVersionMetadata",
    "AWS::SDB::Domain",
    "AWS::EC2::SubnetRouteTableAssociation",
    "AWS::ServiceCatalog::ServiceActionAssociation",
    "AWS::Cognito::UserPoolUICustomizationAttachment",
    "AWS::SageMaker::NotebookInstanceLifecycleConfig",
    "AWS::ImageBuilder::ContainerRecipe",
    "AWS::Connect::Rule",
    "AWS::EFS::AccessPoint",
    "AWS::Omics::ReferenceStore",
    "AWS::Redshift::ClusterSecurityGroupIngress",
    "AWS::ServiceCatalogAppRegistry::AttributeGroupAssociation",
    "AWS::ElasticLoadBalancingV2::LoadBalancer",
    "AWS::OpenSearchService::Domain",
    "AWS::Timestream::Database",
    "AWS::ServiceDiscovery::Instance",
    "AWS::Elasticsearch::Domain",
    "AWS::Personalize::Solution",
    "AWS::KinesisAnalytics::Application",
    "AWS::ApiGatewayV2::Deployment",
    "AWS::ServiceCatalog::StackSetConstraint",
    "AWS::IVS::Channel",
    "AWS::RefactorSpaces::Service",
    "AWS::MemoryDB::User",
    "AWS::EC2::NetworkInterfacePermission",
    "AWS::ServiceCatalog::TagOption",
    "AWS::ServiceDiscovery::PrivateDnsNamespace",
    "AWS::ServiceCatalog::LaunchRoleConstraint",
    "AWS::IoT::RoleAlias",
    "AWS::SageMaker::ModelBiasJobDefinition",
    "AWS::SecretsManager::ResourcePolicy",
    "AWS::CloudFormation::HookDefaultVersion",
    "AWS::Config::ConfigRule",
    "AWS::EC2::NetworkInsightsAnalysis",
    "AWS::EC2::ClientVpnRoute",
    "AWS::ECS::TaskSet",
    "AWS::Omics::VariantStore",
    "AWS::AppSync::ApiKey",
    "AWS::CloudFormation::TypeActivation",
    "AWS::GroundStation::DataflowEndpointGroup",
    "AWS::Location::Map",
    "AWS::ACMPCA::CertificateAuthorityActivation",
    "AWS::MSK::ServerlessCluster",
    "AWS::GuardDuty::ThreatIntelSet",
    "AWS::IoTFleetWise::Campaign",
    "AWS::WAFRegional::RateBasedRule",
    "AWS::KinesisVideo::SignalingChannel",
    "AWS::RedshiftServerless::Workgroup",
    "AWS::Macie::AllowList",
    "AWS::EC2::VPC",
    "AWS::MSK::VpcConnection",
    "AWS::DAX::Cluster",
    "AWS::IoTSiteWise::Asset",
    "AWS::Logs::LogStream",
    "AWS::DMS::ReplicationSubnetGroup",
    "AWS::APS::RuleGroupsNamespace",
    "AWS::S3Outposts::Bucket",
    "AWS::Route53RecoveryControl::ControlPanel",
    "AWS::Route53::RecordSetGroup",
    "AWS::AppStream::ApplicationEntitlementAssociation",
    "AWS::KinesisAnalytics::ApplicationReferenceDataSource",
    "AWS::EC2::LocalGatewayRoute",
    "AWS::CloudFormation::PublicTypeVersion",
    "AWS::RefactorSpaces::Application",
    "AWS::IoTSiteWise::AccessPolicy",
    "AWS::OpsWorks::App",
    "AWS::Kinesis::Stream",
    "AWS::Greengrass::CoreDefinition",
    "AWS::Backup::ReportPlan",
    "AWS::PinpointEmail::DedicatedIpPool",
    "AWS::Batch::JobDefinition",
    "AWS::IAM::SAMLProvider",
    "AWS::Lightsail::Database",
    "AWS::AppFlow::Connector",
    "AWS::Lightsail::LoadBalancer",
    "AWS::CloudFront::KeyGroup",
    "AWS::EC2::NetworkInterfaceAttachment",
    "AWS::EC2::TransitGatewayAttachment",
    "AWS::Wisdom::KnowledgeBase",
    "AWS::Cognito::UserPoolUser",
    "AWS::Connect::ContactFlowModule",
    "AWS::CodeDeploy::DeploymentConfig",
    "AWS::IoTSiteWise::AssetModel",
    "AWS::NetworkManager::GlobalNetwork",
    "AWS::BillingConductor::PricingPlan",
    "AWS::Connect::TaskTemplate",
    "AWS::Pinpoint::APNSSandboxChannel",
    "AWS::ServiceCatalogAppRegistry::Application",
    "AWS::NetworkManager::Site",
    "AWS::Glue::Database",
    "AWS::Neptune::DBCluster",
    "AWS::Evidently::Feature",
    "AWS::Backup::BackupVault",
    "AWS::EC2::CustomerGateway",
    "AWS::Scheduler::Schedule",
    "AWS::WAF::ByteMatchSet",
    "AWS::AmplifyUIBuilder::Theme",
    "AWS::Neptune::DBClusterParameterGroup",
    "AWS::EMRServerless::Application",
    "AWS::EC2::Host",
    "AWS::Forecast::DatasetGroup",
    "AWS::AppStream::User",
    "AWS::Lambda::CodeSigningConfig",
    "AWS::Comprehend::Flywheel",
    "AWS::IoTTwinMaker::Scene",
    "AWS::SystemsManagerSAP::Application",
    "AWS::DMS::ReplicationTask",
    "AWS::Panorama::ApplicationInstance",
    "AWS::EC2::RouteTable",
    "AWS::IoTWireless::WirelessDeviceImportTask",
    "AWS::RDS::DBProxyEndpoint",
    "AWS::DataSync::LocationSMB",
    "AWS::ResilienceHub::App",
    "AWS::RolesAnywhere::CRL",
    "AWS::Connect::EvaluationForm",
    "AWS::Redshift::ClusterParameterGroup",
    "AWS::BillingConductor::CustomLineItem",
    "AWS::Organizations::Policy",
    "AWS::Glue::Trigger",
    "AWS::GlobalAccelerator::Listener",
    "AWS::Signer::SigningProfile",
    "AWS::KendraRanking::ExecutionPlan",
    "AWS::EC2::VPCPeeringConnection",
    "AWS::SNS::TopicPolicy",
    "AWS::MWAA::Environment",
    "AWS::ElastiCache::GlobalReplicationGroup",
    "AWS::NetworkFirewall::RuleGroup",
    "AWS::DataSync::LocationFSxOpenZFS",
    "AWS::KMS::Key",
    "AWS::Route53Resolver::ResolverDNSSECConfig",
    "AWS::ServiceCatalog::AcceptedPortfolioShare",
    "AWS::Route53Resolver::FirewallRuleGroupAssociation",
    "AWS::Route53Resolver::ResolverQueryLoggingConfig",
    "AWS::EC2::Subnet",
    "AWS::CloudTrail::ResourcePolicy",
    "AWS::IoTTwinMaker::ComponentType",
    "AWS::S3ObjectLambda::AccessPoint",
    "AWS::Lightsail::Instance",
    "AWS::WAF::Rule",
    "AWS::ElasticBeanstalk::ConfigurationTemplate",
    "AWS::SQS::QueuePolicy",
    "AWS::SES::ReceiptRuleSet",
    "AWS::AppSync::DomainNameApiAssociation",
    "AWS::AppSync::ApiCache",
    "AWS::ApiGateway::Account",
    "AWS::WAFv2::WebACL",
    "AWS::GlobalAccelerator::EndpointGroup",
    "AWS::EC2::TransitGatewayConnect",
    "AWS::NetworkManager::SiteToSiteVpnAttachment",
    "AWS::EMRContainers::VirtualCluster",
    "AWS::EC2::SecurityGroup",
    "AWS::QuickSight::Theme",
    "AWS::PinpointEmail::Identity",
    "AWS::EC2::CapacityReservationFleet",
    "AWS::OpsWorks::Volume",
    "AWS::SES::EmailIdentity",
    "AWS::IAM::UserToGroupAddition",
    "AWS::Events::Rule",
    "AWS::GameLift::GameSessionQueue",
    "AWS::DataBrew::Dataset",
    "AWS::EC2::VPNGatewayRoutePropagation",
    "AWS::Glue::Crawler",
    "AWS::CloudFront::Function",
    "AWS::ApiGateway::Method",
    "AWS::WAFRegional::RegexPatternSet",
    "AWS::SSM::PatchBaseline",
    "AWS::ServiceDiscovery::Service",
    "AWS::IoTTwinMaker::SyncJob",
    "AWS::CustomerProfiles::ObjectType",
    "AWS::CloudFront::MonitoringSubscription",
    "AWS::IoTEvents::AlarmModel",
    "AWS::EFS::MountTarget",
    "AWS::QuickSight::DataSet",
    "AWS::EC2::VPNConnection",
    "AWS::WAF::WebACL",
    "AWS::ServiceDiscovery::PublicDnsNamespace",
    "AWS::NetworkManager::VpcAttachment",
    "AWS::IAM::User",
    "AWS::EMR::InstanceGroupConfig",
    "AWS::OpenSearchServerless::SecurityPolicy",
    "AWS::MediaConnect::Flow",
    "AWS::IoTWireless::NetworkAnalyzerConfiguration",
    "AWS::LookoutMetrics::Alert",
    "AWS::IoTWireless::TaskDefinition",
    "AWS::StepFunctions::Activity",
    "AWS::Synthetics::Group",
    "AWS::ECR::PublicRepository",
    "AWS::Forecast::Dataset",
    "AWS::SageMaker::Project",
    "AWS::EC2::LocalGatewayRouteTableVirtualInterfaceGroupAssociation",
    "AWS::S3::BucketPolicy",
    "AWS::AppSync::GraphQLSchema",
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
    "AWS::Lightsail::Certificate",
    "AWS::Chatbot::SlackChannelConfiguration",
    "AWS::CloudFront::Distribution",
    "AWS::SSMContacts::Plan",
    "AWS::ElastiCache::SubnetGroup",
    "AWS::XRay::Group",
    "AWS::Panorama::Package",
    "AWS::LookoutVision::Project",
    "AWS::Oam::Link",
    "AWS::IoT::DomainConfiguration",
    "AWS::FraudDetector::EventType",
    "AWS::SageMaker::Endpoint",
    "AWS::NetworkFirewall::Firewall",
    "AWS::EventSchemas::Schema",
    "AWS::M2::Application",
    "AWS::LookoutEquipment::InferenceScheduler",
    "AWS::SES::Template",
    "AWS::KMS::ReplicaKey",
    "AWS::SES::ReceiptRule",
    "AWS::SSMContacts::Rotation",
    "AWS::IoTAnalytics::Dataset",
    "AWS::FraudDetector::Outcome",
    "AWS::Redshift::ClusterSecurityGroup",
    "AWS::Route53::CidrCollection",
    "AWS::ECR::PullThroughCacheRule",
    "AWS::Glue::MLTransform",
    "AWS::IoTTwinMaker::Entity",
    "AWS::AppConfig::HostedConfigurationVersion",
    "AWS::DataSync::LocationEFS",
    "AWS::EC2::LocalGatewayRouteTable",
    "AWS::ApiGateway::Resource",
    "AWS::SageMaker::AppImageConfig",
    "AWS::Macie::Session",
    "AWS::ElasticLoadBalancingV2::TargetGroup",
    "AWS::ApplicationAutoScaling::ScalingPolicy",
    "AWS::Pipes::Pipe",
    "AWS::IoTSiteWise::Gateway",
    "AWS::EMR::StudioSessionMapping",
    "AWS::IVS::PlaybackKeyPair",
    "AWS::CloudFormation::Macro",
    "AWS::RoboMaker::RobotApplication",
    "AWS::SageMaker::Workteam",
    "AWS::SSMIncidents::ResponsePlan",
    "AWS::Lambda::LayerVersionPermission",
    "AWS::SecretsManager::Secret",
    "AWS::Route53Resolver::ResolverConfig",
    "AWS::ElastiCache::User",
    "AWS::Neptune::DBInstance",
    "AWS::SageMaker::Image",
    "AWS::Route53RecoveryReadiness::ResourceSet",
    "AWS::Logs::SubscriptionFilter",
    "AWS::CodeDeploy::Application",
    "AWS::DMS::EventSubscription",
    "AWS::SSMIncidents::ReplicationSet",
    "AWS::IoT::TopicRule",
    "AWS::AppRunner::VpcConnector",
    "AWS::SupportApp::SlackWorkspaceConfiguration",
    "AWS::LakeFormation::PrincipalPermissions",
    "AWS::DataSync::LocationS3",
    "AWS::MediaConvert::Preset",
    "AWS::AutoScaling::LifecycleHook",
    "AWS::FSx::DataRepositoryAssociation",
    "AWS::EC2::NetworkInterface",
    "AWS::SageMaker::FeatureGroup",
    "AWS::AppSync::Resolver",
    "AWS::IoTWireless::PartnerAccount",
    "AWS::FraudDetector::EntityType",
    "AWS::RolesAnywhere::TrustAnchor",
    "AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation",
    "AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource",
    "AWS::Lambda::EventInvokeConfig",
    "AWS::MediaConnect::FlowOutput",
    "AWS::Lambda::LayerVersion",
    "AWS::KinesisVideo::Stream",
    "AWS::RUM::AppMonitor",
    "AWS::RDS::OptionGroup",
    "AWS::OpsWorks::UserProfile",
    "AWS::Glue::Schema",
    "AWS::DocDB::DBSubnetGroup",
    "AWS::ServiceCatalog::Portfolio",
    "AWS::CustomerProfiles::Domain",
    "AWS::IoT::Policy",
    "AWS::EC2::TransitGatewayRoute",
    "AWS::SSM::MaintenanceWindow",
    "AWS::LakeFormation::TagAssociation",
    "AWS::Rekognition::Project",
    "AWS::EC2::IPAMResourceDiscovery",
    "AWS::DataSync::StorageSystem",
    "AWS::GreengrassV2::ComponentVersion",
    "AWS::M2::Environment",
    "AWS::Pinpoint::Campaign",
    "AWS::ImageBuilder::InfrastructureConfiguration",
    "AWS::IoT::Logging",
    "AWS::MediaLive::Input",
    "AWS::CloudFormation::WaitCondition",
    "AWS::Route53Resolver::ResolverEndpoint",
    "AWS::IoT::ScheduledAudit",
    "AWS::Connect::ContactFlow",
    "AWS::DevOpsGuru::LogAnomalyDetectionIntegration",
    "AWS::NetworkManager::Link",
    "AWS::QLDB::Stream",
    "AWS::SageMaker::NotebookInstance",
    "AWS::IoTSiteWise::Dashboard",
    "AWS::Pinpoint::APNSVoipChannel",
    "AWS::SSO::InstanceAccessControlAttributeConfiguration",
    "AWS::WAFRegional::ByteMatchSet",
    "AWS::Evidently::Segment",
    "AWS::CloudWatch::AnomalyDetector",
    "AWS::EC2::SubnetNetworkAclAssociation",
    "AWS::ServiceCatalog::ServiceAction",
    "AWS::AppStream::Entitlement",
    "AWS::CloudFront::OriginAccessControl",
    "AWS::IoT::MitigationAction",
    "AWS::Cognito::UserPool",
    "AWS::SecretsManager::RotationSchedule",
    "AWS::EC2::VerifiedAccessInstance",
    "AWS::Lambda::Permission",
    "AWS::NetworkFirewall::FirewallPolicy",
    "AWS::EKS::IdentityProviderConfig",
    "AWS::IoT1Click::Device",
    "AWS::EC2::IPAMResourceDiscoveryAssociation",
    "AWS::OpsWorksCM::Server",
    "AWS::ServiceCatalogAppRegistry::AttributeGroup",
    "AWS::Lightsail::LoadBalancerTlsCertificate",
    "AWS::EC2::ClientVpnTargetNetworkAssociation",
    "AWS::AppSync::GraphQLApi",
    "AWS::GameLift::MatchmakingRuleSet",
    "AWS::EC2::EgressOnlyInternetGateway",
    "AWS::Config::ConformancePack",
    "AWS::EC2::VPCCidrBlock",
    "AWS::APS::Workspace",
    "AWS::Kendra::DataSource",
    "AWS::IoTThingsGraph::FlowTemplate",
    "AWS::AppRunner::VpcIngressConnection",
    "AWS::GameLift::Script",
    "AWS::IAM::VirtualMFADevice",
    "AWS::EC2::NetworkInsightsPath",
    "AWS::Neptune::DBParameterGroup",
    "AWS::ACMPCA::CertificateAuthority",
    "AWS::Athena::PreparedStatement",
    "AWS::AutoScaling::ScheduledAction",
    "AWS::Omics::SequenceStore",
    "AWS::ApiGatewayV2::Route",
    "AWS::LakeFormation::Resource",
    "AWS::Detective::MemberInvitation",
    "AWS::EC2::IPAMScope",
    "AWS::SageMaker::DataQualityJobDefinition",
    "AWS::DirectoryService::SimpleAD",
    "AWS::CloudFront::StreamingDistribution",
    "AWS::EC2::VPCEndpoint",
    "AWS::Personalize::DatasetGroup",
    "AWS::RDS::EventSubscription",
    "AWS::Config::AggregationAuthorization",
    "AWS::DataSync::Agent",
    "AWS::IoTWireless::Destination",
    "AWS::Cognito::UserPoolIdentityProvider",
    "AWS::AppStream::StackUserAssociation",
    "AWS::ResilienceHub::ResiliencyPolicy",
    "AWS::Location::Tracker",
    "AWS::IoT::Dimension",
    "AWS::Logs::LogGroup",
    "AWS::Evidently::Experiment",
    "AWS::ECS::Cluster",
    "AWS::S3::MultiRegionAccessPointPolicy",
    "AWS::IoTWireless::WirelessDevice",
    "AWS::EC2::TrafficMirrorFilterRule",
    "AWS::Grafana::Workspace",
    "AWS::EC2::PlacementGroup",
    "AWS::Organizations::Account",
    "AWS::ECR::Repository",
    "AWS::AuditManager::Assessment",
    "AWS::SES::DedicatedIpPool",
    "AWS::IoT::FleetMetric",
    "AWS::AppStream::Fleet",
    "AWS::MediaConnect::FlowSource",
    "AWS::Greengrass::SubscriptionDefinitionVersion",
    "AWS::AppConfig::Extension",
    "AWS::Lex::ResourcePolicy",
    "AWS::ElasticLoadBalancingV2::ListenerRule",
    "AWS::Glue::Registry",
    "AWS::EC2::KeyPair",
    "AWS::FSx::FileSystem",
    "AWS::AppStream::ApplicationFleetAssociation",
    "AWS::EC2::EIPAssociation",
    "AWS::IoTAnalytics::Pipeline",
    "AWS::ElasticBeanstalk::Application",
    "AWS::IoT::ThingPrincipalAttachment",
    "AWS::DLM::LifecyclePolicy",
    "AWS::FraudDetector::Detector",
    "AWS::ManagedBlockchain::Accessor",
    "AWS::EC2::CapacityReservation",
    "AWS::ElasticLoadBalancing::LoadBalancer",
    "AWS::Transfer::User",
    "AWS::ManagedBlockchain::Member",
    "AWS::Cognito::IdentityPool",
    "AWS::NimbleStudio::StudioComponent",
    "AWS::EC2::TrafficMirrorTarget",
    "AWS::StepFunctions::StateMachine",
    "AWS::RDS::DBClusterParameterGroup",
    "AWS::WAF::XssMatchSet",
    "AWS::Route53RecoveryReadiness::ReadinessCheck",
    "AWS::AppMesh::VirtualRouter",
    "AWS::PinpointEmail::ConfigurationSet",
    "AWS::Pinpoint::EmailTemplate",
    "AWS::Scheduler::ScheduleGroup",
    "AWS::AppStream::DirectoryConfig",
    "AWS::DevOpsGuru::NotificationChannel",
    "AWS::CodeStar::GitHubRepository",
    "AWS::Inspector::AssessmentTarget",
    "AWS::FSx::Snapshot",
    "AWS::EventSchemas::RegistryPolicy",
    "AWS::Route53::KeySigningKey",
    "AWS::EventSchemas::Registry",
    "AWS::Config::RemediationConfiguration",
    "AWS::Greengrass::LoggerDefinition",
    "AWS::Greengrass::DeviceDefinitionVersion",
    "AWS::SimSpaceWeaver::Simulation",
    "AWS::Events::Connection",
    "AWS::Athena::DataCatalog",
    "AWS::DocDB::DBCluster",
    "AWS::MediaConnect::FlowVpcInterface",
    "AWS::Greengrass::FunctionDefinitionVersion",
    "AWS::Glue::Workflow",
    "AWS::ApiGatewayV2::Authorizer",
    "AWS::IoT::AccountAuditConfiguration",
    "AWS::SageMaker::UserProfile",
    "AWS::Personalize::Dataset",
    "AWS::IoT1Click::Placement",
    "AWS::EC2::PrefixList",
    "AWS::EC2::Instance",
    "AWS::OpenSearchServerless::SecurityConfig",
    "AWS::NetworkManager::Device",
    "AWS::EC2::SubnetCidrBlock",
    "AWS::MediaPackage::Asset",
    "AWS::ElasticBeanstalk::ApplicationVersion",
    "AWS::AppMesh::VirtualGateway",
    "AWS::ConnectCampaigns::Campaign",
    "AWS::WAF::SqlInjectionMatchSet",
    "AWS::SageMaker::DeviceFleet",
    "AWS::EC2::TransitGatewayVpcAttachment",
    "AWS::EC2::FlowLog",
    "AWS::Events::Endpoint",
    "AWS::AmazonMQ::Broker",
    "AWS::EMR::Step",
    "AWS::SSM::Association",
    "AWS::EC2::ClientVpnEndpoint",
    "AWS::CloudFront::ResponseHeadersPolicy",
    "AWS::MSK::ClusterPolicy",
    "AWS::GuardDuty::Master",
    "AWS::KMS::Alias",
    "AWS::FraudDetector::Label",
    "AWS::BillingConductor::BillingGroup",
    "AWS::XRay::SamplingRule",
    "AWS::CodeGuruProfiler::ProfilingGroup",
    "AWS::Route53Resolver::ResolverRule",
    "AWS::Transfer::Connector",
    "AWS::Pinpoint::ADMChannel",
    "AWS::AppMesh::VirtualNode",
    "AWS::ApiGateway::DocumentationVersion",
    "AWS::LicenseManager::Grant",
    "AWS::WAFv2::WebACLAssociation",
    "AWS::LookoutMetrics::AnomalyDetector",
    "AWS::Oam::Sink",
    "AWS::CodeBuild::ReportGroup",
    "AWS::ApiGateway::GatewayResponse",
    "AWS::EC2::ClientVpnAuthorizationRule",
    "AWS::EC2::EnclaveCertificateIamRoleAssociation",
    "AWS::Lightsail::Distribution",
    "AWS::Connect::PhoneNumber",
    "AWS::FSx::Volume",
    "AWS::ACMPCA::Certificate",
    "AWS::EC2::IPAMAllocation",
    "AWS::WorkSpaces::Workspace",
    "AWS::Inspector::AssessmentTemplate",
    "AWS::EMR::Studio",
    "AWS::DAX::ParameterGroup",
    "AWS::SES::ReceiptFilter",
    "AWS::DirectoryService::MicrosoftAD",
    "AWS::MemoryDB::SubnetGroup",
    "AWS::DataSync::LocationObjectStorage",
    "AWS::ECS::CapacityProvider",
    "AWS::ElastiCache::CacheCluster",
    "AWS::SageMaker::ModelCard",
    "AWS::VpcLattice::AccessLogSubscription",
    "AWS::Logs::Destination",
    "AWS::EKS::Nodegroup",
    "AWS::Organizations::OrganizationalUnit",
    "AWS::AppSync::DataSource",
    "AWS::SQS::Queue",
    "AWS::EC2::SecurityGroupIngress",
    "AWS::GuardDuty::Detector",
    "AWS::SageMaker::ModelQualityJobDefinition",
    "AWS::IoT::ProvisioningTemplate",
    "AWS::Personalize::Schema",
    "AWS::AppFlow::Flow",
    "AWS::ApiGateway::Stage",
    "AWS::Budgets::Budget",
    "AWS::NetworkManager::CoreNetwork",
    "AWS::FinSpace::Environment",
    "AWS::IoTWireless::DeviceProfile",
    "AWS::Batch::ComputeEnvironment",
    "AWS::Connect::InstanceStorageConfig",
    "AWS::DataPipeline::Pipeline",
    "AWS::IoTCoreDeviceAdvisor::SuiteDefinition",
    "AWS::IoT::Thing",
    "AWS::Route53::HealthCheck",
    "AWS::Pinpoint::Segment",
    "AWS::Omics::RunGroup",
    "AWS::Events::EventBusPolicy",
    "AWS::Athena::NamedQuery",
    "AWS::EC2::TrafficMirrorFilter",
    "AWS::ApiGateway::Deployment",
    "AWS::WAFRegional::Rule",
    "AWS::Inspector::ResourceGroup",
    "AWS::LakeFormation::DataLakeSettings",
    "AWS::GreengrassV2::Deployment",
    "AWS::AutoScaling::ScalingPolicy",
    "AWS::GroundStation::Config",
    "AWS::ResourceExplorer2::DefaultViewAssociation",
    "AWS::IoTFleetWise::Vehicle",
    "AWS::ECR::RegistryPolicy",
    "AWS::Redshift::ScheduledAction",
    "AWS::RDS::DBSecurityGroup",
    "AWS::Pinpoint::BaiduChannel",
    "AWS::MediaPackage::Channel",
    "AWS::ApiGatewayV2::RouteResponse",
    "AWS::CloudWatch::MetricStream",
    "AWS::Location::GeofenceCollection",
    "AWS::SSM::Parameter",
    "AWS::ApiGatewayV2::ApiGatewayManagedOverrides",
    "AWS::Config::DeliveryChannel",
    "AWS::CertificateManager::Account",
    "AWS::SageMaker::MonitoringSchedule",
    "AWS::IAM::OIDCProvider",
    "AWS::LakeFormation::Tag",
    "AWS::CE::AnomalyMonitor",
    "AWS::IoTFleetWise::Fleet",
    "AWS::ServiceCatalogAppRegistry::ResourceAssociation",
    "AWS::Timestream::Table",
    "AWS::EC2::VPNGateway",
    "AWS::CloudFormation::Stack",
    "AWS::ResourceGroups::Group",
    "AWS::CloudFormation::ResourceDefaultVersion",
    "AWS::SSM::ResourceDataSync",
    "AWS::Signer::ProfilePermission",
    "AWS::DocDB::DBClusterParameterGroup",
    "AWS::S3::MultiRegionAccessPoint",
    "AWS::Greengrass::LoggerDefinitionVersion",
    "AWS::QuickSight::Dashboard",
    "AWS::ServiceCatalog::TagOptionAssociation",
    "AWS::EC2::IPAM",
    "AWS::DataBrew::Job",
    "AWS::EC2::TransitGatewayPeeringAttachment",
    "AWS::QuickSight::Template",
    "AWS::SupportApp::SlackChannelConfiguration",
    "AWS::IoTWireless::FuotaTask",
    "AWS::CloudFront::CachePolicy",
    "AWS::AppIntegrations::DataIntegration",
    "AWS::IAM::AccessKey",
    "AWS::RDS::DBSubnetGroup",
    "AWS::IVSChat::Room",
    "AWS::SecretsManager::SecretTargetAttachment",
    "AWS::AmazonMQ::Configuration",
    "AWS::AppConfig::Deployment",
    "AWS::CodePipeline::CustomActionType",
    "AWS::AccessAnalyzer::Analyzer",
    "AWS::EC2::EC2Fleet",
    "AWS::Pinpoint::InAppTemplate",
    "AWS::Greengrass::ResourceDefinition",
    "AWS::DMS::ReplicationInstance",
    "AWS::DAX::SubnetGroup",
    "AWS::ServiceCatalog::CloudFormationProduct",
    "AWS::S3::StorageLens",
    "AWS::EC2::VPCEndpointService",
    "AWS::IAM::ManagedPolicy",
    "AWS::CodeArtifact::Domain",
    "AWS::EC2::LaunchTemplate",
    "AWS::Pinpoint::VoiceChannel",
    "AWS::CloudFront::OriginRequestPolicy",
    "AWS::DataSync::LocationFSxONTAP",
    "AWS::Route53RecoveryReadiness::RecoveryGroup",
    "AWS::NetworkManager::LinkAssociation",
    "AWS::Cognito::UserPoolRiskConfigurationAttachment",
    "AWS::MediaTailor::PlaybackConfiguration",
    "AWS::ElasticBeanstalk::Environment",
    "AWS::Cognito::UserPoolClient",
    "AWS::MediaPackage::PackagingGroup",
    "AWS::WAFRegional::SqlInjectionMatchSet",
    "AWS::Lambda::Version",
    "AWS::EC2::DHCPOptions",
    "AWS::EC2::IPAMPool",
    "AWS::Kinesis::StreamConsumer",
    "AWS::IoT1Click::Project",
    "AWS::IAM::ServiceLinkedRole",
    "AWS::CloudFormation::HookTypeConfig",
    "AWS::EC2::Volume",
    "AWS::LicenseManager::License",
    "AWS::IoT::Certificate",
    "AWS::EC2::EIP",
    "AWS::Greengrass::ResourceDefinitionVersion",
    "AWS::CloudFormation::ResourceVersion",
    "AWS::SageMaker::ModelExplainabilityJobDefinition",
    "AWS::ApiGatewayV2::Stage",
    "AWS::Panorama::PackageVersion",
    "AWS::Chatbot::MicrosoftTeamsChannelConfiguration",
    "AWS::RDS::DBProxy",
    "AWS::Pinpoint::APNSChannel",
    "AWS::RDS::DBParameterGroup",
    "AWS::SecurityHub::Hub",
    "AWS::S3::AccessPoint",
    "AWS::Greengrass::GroupVersion",
    "AWS::Pinpoint::SMSChannel",
    "AWS::NimbleStudio::Studio",
    "AWS::EC2::TrafficMirrorSession",
    "AWS::S3Outposts::BucketPolicy",
    "AWS::Batch::JobQueue",
    "AWS::Lightsail::Alarm",
    "AWS::VpcLattice::ServiceNetworkVpcAssociation",
    "AWS::ElasticLoadBalancingV2::Listener",
    "AWS::Redshift::EventSubscription",
    "AWS::IoTFleetHub::Application",
    "AWS::Connect::User",
    "AWS::SSMContacts::ContactChannel",
    "AWS::MemoryDB::ACL",
    "AWS::CloudFormation::WaitConditionHandle",
    "AWS::Pinpoint::SmsTemplate",
    "AWS::GlobalAccelerator::Accelerator",
    "AWS::EKS::Addon",
]
cached = []
