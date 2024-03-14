"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.templates.LimitSize import LimitSize  # pylint: disable=E0401


def write_limit_test_templates():
    with open("test/fixtures/templates/bad/limit_numbers.yaml", "w") as f:
        f.write("Parameters:\n")
        for n in range(1, 202):
            f.write(
                "  Parameter"
                + str(n)
                + """:
    Type: String\n"""
            )
        f.write("Resources:\n")
        for n in range(1, 502):
            f.write(
                "  Resource"
                + str(n)
                + """:
    Type: AWS::SNS::Topic\n"""
            )
        f.write("Outputs:\n")
        for n in range(1, 202):
            f.write(
                "  Output"
                + str(n)
                + """:
    Value: !Ref Parameter1\n"""
            )
        f.write("Mappings:\n")
        for n in range(1, 202):
            f.write(
                "  Mapping"
                + str(n)
                + """:
    Key:
      Key: Value\n"""
            )
        for n in range(1, 202):
            f.write("      Key" + str(n) + ": Value\n")

    with open("test/fixtures/templates/bad/limit_size.yaml", "w") as f:
        f.write(
            """Description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In aliquet justo nibh, a venenatis justo suscipit et. Sed vulputate est non vulputate cursus. In et mollis nunc. Ut semper justo nec odio dignissim semper. Sed interdum elementum ante. Phasellus bibendum mattis ultrices. Nullam varius dui mi, ac fermentum ante sodales nec. Mauris id libero id turpis sollicitudin imperdiet. Praesent volutpat, elit ut malesuada ultricies, magna velit ullamcorper leo, sagittis pulvinar elit erat faucibus felis.
Morbi sagittis pretium ligula in tristique. Suspendisse odio lectus, condimentum eget egestas pharetra, elementum sit amet sapien. Nullam ipsum eros, ullamcorper ut mi nec, maximus sagittis lacus. In laoreet quam sit amet ante dictum efficitur. Praesent pellentesque purus sit amet nisl scelerisque feugiat. Phasellus feugiat, ex posuere pharetra eleifend, ipsum libero viverra est, sit amet sodales ipsum urna in quam. Donec sit amet pharetra nibh. Nulla eu fermentum leo, a venenatis urna. Nam ac sagittis magna volutpat."
Resources:\n"""
        )
        for n in range(1, 300):
            # ruff: noqa: E501
            f.write(
                "  Resource"
                + str(n)
                + """:
    Type: AWS::EC2::Instance
    Metadata:
      Comment: Install a Magento web serve
      AWS::CloudFormation::Authentication:
        S3AccessCreds:
          type: S3
          roleName: NewIamInstanceRole
      AWS::CloudFormation::Init:
        config:
          packages:
            yum:
              nfs-utils: []
              awslogs: []
          files:
            /etc/awslogs/awslogs.conf:
              content: !Sub |
                [general]
                state_file= /var/log/agent-state
                [/home/ec2-user/misc/install]
                file = /var/log/cloud-init-output.log
                log_group_name = MagentoMainLogGroup
                log_stream_name = magento/install.log
              mode: '000400'
              owner: root
              group: root
            /etc/awslogs/awscli.conf:
              content: !Sub |
                [plugins]
                cwlogs = cwlogs
                [default]
                region = ${AWS::Region}
              mode: '000400'
              owner: root
              group: root
            /etc/cfn/cfn-hup.conf:
              content: !Sub |
                [main]
                stack=${AWS::StackId}
                region=${AWS::Region}
              mode: '000400'
              owner: root
              group: root
            /etc/cfn/hooks.d/cfn-auto-reloader.conf:
              content: !Sub |
                [cfn-auto-reloader-hook]
                triggers=post.update
                path=Resources.LaunchConfig.Metadata.AWS::CloudFormation::Init
                action=/opt/aws/bin/cfn-init -v --stack ${AWS::StackName} --resource LaunchConfig --region ${AWS::Region}
                runas=root
            /install_magento.sh:
              source: !Sub https://quickstart-reference.s3.amazonaws.com/magento/latest/scripts/install_magento.sh
              mode: '000644'
              owner: root
              group: root
              authentication: S3AccessCreds
            /configure_magento.sh:
              source: !Sub https://quickstart-reference.s3.amazonaws.com/magento/latest/scripts/configure_magento.sh
              mode: '000644'
              owner: root
              group: root
              authentication: S3AccessCreds
            /home/ec2-user/magento.tar.gz:
              source: 'magento.tar.gz'
              mode: '000644'
              owner: root
              group: root
              authentication: S3AccessCreds
          services:
            sysvinit:
              cfn-hup:
                enabled: 'true'
                ensureRunning: 'true'
                files:
                - /etc/cfn/cfn-hup.conf
                - /etc/cfn/hooks.d/cfn-auto-reloader.conf
              awslogs:
                enabled: 'true'
                ensureRunning: 'true'
                files:
                - /etc/awslogs/awslogs.conf
                packages:
                  yum:
                  - awslogs
    Properties:
      ImageId: ami-ami
      InstanceType: t2.micro
      UserData:
        !Base64
          Fn::Sub: |
            #!/bin/bash
            /opt/aws/bin/cfn-init -v --stack ${AWS::StackName} --resource MagentoAMI  --region ${AWS::Region}
            chmod a+x install_magento.sh
            ./install_magento.sh /tmp/params.txt
      Tags:
      - Key: Application
        Value: AWS Quick Start (Magento)
      - Key: Name
        Value: MagentoAMI (AWS Quick Start)
"""
            )


class TestTemplateLimitSize(BaseRuleTestCase):
    """Test template limit size"""

    def setUp(self):
        """Setup"""
        super(TestTemplateLimitSize, self).setUp()
        self.collection.register(LimitSize())
        write_limit_test_templates()

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/limit_size.yaml", 1)
