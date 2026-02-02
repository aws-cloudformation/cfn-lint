# Validate and Update Smithy Service Name Mappings

## Context

The `scripts/smithy/_automated_patches.py` file contains a `renamer()` function that maps Smithy service names to CloudFormation service names. When service name mappings are incorrect or missing, resources won't get Smithy patches generated.

## Current State

After migration, we have:
- **~600 resources** with smithy.json patches
- **~9 resources** with only boto patches (legacy/discontinued services - acceptable)
- **35 resources** with manual.json patches (for schema flattening issues)

## Task

When new AWS services are added or service name mappings are missing:

1. **Identify missing mappings**: Run comparison to find resources without smithy patches
2. **Find correct Smithy service names**: Check the Smithy models directory
3. **Update the renamer function**: Add the correct mapping
4. **Re-run and verify**: Confirm patches are generated

## Files

- `scripts/smithy/_automated_patches.py` - Contains the `renamer()` function
- `scripts/smithy/detailed_comparison.py` - Shows patch coverage
- `scripts/smithy/identify_missing_patches.py` - Identifies boto patches not in smithy
- https://github.com/aws/api-models-aws - Smithy models repository (clone locally to check service names)

## Common Mapping Patterns

| CloudFormation Service | Boto Name | Smithy Name |
|------------------------|-----------|-------------|
| ApiGateway | apigateway | api-gateway |
| AutoScaling | autoscaling | auto-scaling |
| AutoScalingPlans | autoscalingplans | auto-scaling-plans |
| CertificateManager | acm | acm |
| Config | config | config-service |
| CostExplorer | ce | cost-explorer |
| CloudWatchEvents | events | cloudwatch-events |
| CloudWatchLogs | logs | cloudwatch-logs |
| StepFunctions | stepfunctions | sfn |

## Steps

### 1. Check current coverage
```bash
cd /Users/kddejong/code/github.com/aws-cloudformation/cfn-lint
python scripts/smithy/detailed_comparison.py
```

### 2. Find Smithy service name
```bash
# Clone the Smithy models repo if needed
git clone https://github.com/aws/api-models-aws.git /tmp/api-models-aws

# List all Smithy services
ls /tmp/api-models-aws/models/ | grep -i <service-keyword>

# Or browse online: https://github.com/aws/api-models-aws/tree/main/models
```

### 3. Update renamer function

Edit `scripts/smithy/_automated_patches.py`:

```python
def renamer(name):
    """Map Smithy service names to CloudFormation service names"""
    manual_fixes = {
        # Add new mapping:
        "smithy-service-name": "cloudformation-service-name",
    }
    if name in manual_fixes:
        return manual_fixes[name].lower()
    return name.replace("-", "").lower()
```

### 4. Re-run update script
```bash
python scripts/smithy/update_schemas_from_smithy.py
```

### 5. Verify patches created
```bash
ls src/cfnlint/data/schemas/patches/extensions/all/aws_<service>_<resource>/smithy.json
python scripts/smithy/detailed_comparison.py
```

## Handling Missing Patches

If boto has patches that smithy doesn't (due to schema flattening):

```bash
# Identify missing patches
python scripts/smithy/identify_missing_patches.py

# This creates/updates manual.json files automatically
# Review the changes and commit if appropriate
```

## Expected Outcome

- New service gets smithy.json patches
- Comparison shows resource in "BOTH" category
- Total smithy patches increase

## Legacy Services

These services don't exist in Smithy (acceptable):
- OpsWorks (maintenance mode)
- OpsWorks CM (maintenance mode)
- RoboMaker (discontinued)
- Lookout for Metrics (discontinued)
