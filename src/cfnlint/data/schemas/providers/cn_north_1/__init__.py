# pylint: disable=too-many-lines
cached = [
    "aws-apigatewayv2-integration.json",
    "aws-apigatewayv2-apimapping.json",
    "aws-glue-partition.json",
    "aws-ec2-transitgatewayroutetablepropagation.json",
    "aws-apigateway-basepathmapping.json",
    "aws-guardduty-filter.json",
    "aws-ecs-service.json",
    "aws-ram-resourceshare.json",
    "aws-dynamodb-table.json",
    "aws-ec2-securitygroupegress.json",
    "aws-config-organizationconfigrule.json",
    "aws-config-configurationrecorder.json",
    "aws-greengrass-devicedefinition.json",
    "aws-appconfig-extensionassociation.json",
    "aws-iot-topicruledestination.json",
    "aws-ec2-vpcdhcpoptionsassociation.json",
    "aws-apigateway-model.json",
    "aws-apigatewayv2-integrationresponse.json",
    "aws-iotevents-input.json",
    "aws-ec2-networkacl.json",
    "aws-budgets-budgetsaction.json",
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
    "aws-gamelift-fleet.json",
    "aws-datasync-locationfsxwindows.json",
    "aws-gamelift-build.json",
    "aws-apigateway-requestvalidator.json",
    "aws-autoscaling-warmpool.json",
    "aws-applicationautoscaling-scalabletarget.json",
    "aws-apigatewayv2-model.json",
    "aws-cassandra-keyspace.json",
    "aws-apigateway-domainname.json",
    "aws-ecs-primarytaskset.json",
    "aws-autoscaling-autoscalinggroup.json",
    "aws-wafv2-regexpatternset.json",
    "aws-eks-fargateprofile.json",
    "aws-ec2-transitgatewayroutetable.json",
    "aws-route53-recordset.json",
    "aws-iotanalytics-datastore.json",
    "aws-elasticache-securitygroup.json",
    "aws-opsworks-layer.json",
    "aws-kinesisfirehose-deliverystream.json",
    "aws-sagemaker-coderepository.json",
    "aws-imagebuilder-component.json",
    "aws-iotanalytics-channel.json",
    "aws-glue-connection.json",
    "aws-iam-group.json",
    "aws-wafregional-webaclassociation.json",
    "aws-ec2-transitgatewaymulticastgroupsource.json",
    "aws-transfer-profile.json",
    "aws-databrew-recipe.json",
    "aws-gamelift-alias.json",
    "aws-apigateway-usageplankey.json",
    "aws-fms-policy.json",
    "aws-greengrass-functiondefinition.json",
    "aws-cloudfront-realtimelogconfig.json",
    "aws-sagemaker-pipeline.json",
    "aws-lakeformation-datacellsfilter.json",
    "aws-datasync-locationhdfs.json",
    "aws-iotsitewise-portal.json",
    "aws-events-archive.json",
    "aws-msk-cluster.json",
    "aws-ec2-vpcendpointconnectionnotification.json",
    "aws-codepipeline-pipeline.json",
    "aws-opsworks-instance.json",
    "aws-imagebuilder-imagepipeline.json",
    "aws-elasticloadbalancingv2-listenercertificate.json",
    "aws-cloudformation-moduleversion.json",
    "aws-cloud9-environmentec2.json",
    "aws-route53resolver-resolverruleassociation.json",
    "aws-greengrass-connectordefinitionversion.json",
    "aws-synthetics-canary.json",
    "aws-sns-subscription.json",
    "aws-ec2-natgateway.json",
    "aws-greengrass-connectordefinition.json",
    "aws-transfer-workflow.json",
    "aws-appconfig-deploymentstrategy.json",
    "aws-glue-devendpoint.json",
    "aws-sagemaker-modelpackage.json",
    "aws-elasticache-usergroup.json",
    "aws-imagebuilder-imagerecipe.json",
    "aws-apigateway-restapi.json",
    "aws-opsworks-elasticloadbalancerattachment.json",
    "aws-s3objectlambda-accesspointpolicy.json",
    "aws-elasticache-replicationgroup.json",
    "aws-cassandra-table.json",
    "aws-rds-globalcluster.json",
    "aws-cloudformation-moduledefaultversion.json",
    "aws-ce-costcategory.json",
    "aws-glue-job.json",
    "aws-servicecatalog-cloudformationprovisionedproduct.json",
    "aws-glue-table.json",
    "aws-logs-metricfilter.json",
    "aws-lambda-function.json",
    "aws-sns-topic.json",
    "aws-datasync-locationfsxlustre.json",
    "aws-sagemaker-app.json",
    "aws-ec2-vpcgatewayattachment.json",
    "aws-cloudtrail-trail.json",
    "aws-gamelift-gameservergroup.json",
    "aws-ec2-internetgateway.json",
    "aws-ec2-gatewayroutetableassociation.json",
    "aws-wafv2-ipset.json",
    "aws-greengrass-subscriptiondefinition.json",
    "aws-greengrass-group.json",
    "aws-ssm-document.json",
    "aws-iam-role.json",
    "aws-iotsitewise-project.json",
    "aws-cloudfront-cloudfrontoriginaccessidentity.json",
    "aws-apigateway-apikey.json",
    "aws-autoscaling-launchconfiguration.json",
    "aws-apigateway-clientcertificate.json",
    "aws-kinesisanalyticsv2-application.json",
    "aws-lambda-alias.json",
    "aws-waf-ipset.json",
    "aws-ec2-transitgatewaymulticastdomainassociation.json",
    "aws-waf-sizeconstraintset.json",
    "aws-ec2-transitgatewayroutetableassociation.json",
    "aws-appconfig-environment.json",
    "aws-imagebuilder-image.json",
    "aws-elasticache-securitygroupingress.json",
    "aws-wafregional-xssmatchset.json",
    "aws-rds-dbproxytargetgroup.json",
    "aws-cloudwatch-dashboard.json",
    "aws-cloudwatch-alarm.json",
    "aws-guardduty-member.json",
    "aws-cloudformation-customresource.json",
    "aws-kinesisanalytics-applicationoutput.json",
    "aws-wafv2-rulegroup.json",
    "aws-elasticache-parametergroup.json",
    "aws-glue-classifier.json",
    "aws-codedeploy-deploymentgroup.json",
    "aws-cloudformation-stackset.json",
    "aws-ec2-route.json",
    "aws-codecommit-repository.json",
    "aws-iot-resourcespecificlogging.json",
    "aws-servicecatalog-launchtemplateconstraint.json",
    "aws-wafv2-loggingconfiguration.json",
    "aws-dynamodb-globaltable.json",
    "aws-backup-backupplan.json",
    "aws-imagebuilder-distributionconfiguration.json",
    "aws-lakeformation-permissions.json",
    "aws-cloudfront-publickey.json",
    "aws-ram-permission.json",
    "aws-datasync-task.json",
    "aws-ecs-taskdefinition.json",
    "aws-sagemaker-model.json",
    "aws-appsync-functionconfiguration.json",
    "aws-ec2-spotfleet.json",
    "aws-glue-schemaversion.json",
    "aws-iot-policyprincipalattachment.json",
    "aws-msk-batchscramsecret.json",
    "aws-dms-certificate.json",
    "aws-s3-bucket.json",
    "aws-guardduty-ipset.json",
    "aws-servicediscovery-httpnamespace.json",
    "aws-emr-securityconfiguration.json",
    "aws-cloudwatch-insightrule.json",
    "aws-apigateway-usageplan.json",
    "aws-batch-schedulingpolicy.json",
    "aws-iot-authorizer.json",
    "aws-apigatewayv2-vpclink.json",
    "aws-iot-jobtemplate.json",
    "aws-databrew-project.json",
    "aws-athena-workgroup.json",
    "aws-sagemaker-imageversion.json",
    "aws-apigatewayv2-api.json",
    "aws-servicecatalog-portfolioshare.json",
    "aws-iam-servercertificate.json",
    "aws-iot-securityprofile.json",
    "aws-events-eventbus.json",
    "aws-ssm-maintenancewindowtarget.json",
    "aws-apigateway-authorizer.json",
    "aws-iam-policy.json",
    "aws-databrew-schedule.json",
    "aws-rds-dbsecuritygroupingress.json",
    "aws-iotevents-detectormodel.json",
    "aws-ec2-transitgatewaymulticastgroupmember.json",
    "aws-ec2-volumeattachment.json",
    "aws-glue-securityconfiguration.json",
    "aws-databrew-ruleset.json",
    "aws-gamelift-matchmakingconfiguration.json",
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
    "aws-efs-filesystem.json",
    "aws-logs-querydefinition.json",
    "aws-iam-instanceprofile.json",
    "aws-datasync-locationnfs.json",
    "aws-kinesisanalyticsv2-applicationoutput.json",
    "aws-sagemaker-domain.json",
    "aws-greengrass-coredefinitionversion.json",
    "aws-certificatemanager-certificate.json",
    "aws-glue-schemaversionmetadata.json",
    "aws-sdb-domain.json",
    "aws-ec2-subnetroutetableassociation.json",
    "aws-sagemaker-notebookinstancelifecycleconfig.json",
    "aws-imagebuilder-containerrecipe.json",
    "aws-efs-accesspoint.json",
    "aws-redshift-clustersecuritygroupingress.json",
    "aws-elasticloadbalancingv2-loadbalancer.json",
    "aws-opensearchservice-domain.json",
    "aws-servicediscovery-instance.json",
    "aws-elasticsearch-domain.json",
    "aws-personalize-solution.json",
    "aws-apigatewayv2-deployment.json",
    "aws-servicecatalog-stacksetconstraint.json",
    "aws-ec2-networkinterfacepermission.json",
    "aws-servicecatalog-tagoption.json",
    "aws-servicediscovery-privatednsnamespace.json",
    "aws-servicecatalog-launchroleconstraint.json",
    "aws-iot-rolealias.json",
    "aws-secretsmanager-resourcepolicy.json",
    "aws-config-configrule.json",
    "aws-ecs-taskset.json",
    "aws-appsync-apikey.json",
    "aws-guardduty-threatintelset.json",
    "aws-ec2-vpc.json",
    "aws-iotsitewise-asset.json",
    "aws-dms-replicationsubnetgroup.json",
    "aws-route53-recordsetgroup.json",
    "aws-iotsitewise-accesspolicy.json",
    "aws-opsworks-app.json",
    "aws-kinesis-stream.json",
    "aws-greengrass-coredefinition.json",
    "aws-batch-jobdefinition.json",
    "aws-iam-samlprovider.json",
    "aws-cloudfront-keygroup.json",
    "aws-ec2-networkinterfaceattachment.json",
    "aws-ec2-transitgatewayattachment.json",
    "aws-codedeploy-deploymentconfig.json",
    "aws-neptune-dbcluster.json",
    "aws-waf-bytematchset.json",
    "aws-dms-replicationtask.json",
    "aws-ec2-routetable.json",
    "aws-rds-dbproxyendpoint.json",
    "aws-datasync-locationsmb.json",
    "aws-glue-trigger.json",
    "aws-ec2-vpcpeeringconnection.json",
    "aws-sns-topicpolicy.json",
    "aws-elasticache-globalreplicationgroup.json",
    "aws-kms-key.json",
    "aws-route53resolver-firewallrulegroupassociation.json",
    "aws-route53resolver-resolverqueryloggingconfig.json",
    "aws-ec2-subnet.json",
    "aws-s3objectlambda-accesspoint.json",
    "aws-waf-rule.json",
    "aws-elasticbeanstalk-configurationtemplate.json",
    "aws-sqs-queuepolicy.json",
    "aws-appsync-apicache.json",
    "aws-apigateway-account.json",
    "aws-wafv2-webacl.json",
    "aws-ec2-transitgatewayconnect.json",
    "aws-ec2-securitygroup.json",
    "aws-opsworks-volume.json",
    "aws-iam-usertogroupaddition.json",
    "aws-events-rule.json",
    "aws-gamelift-gamesessionqueue.json",
    "aws-databrew-dataset.json",
    "aws-ec2-vpngatewayroutepropagation.json",
    "aws-apigateway-method.json",
    "aws-wafregional-regexpatternset.json",
    "aws-ssm-patchbaseline.json",
    "aws-servicediscovery-service.json",
    "aws-iotevents-alarmmodel.json",
    "aws-efs-mounttarget.json",
    "aws-waf-webacl.json",
    "aws-servicediscovery-publicdnsnamespace.json",
    "aws-iam-user.json",
    "aws-emr-instancegroupconfig.json",
    "aws-stepfunctions-activity.json",
    "aws-s3-bucketpolicy.json",
    "aws-appsync-graphqlschema.json",
    "aws-iot-custommetric.json",
    "aws-codebuild-sourcecredential.json",
    "aws-emr-instancefleetconfig.json",
    "aws-emr-cluster.json",
    "aws-apigatewayv2-domainname.json",
    "aws-servicecatalog-resourceupdateconstraint.json",
    "aws-transfer-agreement.json",
    "aws-cloudfront-distribution.json",
    "aws-elasticache-subnetgroup.json",
    "aws-oam-link.json",
    "aws-iot-domainconfiguration.json",
    "aws-sagemaker-endpoint.json",
    "aws-iotanalytics-dataset.json",
    "aws-redshift-clustersecuritygroup.json",
    "aws-route53-cidrcollection.json",
    "aws-glue-mltransform.json",
    "aws-appconfig-hostedconfigurationversion.json",
    "aws-datasync-locationefs.json",
    "aws-apigateway-resource.json",
    "aws-sagemaker-appimageconfig.json",
    "aws-elasticloadbalancingv2-targetgroup.json",
    "aws-applicationautoscaling-scalingpolicy.json",
    "aws-iotsitewise-gateway.json",
    "aws-cloudformation-macro.json",
    "aws-sagemaker-workteam.json",
    "aws-lambda-layerversionpermission.json",
    "aws-secretsmanager-secret.json",
    "aws-elasticache-user.json",
    "aws-sagemaker-image.json",
    "aws-codedeploy-application.json",
    "aws-dms-eventsubscription.json",
    "aws-lakeformation-principalpermissions.json",
    "aws-datasync-locations3.json",
    "aws-autoscaling-lifecyclehook.json",
    "aws-fsx-datarepositoryassociation.json",
    "aws-ec2-networkinterface.json",
    "aws-sagemaker-featuregroup.json",
    "aws-appsync-resolver.json",
    "aws-route53resolver-resolverqueryloggingconfigassociation.json",
    "aws-lambda-eventinvokeconfig.json",
    "aws-lambda-layerversion.json",
    "aws-rds-optiongroup.json",
    "aws-opsworks-userprofile.json",
    "aws-glue-schema.json",
    "aws-iot-policy.json",
    "aws-ssm-maintenancewindow.json",
    "aws-lakeformation-tagassociation.json",
    "aws-greengrassv2-componentversion.json",
    "aws-imagebuilder-infrastructureconfiguration.json",
    "aws-iot-logging.json",
    "aws-cloudformation-waitcondition.json",
    "aws-route53resolver-resolverendpoint.json",
    "aws-iot-scheduledaudit.json",
    "aws-sagemaker-notebookinstance.json",
    "aws-iotsitewise-dashboard.json",
    "aws-wafregional-bytematchset.json",
    "aws-cloudwatch-anomalydetector.json",
    "aws-ec2-subnetnetworkaclassociation.json",
    "aws-iot-mitigationaction.json",
    "aws-secretsmanager-rotationschedule.json",
    "aws-lambda-permission.json",
    "aws-eks-identityproviderconfig.json",
    "aws-appsync-graphqlapi.json",
    "aws-gamelift-matchmakingruleset.json",
    "aws-ec2-egressonlyinternetgateway.json",
    "aws-ec2-vpccidrblock.json",
    "aws-gamelift-script.json",
    "aws-iam-virtualmfadevice.json",
    "aws-athena-preparedstatement.json",
    "aws-autoscaling-scheduledaction.json",
    "aws-apigatewayv2-route.json",
    "aws-lakeformation-resource.json",
    "aws-ec2-vpcendpoint.json",
    "aws-personalize-datasetgroup.json",
    "aws-rds-eventsubscription.json",
    "aws-datasync-agent.json",
    "aws-iot-dimension.json",
    "aws-ec2-placementgroup.json",
    "aws-organizations-account.json",
    "aws-ecr-repository.json",
    "aws-iot-fleetmetric.json",
    "aws-greengrass-subscriptiondefinitionversion.json",
    "aws-appconfig-extension.json",
    "aws-glue-registry.json",
    "aws-ec2-keypair.json",
    "aws-fsx-filesystem.json",
    "aws-ec2-eipassociation.json",
    "aws-iotanalytics-pipeline.json",
    "aws-elasticbeanstalk-application.json",
    "aws-iot-thingprincipalattachment.json",
    "aws-dlm-lifecyclepolicy.json",
    "aws-ec2-capacityreservation.json",
    "aws-elasticloadbalancing-loadbalancer.json",
    "aws-transfer-user.json",
    "aws-ec2-trafficmirrortarget.json",
    "aws-rds-dbclusterparametergroup.json",
    "aws-waf-xssmatchset.json",
    "aws-config-remediationconfiguration.json",
    "aws-greengrass-loggerdefinition.json",
    "aws-greengrass-devicedefinitionversion.json",
    "aws-athena-datacatalog.json",
    "aws-greengrass-functiondefinitionversion.json",
    "aws-glue-workflow.json",
    "aws-apigatewayv2-authorizer.json",
    "aws-iot-accountauditconfiguration.json",
    "aws-sagemaker-userprofile.json",
    "aws-personalize-dataset.json",
    "aws-ec2-prefixlist.json",
    "aws-ec2-instance.json",
    "aws-ec2-subnetcidrblock.json",
    "aws-elasticbeanstalk-applicationversion.json",
    "aws-waf-sqlinjectionmatchset.json",
    "aws-ec2-transitgatewayvpcattachment.json",
    "aws-ec2-flowlog.json",
    "aws-amazonmq-broker.json",
    "aws-emr-step.json",
    "aws-ssm-association.json",
    "aws-cloudfront-responseheaderspolicy.json",
    "aws-route53resolver-resolverrule.json",
    "aws-transfer-connector.json",
    "aws-apigateway-documentationversion.json",
    "aws-wafv2-webaclassociation.json",
    "aws-oam-sink.json",
    "aws-codebuild-reportgroup.json",
    "aws-apigateway-gatewayresponse.json",
    "aws-workspaces-workspace.json",
    "aws-emr-studio.json",
    "aws-directoryservice-microsoftad.json",
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
    "aws-iot-provisioningtemplate.json",
    "aws-personalize-schema.json",
    "aws-apigateway-stage.json",
    "aws-budgets-budget.json",
    "aws-batch-computeenvironment.json",
    "aws-iot-thing.json",
    "aws-events-eventbuspolicy.json",
    "aws-ec2-trafficmirrorfilter.json",
    "aws-apigateway-deployment.json",
    "aws-lakeformation-datalakesettings.json",
    "aws-greengrassv2-deployment.json",
    "aws-autoscaling-scalingpolicy.json",
    "aws-rds-dbsecuritygroup.json",
    "aws-apigatewayv2-routeresponse.json",
    "aws-ssm-parameter.json",
    "aws-apigatewayv2-apigatewaymanagedoverrides.json",
    "aws-config-deliverychannel.json",
    "aws-certificatemanager-account.json",
    "aws-sagemaker-monitoringschedule.json",
    "aws-iam-oidcprovider.json",
    "aws-lakeformation-tag.json",
    "aws-ec2-vpngateway.json",
    "aws-cloudformation-stack.json",
    "aws-resourcegroups-group.json",
    "aws-cloudformation-resourcedefaultversion.json",
    "aws-greengrass-loggerdefinitionversion.json",
    "aws-databrew-job.json",
    "aws-ec2-transitgatewaypeeringattachment.json",
    "aws-cloudfront-cachepolicy.json",
    "aws-iam-accesskey.json",
    "aws-rds-dbsubnetgroup.json",
    "aws-amazonmq-configuration.json",
    "aws-appconfig-deployment.json",
    "aws-codepipeline-customactiontype.json",
    "aws-accessanalyzer-analyzer.json",
    "aws-ec2-ec2fleet.json",
    "aws-greengrass-resourcedefinition.json",
    "aws-dms-replicationinstance.json",
    "aws-servicecatalog-cloudformationproduct.json",
    "aws-iam-managedpolicy.json",
    "aws-ec2-launchtemplate.json",
    "aws-elasticbeanstalk-environment.json",
    "aws-wafregional-sqlinjectionmatchset.json",
    "aws-lambda-version.json",
    "aws-ec2-dhcpoptions.json",
    "aws-kinesis-streamconsumer.json",
    "aws-iam-servicelinkedrole.json",
    "aws-ec2-volume.json",
    "aws-iot-certificate.json",
    "aws-ec2-eip.json",
    "aws-greengrass-resourcedefinitionversion.json",
    "aws-cloudformation-resourceversion.json",
    "aws-apigatewayv2-stage.json",
    "aws-rds-dbproxy.json",
    "aws-rds-dbparametergroup.json",
    "aws-securityhub-hub.json",
    "aws-s3-accesspoint.json",
    "aws-greengrass-groupversion.json",
    "aws-batch-jobqueue.json",
    "aws-cloudformation-waitconditionhandle.json",
    "aws-eks-addon.json",
]
