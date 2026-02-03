# Smithy-based Schema Patches

This directory contains scripts to extract validation patches from AWS Smithy API models instead of botocore.

## Why Smithy?

The [AWS API Models repository](https://github.com/aws/api-models-aws) provides official Smithy models for all public AWS services. These are:
- **More authoritative**: Maintained directly by AWS service teams
- **More complete**: Designed as the source of truth for AWS APIs
- **Future-proof**: Smithy is AWS's standard IDL going forward
- **Source of botocore**: Botocore likely generates its models from these Smithy definitions

## Structure

```
smithy/
├── _automated_patches.py    # Core logic to extract patches from Smithy models
├── _helpers.py               # Helper functions for schema loading
├── _types.py                 # Type definitions
├── update_schemas_from_smithy.py  # Main script to download and process
└── test_smithy_parsing.py    # Test script to verify parsing
```

## What Gets Extracted

From Smithy models, we extract:

1. **Enum values** - From `enum` type shapes via `smithy.api#enumValue` traits
2. **String/List length** - From `smithy.api#length` trait (min/max)
3. **Number ranges** - From `smithy.api#range` trait (min/max)
4. **Patterns** - From `smithy.api#pattern` trait

## Usage

### Run the update script

```bash
cd scripts/smithy
python update_schemas_from_smithy.py
```

This will:
1. Download the latest Smithy models from GitHub
2. Download CloudFormation schemas
3. Extract patches and save to `src/cfnlint/data/schemas/patches/extensions/all/<resource>/smithy.json`

### Test parsing

```bash
# First clone the repo
git clone https://github.com/aws/api-models-aws /tmp/api-models-aws

# Run test
python test_smithy_parsing.py
```

## Smithy Model Structure

Smithy models use JSON AST format:

```json
{
  "smithy": "2.0",
  "shapes": {
    "com.amazonaws.ec2#InstanceType": {
      "type": "enum",
      "members": {
        "t2_micro": {
          "target": "smithy.api#Unit",
          "traits": {
            "smithy.api#enumValue": "t2.micro"
          }
        }
      }
    },
    "com.amazonaws.ec2#RunInstances": {
      "type": "operation",
      "input": {
        "target": "com.amazonaws.ec2#RunInstancesRequest"
      }
    }
  }
}
```

## Differences from Botocore Approach

| Aspect | Botocore | Smithy |
|--------|----------|--------|
| Enum format | Direct array | Nested members with traits |
| Constraints | Direct properties | Smithy traits |
| File naming | `service-2.json` | `<service>-<version>.json` |
| Output file | `boto.json` | `smithy.json` |

## Migration Notes

- Both `boto.json` and `smithy.json` can coexist
- Smithy patches take precedence if both exist
- Service name mappings may differ slightly (e.g., `elastic-load-balancing-v2` vs `elbv2`)

## Service Name Mapping

Some services need manual mapping from Smithy names to CloudFormation names:

```python
manual_fixes = {
    "acm": "CertificateManager",
    "mq": "AmazonMQ",
    "kafka": "MSK",
    "firehose": "KinesisFirehose",
    "elasticsearch-service": "ElasticSearch",
    "elastic-load-balancing-v2": "ElasticLoadBalancingV2",
    "elastic-load-balancing": "ElasticLoadBalancing",
    "directory-service": "DirectoryService",
}
```

## Troubleshooting

### No patches generated

Check:
1. Service name mapping is correct
2. CloudFormation resource files exist for the service
3. Create operations are found in the CloudFormation schema
4. Smithy model file exists and is valid JSON

### Missing enum values

Check:
1. The shape is actually an `enum` type in Smithy
2. Members have `smithy.api#enumValue` traits
3. The property path matches between CloudFormation schema and Smithy model

### Pattern compilation errors

Some Smithy patterns may not be valid regex. These are logged and skipped.

## Future Improvements

- [ ] Add support for manual patches (like `_manual_patches.py` in boto)
- [ ] Better service name auto-detection
- [ ] Parallel processing of services
- [ ] Incremental updates (only changed services)
- [ ] Validation against existing boto patches
