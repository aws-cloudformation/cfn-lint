./scripts/create_cfn_schema_rule.py --resource-type aws::autoscaling::AutoScalingGroup --rule-level E --schema-name onlyone --rule-name AutoScalingGroupOnlyone
./scripts/create_cfn_schema_rule.py --resource-type aws::autoscaling::AutoScalingGroup --rule-level E --schema-name launchtemplatespecification_onlyone --rule-name AutoScalingGroupOnlyoneLaunchTemplateSpecificationOnlyOne
./scripts/create_cfn_schema_rule.py --resource-type aws::cloudwatch::alarm --rule-level E --schema-name thresholdmetric_exclusive --rule-name AlarmThresholdMetricExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::cloudwatch::alarm --rule-level E --schema-name metrics_exclusive --rule-name AlarmMetricsExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::cloudwatch::alarm --rule-level E --schema-name metric_onlyone --rule-name AlarmMetricOnlyOne
./scripts/create_cfn_schema_rule.py --resource-type aws::cloudwatch::alarm --rule-level E --schema-name aws_namespace_period --rule-name AlarmAwsNamespacePeriod
./scripts/create_cfn_schema_rule.py --resource-type aws::cloudwatch::alarm --rule-level E --schema-name statistic_exclusive --rule-name AlarmStatisticExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::managedblockchain::node --rule-level E --schema-name nodeconfiguration_instancetype_enum --rule-name NodeNodeConfigurationInstancetypeEnum
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::LaunchTemplate --rule-level E --schema-name launchtemplatedata_securitygroups_onlyone --rule-name LaunchTemplateLaunchTemplateDataSecurityGroupsOnlyOne
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::LaunchTemplate --rule-level E --schema-name blockdevicemapping_virtualname --rule-name LaunchTemplateBlockDeviceMappingVirtualName
./scripts/create_cfn_schema_rule.py --resource-type aws::docdb::DBInstance --rule-level E --schema-name dbinstanceclass_enum --rule-name DBInstanceClassEnum
./scripts/create_cfn_schema_rule.py --resource-type aws::appstream::fleet --rule-level E --schema-name instancetype_enum --rule-name FleetInstanceTypeEnum
./scripts/create_cfn_schema_rule.py --resource-type aws::iam::role --rule-level E --schema-name arn_pattern --rule-name RoleArnPattern
./scripts/create_cfn_schema_rule.py --resource-type aws::iam::role --rule-level E --schema-name maxsessionduration_integer --rule-name RoleMaxsessionDurationInteger
./scripts/create_cfn_schema_rule.py --resource-type aws::iam::role --rule-level E --schema-name rolename_string --rule-name RoleRoleNameString
./scripts/create_cfn_schema_rule.py --resource-type aws::route53::recordset --rule-level E --schema-name hostedzone_onlyone --rule-name RecordSetHostedZoneOnlyOne
./scripts/create_cfn_schema_rule.py --resource-type aws::codepipeline::pipeline --rule-level E --schema-name artifactstore_onlyone --rule-name PipelineArtifactStoreOnlyOne
./scripts/create_cfn_schema_rule.py --resource-type aws::iam::path --rule-level E --schema-name path_pattern --rule-name PathPathPattern
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::instance --rule-level E --schema-name instancetype_enum --rule-name InstanceInstancetypeEnum
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::instance --rule-level E --schema-name exclusive --rule-name InstanceExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::instance --rule-level E --schema-name blockdevicemapping_onlyone --rule-name InstanceBlockDeviceMappingOnlyOne
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::instance --rule-level E --schema-name blockdevicemapping_virtualname_exclusive --rule-name InstanceBlockDeviceMappingVirtualNameExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::instance --rule-level E --schema-name required --rule-name InstanceRequired
./scripts/create_cfn_schema_rule.py --resource-type aws::lambda::eventsourcemapping --rule-level E --schema-name eventsourcearn_stream_inclusive --rule-name EventSourceMappingEventSourceArnStreamInclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::lambda::eventsourcemapping --rule-level E --schema-name eventsourcearn_sqs_exclusive --rule-name EventSourceMappingEventSourceArnSqsExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::neptune::DBInstance --rule-level E --schema-name dbinstanceclass_enum --rule-name DBInstanceDBInstanceClassEnum
./scripts/create_cfn_schema_rule.py --resource-type aws::iam::policy --rule-level E --schema-name required --rule-name PolicyRequired
./scripts/create_cfn_schema_rule.py --resource-type aws::iam::policy --rule-level E --schema-name policyname_string --rule-name PolicyPolicyNameString
./scripts/create_cfn_schema_rule.py --resource-type aws::dynamodb::table --rule-level E --schema-name billingmode_exclusive --rule-name TableBillingModeExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::vpc --rule-level E --schema-name cidr_oneof --rule-name VpcCidrOneOf
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::vpc --rule-level E --schema-name ipam_pool --rule-name VpcIpamPool
./scripts/create_cfn_schema_rule.py --resource-type aws::gamelift::fleet --rule-level E --schema-name ec2instancetype_enum --rule-name FleetEc2InstanceTypeEnum
./scripts/create_cfn_schema_rule.py --resource-type aws::cloudfront::distribution --rule-level E --schema-name viewercertificate_onlyone --rule-name DistributionViewerCertificateOnlyOne
./scripts/create_cfn_schema_rule.py --resource-type aws::cloudfront::distribution --rule-level E --schema-name viewercertificate_acmcertificatearn_inclusive --rule-name DistributionViewerCertificateAcmCertificateArnInclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::cloudfront::distribution --rule-level E --schema-name customerrorresponse_responsecode_inclusive --rule-name DistributionCustomErrorResponseResponseCodeInclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::cloudfront::distribution --rule-level E --schema-name origin_onlyone --rule-name DistributionOriginOnlyOne
./scripts/create_cfn_schema_rule.py --resource-type aws::cloudfront::distribution --rule-level E --schema-name viewercertificate_iamcertificateid_inclusive --rule-name DistributionViewerCertificateIamCertificateIdInclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::elasticache::cachecluster --rule-level E --schema-name cachenodetype_enum --rule-name CacheclusterCachenodetypeEnum
./scripts/create_cfn_schema_rule.py --resource-type aws::applicationautoscaling::scalingpolicy --rule-level E --schema-name scalingpolicy --rule-name ScalingpolicyScalingPolicy
./scripts/create_cfn_schema_rule.py --resource-type aws::events::rule --rule-level E --schema-name required --rule-name RuleRequired
./scripts/create_cfn_schema_rule.py --resource-type aws::iam::managedpolicy --rule-level E --schema-name arn_pattern --rule-name ManagedPolicyArnPattern
./scripts/create_cfn_schema_rule.py --resource-type aws::iam::managedpolicy --rule-level E --schema-name arns_array --rule-name ManagedPolicyArnsArray
./scripts/create_cfn_schema_rule.py --resource-type aws::elasticsearch::domain --rule-level E --schema-name elasticsearchclusterconfig_instancetype_enum --rule-name DomainElasticsearchClusterConfigInstanceTypeEnum
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::spotfleet --rule-level E --schema-name blockdevicemapping_onlyone --rule-name SpotFleetBlockDeviceMappingOnlyOne
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::spotfleet --rule-level E --schema-name spotfleetrequestconfigdata_onlyone --rule-name SpotFleetSpotfleetRequestConfigDataOnlyOne
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::spotfleet --rule-level E --schema-name blockdevicemapping_virtualname --rule-name SpotFleetBlockDeviceMappingVirtualName
./scripts/create_cfn_schema_rule.py --resource-type aws::s3::bucket --rule-level E --schema-name routingrulecondition_required --rule-name BucketRoutingRuleConditionRequired
./scripts/create_cfn_schema_rule.py --resource-type aws::s3::bucket --rule-level E --schema-name websiteconfiguration_redirectallrequeststo_exclusive --rule-name BucketWebsiteConfigurationRedirectAllRequestsToExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::opsworks::instance --rule-level E --schema-name blockdevicemapping_onlyone --rule-name InstanceBlockDeviceMappingOnlyone
./scripts/create_cfn_schema_rule.py --resource-type aws::opsworks::instance --rule-level E --schema-name blockdevicemapping_virtualname_exclusive --rule-name InstanceBlockDeviceMappingVirtualNameExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::route53::healthcheck --rule-level E --schema-name healthcheckconfig --rule-name HealthCheckHealthCheckConfig
./scripts/create_cfn_schema_rule.py --resource-type aws::route53::healthcheck --rule-level E --schema-name healthcheckconfig_type_inclusive --rule-name HealthCheckHealthCheckConfigTypeInclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::securitygroup --rule-level E --schema-name egress_onlyone --rule-name SecurityGroupEgressOnlyone
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::securitygroup --rule-level E --schema-name ingress_cidripv6_exclusive --rule-name SecurityGroupIngressCidrIpv6Exclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::securitygroup --rule-level E --schema-name ingress_sourcesecuritygroupid_exclusive --rule-name SecurityGroupIngressSourceSecurityGroupIdExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::securitygroup --rule-level E --schema-name securitygroupegress_inclusive --rule-name SecuritygroupSecurityGroupEgressInclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::securitygroup --rule-level E --schema-name ingress_cidrip_exclusive --rule-name SecurityGroupIngressCidrIpExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::redshift::cluster --rule-level E --schema-name nodetype_enum --rule-name ClusterNodeTypeEnum
./scripts/create_cfn_schema_rule.py --resource-type aws::rds::dbproxyendpoint --rule-level E --schema-name targetrole_enum --rule-name DbproxyEndpointTargetRoleEnum
./scripts/create_cfn_schema_rule.py --resource-type aws::elasticloadbalancingv2::loadbalancer --rule-level E --schema-name subnets_onlyone --rule-name LoadBalancerSubnetsOnlyOne
./scripts/create_cfn_schema_rule.py --resource-type aws::amazonmq::broker --rule-level E --schema-name instancetype_enum --rule-name BrokerInstanceTypeEnum
./scripts/create_cfn_schema_rule.py --resource-type aws::opsworks::stack --rule-level E --schema-name vpcid_inclusive --rule-name StackVpcIdInclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::dax::cluster --rule-level E --schema-name nodetype_enum --rule-name ClusterNodeTypeEnum
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::securitygroupingress --rule-level E --schema-name groupid_exclusive --rule-name SecurityGroupIngressGroupIdExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::securitygroupingress --rule-level E --schema-name cidripv6_exclusive --rule-name SecurityGroupIngressCidripv6Exclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::securitygroupingress --rule-level E --schema-name sourcesecuritygroupid_exclusive --rule-name SecurityGroupIngressSourcesecuritygroupIdExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::securitygroupingress --rule-level E --schema-name cidrip_exclusive --rule-name SecurityGroupIngressCidrIpExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::route53::recordsetgroup --rule-level E --schema-name hostedzone_onlyone --rule-name RecordsetGroupHostedzoneOnlyOne
./scripts/create_cfn_schema_rule.py --resource-type aws::emr::cluster --rule-level E --schema-name instancetypeconfig_instancetype_enum --rule-name ClusterInstancetypeconfigInstancetypeEnum
./scripts/create_cfn_schema_rule.py --resource-type aws::servicediscovery::service --rule-level E --schema-name healthcheckconfig_exclusive --rule-name ServiceHealthCheckConfigExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::lambda::function --rule-level E --schema-name zipfile_runtime_enum --rule-name FunctionZipfileRuntimeEnum
./scripts/create_cfn_schema_rule.py --resource-type aws::lambda::function --rule-level E --schema-name zipfile_runtime_exists --rule-name FunctionZipfileRuntimeExists
./scripts/create_cfn_schema_rule.py --resource-type aws::autoscaling::launchconfiguration --rule-level E --schema-name blockdevicemapping_virtualname_exlusive --rule-name LaunchConfigurationBlockDeviceMappingVirtualNameExlusive
./scripts/create_cfn_schema_rule.py --resource-type aws::autoscaling::launchconfiguration --rule-level E --schema-name blockdevicemapping_onlyone --rule-name LaunchConfigurationBlockDeviceMappingOnlyOne
./scripts/create_cfn_schema_rule.py --resource-type aws::ec2::networkaclentry --rule-level E --schema-name required --rule-name NetworkAclEntryRequired
./scripts/create_cfn_schema_rule.py --resource-type aws::rds::DBInstance --rule-level E --schema-name sourcedbinstanceidentifier_exclusive --rule-name DBInstanceSourceDBInstanceIdentifierExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::rds::DBInstance --rule-level E --schema-name aurora_exclusive --rule-name DBInstanceAuroraExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::rds::DBInstance --rule-level E --schema-name dbinstanceclass_enum --rule-name DBInstanceDBInstanceclassEnum
./scripts/create_cfn_schema_rule.py --resource-type aws::rds::dbcluster --rule-level E --schema-name snapshotidentifier_exclusive --rule-name DbClusterSnapshotidentifierExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::rds::dbcluster --rule-level E --schema-name sourcedbclusteridentifier_exclusive --rule-name DbClusterSourceDbClusterIdentifierExclusive
./scripts/create_cfn_schema_rule.py --resource-type aws::rds::dbcluster --rule-level E --schema-name serverless_exclusive --rule-name DbClusterServerlessExclusive