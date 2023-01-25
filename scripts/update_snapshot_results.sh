#!/usr/bin/env bash

dir="test/fixtures"

# public/
cfn-lint ${dir}/templates/public/lambda-poller.yaml -e -c I --format json > ${dir}/results/public/lambda-poller.json
cfn-lint ${dir}/templates/public/watchmaker.json -e -c I --format json > ${dir}/results/public/watchmaker.json

# quickstart/non_strict/
cfn-lint ${dir}/templates/quickstart/cis_benchmark.yaml -e -c I --format json > ${dir}/results/quickstart/non_strict/cis_benchmark.json
cfn-lint ${dir}/templates/quickstart/nist_application.yaml -e -c I --format json > ${dir}/results/quickstart/non_strict/nist_application.json
cfn-lint ${dir}/templates/quickstart/nist_high_main.yaml -e -c I --format json > ${dir}/results/quickstart/non_strict/nist_high_main.json
cfn-lint ${dir}/templates/quickstart/openshift.yaml -e -c I --format json > ${dir}/results/quickstart/non_strict/openshift.json

# quickstart/
cfn-lint ${dir}/templates/quickstart/cis_benchmark.yaml -e -c I --format json -x E3012:strict=true > ${dir}/results/quickstart/cis_benchmark.json
cfn-lint ${dir}/templates/quickstart/nist_application.yaml -e -c I --format json -x E3012:strict=true > ${dir}/results/quickstart/nist_application.json 
cfn-lint ${dir}/templates/quickstart/nist_config_rules.yaml -e -c I --format json -x E3012:strict=true > ${dir}/results/quickstart/nist_config_rules.json
cfn-lint ${dir}/templates/quickstart/nist_high_main.yaml -e -c I --format json -x E3012:strict=true > ${dir}/results/quickstart/nist_high_main.json
cfn-lint ${dir}/templates/quickstart/nist_iam.yaml -e -c I --format json -x E3012:strict=true > ${dir}/results/quickstart/nist_iam.json
cfn-lint ${dir}/templates/quickstart/nist_logging.yaml -e -c I --format json -x E3012:strict=true > ${dir}/results/quickstart/nist_logging.json
cfn-lint ${dir}/templates/quickstart/nist_vpc_management.yaml -e -c I --format json -x E3012:strict=true > ${dir}/results/quickstart/nist_vpc_management.json
cfn-lint ${dir}/templates/quickstart/nist_vpc_production.yaml -e -c I --format json -x E3012:strict=true > ${dir}/results/quickstart/nist_vpc_production.json
cfn-lint ${dir}/templates/quickstart/openshift.yaml -e -c I --format json -x E3012:strict=true > ${dir}/results/quickstart/openshift.json
cfn-lint ${dir}/templates/quickstart/openshift_master.yaml -e -c I --format json -x E3012:strict=true > ${dir}/results/quickstart/openshift_master.json
