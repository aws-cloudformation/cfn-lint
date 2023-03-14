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
    "aws-s3outposts-accesspoint.json",
    "aws-ec2-ipampoolcidr.json",
    "aws-iot-topicruledestination.json",
    "aws-redshift-clustersubnetgroup.json",
    "aws-apigatewayv2-integrationresponse.json",
    "aws-ec2-networkacl.json",
    "aws-logs-resourcepolicy.json",
    "aws-servicecatalog-launchnotificationconstraint.json",
    "aws-iot-cacertificate.json",
    "aws-ec2-networkaclentry.json",
    "aws-transfer-certificate.json",
    "aws-apigateway-documentationpart.json",
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
    "aws-kinesisfirehose-deliverystream.json",
    "aws-imagebuilder-component.json",
    "aws-glue-connection.json",
    "aws-iam-group.json",
    "aws-ec2-transitgatewaymulticastgroupsource.json",
    "aws-transfer-profile.json",
    "aws-apigateway-usageplankey.json",
    "aws-datasync-locationhdfs.json",
    "aws-msk-cluster.json",
    "aws-codepipeline-pipeline.json",
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
    "aws-appconfig-deploymentstrategy.json",
    "aws-glue-devendpoint.json",
    "aws-elasticache-usergroup.json",
    "aws-imagebuilder-imagerecipe.json",
    "aws-opsworks-elasticloadbalancerattachment.json",
    "aws-s3objectlambda-accesspointpolicy.json",
    "aws-networkmanager-transitgatewayregistration.json",
    "aws-elasticache-replicationgroup.json",
    "aws-cloudformation-moduledefaultversion.json",
    "aws-sso-permissionset.json",
    "aws-glue-job.json",
    "aws-servicecatalog-cloudformationprovisionedproduct.json",
    "aws-glue-table.json",
    "aws-logs-metricfilter.json",
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
    "aws-datasync-task.json",
    "aws-ecs-taskdefinition.json",
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
    "aws-ec2-vpcendpointservicepermissions.json",
    "aws-ssm-maintenancewindowtask.json",
    "aws-ec2-transitgatewaymulticastdomain.json",
    "aws-eks-cluster.json",
    "aws-codebuild-project.json",
    "aws-logs-querydefinition.json",
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
    "aws-dms-replicationsubnetgroup.json",
    "aws-s3outposts-bucket.json",
    "aws-route53-recordsetgroup.json",
    "aws-ec2-localgatewayroute.json",
    "aws-opsworks-app.json",
    "aws-batch-jobdefinition.json",
    "aws-iam-samlprovider.json",
    "aws-ec2-networkinterfaceattachment.json",
    "aws-ec2-transitgatewayattachment.json",
    "aws-networkmanager-globalnetwork.json",
    "aws-servicecatalogappregistry-application.json",
    "aws-networkmanager-site.json",
    "aws-glue-database.json",
    "aws-neptune-dbcluster.json",
    "aws-backup-backupvault.json",
    "aws-waf-bytematchset.json",
    "aws-dms-replicationtask.json",
    "aws-datasync-locationsmb.json",
    "aws-redshift-clusterparametergroup.json",
    "aws-organizations-policy.json",
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
    "aws-glue-crawler.json",
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
    "aws-secretsmanager-secret.json",
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
    "aws-apigatewayv2-route.json",
    "aws-detective-memberinvitation.json",
    "aws-ec2-ipamscope.json",
    "aws-ec2-vpcendpoint.json",
    "aws-rds-eventsubscription.json",
    "aws-datasync-agent.json",
    "aws-iot-dimension.json",
    "aws-ec2-trafficmirrorfilterrule.json",
    "aws-ecr-repository.json",
    "aws-iot-fleetmetric.json",
    "aws-glue-registry.json",
    "aws-ec2-keypair.json",
    "aws-fsx-filesystem.json",
    "aws-ec2-eipassociation.json",
    "aws-iot-thingprincipalattachment.json",
    "aws-dlm-lifecyclepolicy.json",
    "aws-ec2-capacityreservation.json",
    "aws-elasticloadbalancing-loadbalancer.json",
    "aws-transfer-user.json",
    "aws-ec2-trafficmirrortarget.json",
    "aws-stepfunctions-statemachine.json",
    "aws-rds-dbclusterparametergroup.json",
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
    "aws-kms-alias.json",
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
    "aws-organizations-organizationalunit.json",
    "aws-ec2-securitygroupingress.json",
    "aws-guardduty-detector.json",
    "aws-iot-provisioningtemplate.json",
    "aws-batch-computeenvironment.json",
    "aws-events-eventbuspolicy.json",
    "aws-athena-namedquery.json",
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
    "aws-ec2-launchtemplate.json",
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
