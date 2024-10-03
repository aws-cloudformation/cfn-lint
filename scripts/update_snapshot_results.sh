#!/usr/bin/env bash

# integration/
cfn-lint test/fixtures/templates/integration/dynamic-references.yaml -e -c I --format json > test/fixtures/results/integration/dynamic-references.json
cfn-lint test/fixtures/templates/integration/resources-cloudformation-init.yaml -e -c I --format json > test/fixtures/results/integration/resources-cloudformation-init.json
cfn-lint test/fixtures/templates/integration/ref-no-value.yaml -e -c I --format json > test/fixtures/results/integration/ref-no-value.json
cfn-lint test/fixtures/templates/integration/availability-zones.yaml -e -c I --format json > test/fixtures/results/integration/availability-zones.json
cfn-lint test/fixtures/templates/integration/getatt-types.yaml -e -c I --format json > test/fixtures/results/integration/getatt-types.json
cfn-lint test/fixtures/templates/integration/aws-ec2-networkinterface.yaml -e -c I --format json > test/fixtures/results/integration/aws-ec2-networkinterface.json
cfn-lint test/fixtures/templates/integration/aws-ec2-instance.yaml -e -c I --format json > test/fixtures/results/integration/aws-ec2-instance.json
cfn-lint test/fixtures/templates/integration/aws-ec2-launchtemplate.yaml -e -c I --format json > test/fixtures/results/integration/aws-ec2-launchtemplate.json
cfn-lint test/fixtures/templates/integration/aws-ec2-subnet.yaml -e -c I --format json > test/fixtures/results/integration/aws-ec2-subnet.json
cfn-lint test/fixtures/templates/integration/aws-dynamodb-table.yaml -e -c I --format json > test/fixtures/results/integration/aws-dynamodb-table.json

# public/
cfn-lint test/fixtures/templates/public/lambda-poller.yaml -e -c I --format json > test/fixtures/results/public/lambda-poller.json
cfn-lint test/fixtures/templates/public/watchmaker.json -e -x E3012:strict=true -c I --format json > test/fixtures/results/public/watchmaker.json

# quickstart/non_strict/
cfn-lint test/fixtures/templates/quickstart/cis_benchmark.yaml -e -c I --format json > test/fixtures/results/quickstart/non_strict/cis_benchmark.json
cfn-lint test/fixtures/templates/quickstart/nist_application.yaml -e -c I --format json > test/fixtures/results/quickstart/non_strict/nist_application.json
cfn-lint test/fixtures/templates/quickstart/nist_high_main.yaml -e -c I --format json > test/fixtures/results/quickstart/non_strict/nist_high_main.json
cfn-lint test/fixtures/templates/quickstart/openshift.yaml -e -c I --format json > test/fixtures/results/quickstart/non_strict/openshift.json

# quickstart/
cfn-lint test/fixtures/templates/quickstart/cis_benchmark.yaml -e -c I --format json -x E3012:strict=true > test/fixtures/results/quickstart/cis_benchmark.json
cfn-lint test/fixtures/templates/quickstart/nist_application.yaml -e -c I --format json -x E3012:strict=true > test/fixtures/results/quickstart/nist_application.json
cfn-lint test/fixtures/templates/quickstart/nist_config_rules.yaml -e -c I --format json -x E3012:strict=true > test/fixtures/results/quickstart/nist_config_rules.json
cfn-lint test/fixtures/templates/quickstart/nist_high_main.yaml -e -c I --format json -x E3012:strict=true > test/fixtures/results/quickstart/nist_high_main.json
cfn-lint test/fixtures/templates/quickstart/nist_iam.yaml -e -c I --format json -x E3012:strict=true > test/fixtures/results/quickstart/nist_iam.json
cfn-lint test/fixtures/templates/quickstart/nist_logging.yaml -e -c I --format json -x E3012:strict=true > test/fixtures/results/quickstart/nist_logging.json
cfn-lint test/fixtures/templates/quickstart/nist_vpc_management.yaml -e -c I --format json -x E3012:strict=true > test/fixtures/results/quickstart/nist_vpc_management.json
cfn-lint test/fixtures/templates/quickstart/nist_vpc_production.yaml -e -c I --format json -x E3012:strict=true > test/fixtures/results/quickstart/nist_vpc_production.json
cfn-lint test/fixtures/templates/quickstart/openshift.yaml -e -c I --format json -x E3012:strict=true > test/fixtures/results/quickstart/openshift.json
cfn-lint test/fixtures/templates/quickstart/openshift_master.yaml -e -c I --format json -x E3012:strict=true > test/fixtures/results/quickstart/openshift_master.json
