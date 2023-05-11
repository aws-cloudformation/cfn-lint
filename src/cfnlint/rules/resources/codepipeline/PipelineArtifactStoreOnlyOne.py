"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class PipelineArtifactStoreOnlyOne(BaseCfnSchema):
    id = "E3626"
    shortdesc = "Validate codepipeline artifacts only use Store or Stores"
    description = "Specify only 'ArtifactStore' or 'ArtifactStores'"
    tags = ["resources"]
    schema_path = "aws_codepipeline_pipeline/artifactstore_onlyone"
