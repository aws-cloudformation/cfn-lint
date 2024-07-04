## Customize specifications
The linter follows the [CloudFormation specifications](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.html) by default. However, for your use case specific requirements might exist. For example, within your organisation it might be mandatory to use [Tagging](https://aws.amazon.com/answers/account-management/aws-tagging-strategies/).

The linter provides the possibility to implement these customized specifications using the `--override-spec` argument. This argument should pass a (JSON) file in the same format as the [Specification](/src/cfnlint/data) files, this file is then merged into the Regional specification files that are used to process all the linting rules.

This makes it easy to apply your our rules on top of the CloudFormation rules without having to write your own checks in Python and use the power of the linter itself with a single file!

### Features
The `--override-spec` functionality currently supports the following features:

#### Include/Exclude resources
If you want to block the use of specific resources, you can easily disable them by using the Include/Exclude features. This can be done by specifying a list of `IncludedResourceTypes` and/or `ExcludedResourceTypes`.

* `IncludedResourceTypes`: List of resources that are supported. If specified, all resources that are not in this list are not allowed.
* `ExcludedResourceTypes`: List of resources that are not supported. Resources in this list are not allowed.

Wildcards (`*`) are supported in these lists, so `AWS::EC2::*` allows ALL EC2 ResourceTypes. Both lists can work in conjunction with each other.

The following example only allows the usage of all `EC2` resources, except for `AWS::EC2::SpotFleet`:

```json
{
  "IncludeResourceTypes": [
    "AWS::EC2::*"
  ],
  "ExcludeResourceTypes": [
    "AWS::EC2::SpotFleet"
  ]
}
```

#### Alter Resource/Parameter specifications
CloudFormation schemas can be patched to change the behavior of how a property works. This can be amazingly useful if you want to require certain properties or add extra validation to a property. You can create a patch by specifying `Patches` at the root, then the resource type you want to patch, followed by a list of patches in [json patch](https://jsonpatch.com/) format.

For example, to enforce tagging on an S3 bucket, the override file looks like this:

```json
{
  "Patches": {
    "AWS::S3::Bucket": [
      {
        "op": "add",
        "path": "/required",
        "value": [
          "Tags"
        ]
      }
    ]
  }
}
```

**WARNING**
JSON patches will fail if they don't apply the schema. Schema structure can change without changing how customers use the resource type. These changes may result in your patch breaking the cfn-lint process.

**WARNING**
You can patch the schemas so the result is a non properly structured schema. For instance if you patch `/required` to have a value of `{}` cfn-lint will crash many ways as it is expecting an array. We test the schemas on each release to validate their structure before doing a release. We do not test them after you apply your patches.
