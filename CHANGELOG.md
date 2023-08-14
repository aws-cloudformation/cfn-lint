### v0.79.7
###### CloudFormation Specifications
- Add region `il-central-1` (pull #[2836](https://github.com/aws-cloudformation/cfn-lint/pull/2836))
- Update CloudFormation specs to `135.0.0` (pull #[2837](https://github.com/aws-cloudformation/cfn-lint/pull/2837))
###### Fixes
- Allow for `RetainExceptOnCreate` for `DeletionPolicy` (pull #[2834](https://github.com/aws-cloudformation/cfn-lint/pull/2834))
- Fix language extension transform to resolve foreach refs in Sub parameters (pull #[2846](https://github.com/aws-cloudformation/cfn-lint/pull/2846))
- Fix language extension transform to allow `Fn::FindInMap` to return arrays (pull #[2845](https://github.com/aws-cloudformation/cfn-lint/pull/2845))

### v0.79.6
###### CloudFormation Specifications
- Fix `AWS::Glue::Job.Name` to use string min/max instead of number min/max (pull #[2831](https://github.com/aws-cloudformation/cfn-lint/pull/2831))

### v0.79.5
###### CloudFormation Specifications
- Update schema to spec conversions to include include a default string minimum value of 0 if not specified (pull #[2824](https://github.com/aws-cloudformation/cfn-lint/pull/2824))
- Update CloudFormation specs to `132.0.0` (pull #[2824](https://github.com/aws-cloudformation/cfn-lint/pull/2824))
###### Fixes
- Fix `AWS::LanguageExtensions` to not empty out a hardcoded string `Fn::FindInmap` that cannot be resolved (pull #[2827](https://github.com/aws-cloudformation/cfn-lint/pull/2827))

### v0.79.4
###### Fixes
- Fix `AWS::LanguageExtensions` to not fully resolve `Fn::FindInMap` unless in `Fn::ForEach` collection (pull #[2822](https://github.com/aws-cloudformation/cfn-lint/pull/2822))
- Update `convert_dict` to include `Mark` instead of tuple for default value (pull #[2821](https://github.com/aws-cloudformation/cfn-lint/pull/2821))

### v0.79.3
###### Fixes
- Fix `Conditions` logic to not crash on a condition that isn't found (pull #[2814](https://github.com/aws-cloudformation/cfn-lint/pull/2814))
- Update rule [E1011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1011) to better handle `Fn::FindInMap` with `AWS::LanguageExtensions` (pull #[2814](https://github.com/aws-cloudformation/cfn-lint/pull/2814))
- Update rule [W2001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2001) to better handle `Ref` with `AWS::LanguageExtensions` (pull #[2814](https://github.com/aws-cloudformation/cfn-lint/pull/2814))

### v0.79.2
###### Features
- Add rule [E1032](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1032) to validate ForEach with transform (pull #[2809](https://github.com/aws-cloudformation/cfn-lint/pull/2809))
###### Fixes
- Fix `AWS::LanguageExtensions` regex for sub removal to handle pseudo parameters (pull #[2812](https://github.com/aws-cloudformation/cfn-lint/pull/2812))

### v0.79.1
###### Features
- Add support for `Fn::ForEach` when using `AWS::LanguageExtensions` (pull #[2801](https://github.com/aws-cloudformation/cfn-lint/pull/2801))

### v0.78.2
###### Features
- Add `test` function to test conditions given a scenario (pull #[2801](https://github.com/aws-cloudformation/cfn-lint/pull/2801))
###### CloudFormation Specifications
- Update CloudFormation specs to `131.0.0` (pull #[2795](https://github.com/aws-cloudformation/cfn-lint/pull/2795))
- Updated `DocumentDBEngineVersion` `AllowedValues` (pull #[2800](https://github.com/aws-cloudformation/cfn-lint/pull/2800))

### v0.78.1
###### Features
- Update rule [E1018](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1018) to flag splitting dynamic references (pull #[2786](https://github.com/aws-cloudformation/cfn-lint/pull/2786))
- New rule [W2533](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2533) to validate lambda zip deployment configuration (pull #[2682](https://github.com/aws-cloudformation/cfn-lint/pull/2682))
- Supporting intrinsic function in `DeletionPolicy` and `UpdateReplacePolicy` (pull #[2784](https://github.com/aws-cloudformation/cfn-lint/pull/2784))
###### CloudFormation Specifications
- Update CloudFormation specs to `130.0.0` (pull #[2783](https://github.com/aws-cloudformation/cfn-lint/pull/2783))
###### Fixes
- Pin `jsonschema` to be under `4.18` (pull #[2792](https://github.com/aws-cloudformation/cfn-lint/pull/2792))
- Fix using `include_experimental` in metadata (pull #[2785](https://github.com/aws-cloudformation/cfn-lint/pull/2785))
- Fix rule [E1024](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1024) to better handle conditions (pull #[2780](https://github.com/aws-cloudformation/cfn-lint/pull/2780))

### v0.77.10
###### CloudFormation Specifications
- Update CloudFormation specs to `127.0.0` (pull #[2763](https://github.com/aws-cloudformation/cfn-lint/pull/2763))

### v0.77.9
###### CloudFormation Specifications
- Fix an issue with SSM patching (pull #[2765](https://github.com/aws-cloudformation/cfn-lint/pull/2765))

### v0.77.8
###### CloudFormation Specifications
- Update CloudFormation specs to `126.0.0` (pull #[2753](https://github.com/aws-cloudformation/cfn-lint/pull/2753))

### v0.77.7
###### Fixes
- Fix usage of comments and new lines in custom rules(pull #[2757](https://github.com/aws-cloudformation/cfn-lint/pull/2757))

### v0.77.6
###### CloudFormation Specifications
- Update CloudFormation specs to `124.0.0` (pull #[2736](https://github.com/aws-cloudformation/cfn-lint/pull/2736))
- Add `AWS::KMS::Key` to stateful resource list (pull #[2751](https://github.com/aws-cloudformation/cfn-lint/pull/2751))
###### Fixes
- Update [E3012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3012) documentation changes for more clarity (pull #[2747](https://github.com/aws-cloudformation/cfn-lint/pull/2747))

### v0.77.5
###### CloudFormation Specifications
- Update CloudFormation specs to `121.0.0` (pull #[2723](https://github.com/aws-cloudformation/cfn-lint/pull/2723))

### v0.77.4
###### CloudFormation Specifications
- Update CloudFormation specs to `120.0.0` (pull #[2714](https://github.com/aws-cloudformation/cfn-lint/pull/2714))
###### Fixes
- Fix Conditions logic when checking a condition against a region. Now return True and False when the condition has no basis on region (pull #[2721](https://github.com/aws-cloudformation/cfn-lint/pull/2721))
- Rebuild conditions inside the Template class when doing a Transform (pull #[2721](https://github.com/aws-cloudformation/cfn-lint/pull/2721))

### v0.77.3
###### CloudFormation Specifications
- Update CloudFormation specs to `119.2.0` (pull #[2703](https://github.com/aws-cloudformation/cfn-lint/pull/2703))
###### Fixes
- GetAtt can return objects along with FindInMap (pull #[2709](https://github.com/aws-cloudformation/cfn-lint/pull/2709))

### v0.77.2
###### Features
- Add custom operators for regex, gt, lt (pull #[2694](https://github.com/aws-cloudformation/cfn-lint/pull/2694))
###### CloudFormation Specifications
- Update CloudFormation specs to `119.1.0` (pull #[2698](https://github.com/aws-cloudformation/cfn-lint/pull/2698))

### v0.77.1
###### CloudFormation Specifications
- Update CloudFormation specs to `119.1.0` (pull #[2678](https://github.com/aws-cloudformation/cfn-lint/pull/2678))
- Update allowed values for `AWS::RDS::DBInstance.PerformanceInsightsRetentionPeriod` (pull #[2696](https://github.com/aws-cloudformation/cfn-lint/pull/2696))
###### Fixes
- Update rule [E3001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3001) to evaluate if a resource with a condition is affected by the region (pull #[2691](https://github.com/aws-cloudformation/cfn-lint/pull/2691))

### v0.77.0
###### Features
- Convert from `re` to `regex` (pull #[2643](https://github.com/aws-cloudformation/cfn-lint/pull/2643))
- Implement `IS DEFINED` in custom rules (pull #[2656](https://github.com/aws-cloudformation/cfn-lint/pull/2656))
###### CloudFormation Specifications
- Update CloudFormation specs to `119.0.0` (pull #[2660](https://github.com/aws-cloudformation/cfn-lint/pull/2660))
- Patch `AWS::S3::Bucket.InventoryConfiguration.OptionalFields` to include `ChecksumAlgorithm` (pull #[2666](https://github.com/aws-cloudformation/cfn-lint/pull/2666))
- Patch `AWS::Cognito::UserPool.UserPollTags` to be a map of strings (pull #[2671](https://github.com/aws-cloudformation/cfn-lint/pull/2671))
###### Fixes
- Update SAM translation to substitute for a sub in `CodeUri` (pull #[2661](https://github.com/aws-cloudformation/cfn-lint/pull/2661))
- Update language extensions to validate if a ref is iterable before assuming it is (pull #[2665](https://github.com/aws-cloudformation/cfn-lint/pull/2665))
- Update rule [E3001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3001) to consider a resource level condition when evaluating if the resource type exists (pull #[2668](https://github.com/aws-cloudformation/cfn-lint/pull/2668))
- Update rule [E3012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3001) to validate if a map is actually a map (pull #[2669](https://github.com/aws-cloudformation/cfn-lint/pull/2669))

### v0.76.2
###### CloudFormation Specifications
- Update CloudFormation specs to `118.1.0` (pull #[2644](https://github.com/aws-cloudformation/cfn-lint/pull/2644))

### v0.76.1
###### Fixes
- Fix an issue with Conditions when a `Fn::Equals` has a string that isn't in a Parameters `AllowedValues` (pull #[2649](https://github.com/aws-cloudformation/cfn-lint/pull/2649))

### v0.76.0
###### Features
- Convert conditions to SymPy (pull #[2624](https://github.com/aws-cloudformation/cfn-lint/pull/2624))
- Include tests in sdist (pull #[2630](https://github.com/aws-cloudformation/cfn-lint/pull/2630))
###### CloudFormation Specifications
- Update CloudFormation specs to `117.0.0` (pull #[2642](https://github.com/aws-cloudformation/cfn-lint/pull/2642))
###### Fixes
- Fix SAM templates treated as normal by api (pull #[2646](https://github.com/aws-cloudformation/cfn-lint/pull/2646))

### v0.75.1
###### CloudFormation Specifications
- Update CloudFormation specs to `116.0.0` (pull #[2620](https://github.com/aws-cloudformation/cfn-lint/pull/2620))
- Add string length for `AWS::WAFRegional::RegexPatternSet.RegexPatternStrings` and `AWS::WAFv2::RegexPatternSet.RegularExpressionList` (pull #[2637](https://github.com/aws-cloudformation/cfn-lint/pull/2616), (pull #[2639](https://github.com/aws-cloudformation/cfn-lint/pull/2639))

### v0.75.0
###### Features
- Read the default region from Env Vars (pull #[2618](https://github.com/aws-cloudformation/cfn-lint/pull/2618))
###### Fixes
- Update rule [W2030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2030) and [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3008) to read `ValueTypes` from `us-east-1` when `CACHED` (pull #[2635](https://github.com/aws-cloudformation/cfn-lint/pull/2635))

### v0.74.3
###### Fixes
- Update rule [W2031](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2031), [E3031](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3031), [E3030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3030), [E3034](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3034), and [E3033](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3033) to read `ValueTypes` from `us-east-1` when `CACHED` (pull #[2628](https://github.com/aws-cloudformation/cfn-lint/pull/2628))

### v0.74.2
###### CloudFormation Specifications
- Update CloudFormation specs to `115.0.0` (pull #[2616](https://github.com/aws-cloudformation/cfn-lint/pull/2616))
###### Fixes
- Fix custom rule inequality comparison (pull #[2614](https://github.com/aws-cloudformation/cfn-lint/pull/2614))
- Restructure the decode module (pull #[2607](https://github.com/aws-cloudformation/cfn-lint/pull/2607))

### v0.74.1
###### CloudFormation Specifications
- Update CloudFormation specs to `114.0.0` (pull #[2601](https://github.com/aws-cloudformation/cfn-lint/pull/2601))
- Remove `AWS::Logs::LogGroup.RetentionInDays` `AllowedValues` (pull #[2604](https://github.com/aws-cloudformation/cfn-lint/pull/2604))

### v0.74.0
###### Features
- Add rule [E3044](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3044) to validate the scheduling strategy for Fargate services (pull #[2559](https://github.com/aws-cloudformation/cfn-lint/pull/2559))
###### CloudFormation Specifications
- Update CloudFormation specs to `113.0.0` (pull #[2591](https://github.com/aws-cloudformation/cfn-lint/pull/2591))
###### Fixes
- Updated condition logic to limit the number of conditions that are processed (pull #[2598](https://github.com/aws-cloudformation/cfn-lint/pull/2598))

### v0.73.2
###### CloudFormation Specifications
- Update CloudFormation specs to `112.0.0` (pull #[2580](https://github.com/aws-cloudformation/cfn-lint/pull/2580))
###### Fixes
- Updated rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2532) by adding `ItemProcessor` to `Map` (pull #[2577](https://github.com/aws-cloudformation/cfn-lint/pull/2577))
- Relax `networkx` dependency (pull #[2584](https://github.com/aws-cloudformation/cfn-lint/pull/2584))
- Validate sub string checks are strings before running regex in graph and template (pull #[2589](https://github.com/aws-cloudformation/cfn-lint/pull/2589))
- Update SAM transform pre-work to include `DefinitionBody` when `DisableExecuteApiEndpoint` is specified (pull #[2590](https://github.com/aws-cloudformation/cfn-lint/pull/2590))

### v0.73.1
###### CloudFormation Specifications
- Patch back in `TargetRole` for `AWS::RDS::DBProxyEndpoint` (pull #[2581](https://github.com/aws-cloudformation/cfn-lint/pull/2581))

### v0.73.0
###### CloudFormation Specifications
- Update CloudFormation specs to `111.0.0` (pull #[2572](https://github.com/aws-cloudformation/cfn-lint/pull/2572))
- Add region `ap-southeast-4` (pull #[2568](https://github.com/aws-cloudformation/cfn-lint/pull/2568))
- Remove `AWS::RDS::DBCluster` `MasterUsername` and `MasterUserPassword` from Inclusive (pull #[2571](https://github.com/aws-cloudformation/cfn-lint/pull/2571))
###### Fixes
- Update SAM Translator version based on the SAM CLI requirement (pull #[2570](https://github.com/aws-cloudformation/cfn-lint/pull/2570))

### v0.72.10
###### CloudFormation Specifications
- Update CloudFormation specs to `108.0.0` (pull #[2557](https://github.com/aws-cloudformation/cfn-lint/pull/2557))
- Add `AWS::Organizations::Account` to `StatefulResources` (pull #[2560](https://github.com/aws-cloudformation/cfn-lint/pull/2560))
###### Fixes
- Update rule [I3100](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3100) regex family string matching (pull #[2558](https://github.com/aws-cloudformation/cfn-lint/pull/2558))

### v0.72.9
###### CloudFormation Specifications
- Update CloudFormation specs to `107.0.0` (pull #[2546](https://github.com/aws-cloudformation/cfn-lint/pull/2550))

### v0.72.8
###### Features
- Support `Fn::FindInMap` [enhancements](https://github.com/aws-cloudformation/cfn-language-discussion/commit/42cec9ce0d980a0832dc0fd1aed5750980280892?short_path=be2a597#diff-be2a59710611cc501f7361fcff1c335613d5dabb8326ce3ea746f4474f954bc5) when template is declared with `AWS::LanguageExtensions` (pull #[2512](https://github.com/aws-cloudformation/cfn-lint/pull/2512))

### v0.72.7
###### CloudFormation Specifications
- Update CloudFormation specs to `106.0.0` (pull #[2546](https://github.com/aws-cloudformation/cfn-lint/pull/2546))
###### Fixes
- Update rule [E1030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1030) to include `Fn::FindInMap` when using `Fn::Length` (pull #[2547](https://github.com/aws-cloudformation/cfn-lint/pull/2547))
- Update rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) to allow a `Fn::GetAtt` for an object (pull #[2548](https://github.com/aws-cloudformation/cfn-lint/pull/2548))
- Update rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2532) to include current task properties (pull #[2549](https://github.com/aws-cloudformation/cfn-lint/pull/2549))

### v0.72.6
###### CloudFormation Specifications
- Update CloudFormation specs to `105.0.0` (pull #[2530](https://github.com/aws-cloudformation/cfn-lint/pull/2530))
###### Fixes
- Use a clean copy of the `cli_value` each time when merging config to avoid leaking config from one template to another (pull #[2536](https://github.com/aws-cloudformation/cfn-lint/pull/2536))

### v0.72.5
###### Features
- Update rule [W1001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W1001) to support `Fn::Sub` (pull #[2525](https://github.com/aws-cloudformation/cfn-lint/pull/2525))
###### CloudFormation Specifications
- Update CloudFormation specs to `102.0.0` (pull #[2523](https://github.com/aws-cloudformation/cfn-lint/pull/2523))

### v0.72.4
###### Fixes
- Update `Template` function `get_valid_getatts` to better return None when a property type doesn't exist (pull #[2527](https://github.com/aws-cloudformation/cfn-lint/pull/2527))

### v0.72.3
###### Features
- Update rule [E2015](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2015) to support the `AllowedValues` and `AllowedPattern` attributes for `CommaDelimitedList` parameters (pull #[2521](https://github.com/aws-cloudformation/cfn-lint/pull/2521))
###### CloudFormation Specifications
- Update CloudFormation specs to `101.0.0` (pull #[2517](https://github.com/aws-cloudformation/cfn-lint/pull/2517))
- Update `get_valid_getatts` to account for changes in the CloudFormation spec (pull #[2520](https://github.com/aws-cloudformation/cfn-lint/pull/2520))
###### Fixes
- Don't validate rule [I3042](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3042) when using SAM (pull #[2513](https://github.com/aws-cloudformation/cfn-lint/pull/2513))

### v0.72.2
###### CloudFormation Specifications
- Update CloudFormation specs to `100.0.0` (pull #[2493](https://github.com/aws-cloudformation/cfn-lint/pull/2493))
###### Fixes
- Update rule [E1011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1011) to merge key validation into one method (pull #[2502](https://github.com/aws-cloudformation/cfn-lint/pull/2502))

### v0.72.1
###### CloudFormation Specifications
- Add `ap-south-2` region (pull #[2503](https://github.com/aws-cloudformation/cfn-lint/pull/2503))
###### Fixes
- Rebuild the graph after doing the transform (pull #[2502](https://github.com/aws-cloudformation/cfn-lint/pull/2502))

### v0.72.0
###### Features
- Add more info into the graph including outputs and parameters(pull #[2452](https://github.com/aws-cloudformation/cfn-lint/pull/2452))
###### CloudFormation Specifications
- Update CloudFormation specs to `99.0.0` (pull #[2486](https://github.com/aws-cloudformation/cfn-lint/pull/2486))
- Add `eu-south-2` region (pull #[2490](https://github.com/aws-cloudformation/cfn-lint/pull/2490))
###### Fixes
- Make sure regex patterns with `\w` are validating against ASCII (pull #[2487](https://github.com/aws-cloudformation/cfn-lint/pull/2487))

### v0.71.1
###### Features
###### CloudFormation Specifications
- Add support for region `eu-central-2` (pull #[2478](https://github.com/aws-cloudformation/cfn-lint/pull/2478))
- Update CloudFormation specs to `97.0.0` (pull #[2475](https://github.com/aws-cloudformation/cfn-lint/pull/2475))

### v0.71.0
###### Features
- Reduce storage on disk by reducing regional specs to only have differences from `us-east-1` spec (pull #[2457](https://github.com/aws-cloudformation/cfn-lint/pull/2457))
###### CloudFormation Specifications
- Update CloudFormation specs to `96.0.0` (pull #[2461](https://github.com/aws-cloudformation/cfn-lint/pull/2461))
###### Fixes
- Fix an issue with junit/pretty formatter/core process to get all rules even on parse failure (pull #[2462](https://github.com/aws-cloudformation/cfn-lint/pull/2462))
- Fix an issue when use stdin to pass a template and cfn-lint with parameters giving `E0000` (pull #[2470](https://github.com/aws-cloudformation/cfn-lint/pull/2470))

### v0.70.1
###### Features
- Add support for Python 3.11 (pull #[2463](https://github.com/aws-cloudformation/cfn-lint/pull/2463))
###### Fixes
- Fix an issue with `--list-rules` failing (pull #[2466](https://github.com/aws-cloudformation/cfn-lint/pull/2466))

### v0.70.0
###### Features
- Add rule [W8003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W8003) to check if `Fn::Equals` will always be true or false (pull #[2426](https://github.com/aws-cloudformation/cfn-lint/pull/2426))
- Allow you to configure how exit codes work (pull #[2436](https://github.com/aws-cloudformation/cfn-lint/pull/2436))
###### CloudFormation Specifications
- Update CloudFormation specs to `95.0.0` (pull #[2440](https://github.com/aws-cloudformation/cfn-lint/pull/2440))
- Remove check for string size of `Lambda::Function.Code.Zipfile` (pull #[2447](https://github.com/aws-cloudformation/cfn-lint/pull/2447))
###### Fixes
- Update rule [E3012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3012) to validate bad functions (pull #[2441](https://github.com/aws-cloudformation/cfn-lint/pull/2441))
- Update rule [E3016](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3016) to make checks less restrictive (pull #[2453](https://github.com/aws-cloudformation/cfn-lint/pull/2453))

### v0.69.1
###### CloudFormation Specifications
- Updated string max value to `Lambda::Function.Code.Zipfile` to 4MB (pull #[2444](https://github.com/aws-cloudformation/cfn-lint/pull/2444))

### v0.69.0
###### Features
- Update decode of yaml/json to report on all duplicates (pull #[2428](https://github.com/aws-cloudformation/cfn-lint/pull/2428))
###### CloudFormation Specifications
- Patch in `db.serverless` into `AWS::RDS::DBInstance.DBInstanceClass` (pull #[2430](https://github.com/aws-cloudformation/cfn-lint/pull/2430))
- Added string max value to `Lambda::Function.Code.Zipfile` (pull #[2431](https://github.com/aws-cloudformation/cfn-lint/pull/2431))
###### Fixes
- Don't replace location for resource `AWS::Serverless::Application` in SAM transform when its a string (pull #[2425](https://github.com/aws-cloudformation/cfn-lint/pull/2425))

### v0.68.1
###### CloudFormation Specifications
- Patch in `db.serverless` into `AWS::RDS::DBInstance.DBInstanceClass` (pull #[2424](https://github.com/aws-cloudformation/cfn-lint/pull/2424))
- Update CloudFormation specs to `94.0.0` (pull #[2420](https://github.com/aws-cloudformation/cfn-lint/pull/2420))

### v0.68.0
###### Features
- Ability to override location of the finding (pull #[2410](https://github.com/aws-cloudformation/cfn-lint/pull/2410))
###### CloudFormation Specifications
- Patch in `DBClusterResourceId` for as an Attribute of `AWS::RDS::DBCluster` (pull #[2407](https://github.com/aws-cloudformation/cfn-lint/pull/2407))
- Update CloudFormation specs to `93.0.0` (pull #[2409](https://github.com/aws-cloudformation/cfn-lint/pull/2409))
- Update `AllowedPatternRegex` for `AWS::CloudWatch::Alarm.MetricDataQuery.Id`  (pull #[2414](https://github.com/aws-cloudformation/cfn-lint/pull/2414)
- Add GetAtt to AWS::KMS::ReplicaKey.Arn for KmsKey.Arn (pull #[2417](https://github.com/aws-cloudformation/cfn-lint/pull/2417))

### v0.67.0
###### Features
- Support child rules allowing rules to add another rule in their match responses (pull #[2393](https://github.com/aws-cloudformation/cfn-lint/pull/2393))
###### CloudFormation Specifications
- Update CloudFormation specs to `92.0.0` (pull #[2399](https://github.com/aws-cloudformation/cfn-lint/pull/2399))

### v0.66.1
###### CloudFormation Specifications
- Update CloudFormation specs to `91.0.0` (pull #[2392](https://github.com/aws-cloudformation/cfn-lint/pull/2392))
###### Fixes
- Update [E8003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E8003), [E1018](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1018), [E1019](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1019) to allow `Fn::ToJsonString` inside `Equals`, `Split`, and `Sub` (pull #[2397](https://github.com/aws-cloudformation/cfn-lint/pull/2397))
- Update [I3013](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3013) to allow https and s3 (pull #[2394](https://github.com/aws-cloudformation/cfn-lint/pull/2394))

### v0.66.0
###### Features
- Update [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) to provide a suggestion if the wrong value is close to a correct value (pull #[2387](https://github.com/aws-cloudformation/cfn-lint/pull/2387))
###### CloudFormation Specifications
- Update CloudFormation specs to `90.0.0` (pull #[2376](https://github.com/aws-cloudformation/cfn-lint/pull/2376))
- Add in allowed values for oracle cdb engine types to `AWS::RDS::DBInstance.Engine` (pull #[2381](https://github.com/aws-cloudformation/cfn-lint/pull/2381))
- Add in allowd value `PredictiveScaling` to `AWS::AutoScaling::ScalingPolicy.PolicyType` (pull #[2378](https://github.com/aws-cloudformation/cfn-lint/pull/2378))
###### Fixes
- Update [W3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W3002) to validate values aren't already S3 paths (pull #[2382](https://github.com/aws-cloudformation/cfn-lint/pull/2382))
- Update [I3013](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3013) to not regex check if a function (pull #[2386](https://github.com/aws-cloudformation/cfn-lint/pull/2386))

### v0.65.1
###### CloudFormation Specifications
- Update CloudFormation specs to `89.0.0` (pull #[2366](https://github.com/aws-cloudformation/cfn-lint/pull/2366))
- Add support for `custom` RDS `Engine` types on resource type `AWS::RDS::DBInstance` (pull #[2370](https://github.com/aws-cloudformation/cfn-lint/pull/2370))
- Remove extra spacing in specs reducing overall size (pull #[2371](https://github.com/aws-cloudformation/cfn-lint/pull/2371))
- Update `AllowedValues` for `RetentionInDays` on resource type `AWS::Logs::LogGroup` (pull #[2372](https://github.com/aws-cloudformation/cfn-lint/pull/2372))

### v0.65.0
###### Features
- Add `--force` option on `--update-specs` so cache isn't used (pull #[2334](https://github.com/aws-cloudformation/cfn-lint/pull/2334))
- Add support for Python 3.10 (pull #[2365](https://github.com/aws-cloudformation/cfn-lint/pull/2365))
###### CloudFormation Specifications
- Update CloudFormation specs to `88.0.0` (pull #[2361](https://github.com/aws-cloudformation/cfn-lint/pull/2361))
###### Fixes
- Add in `mypy` testing and do a bunch of cleanup based on the results (pull #[2328](https://github.com/aws-cloudformation/cfn-lint/pull/2328))
- Update rule [I1022](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I1022) to not suggest `Fn::Sub` on complext `Fn::Join`s (pull #[2364](https://github.com/aws-cloudformation/cfn-lint/pull/2364))


### v0.64.1
###### Fixes
- Make `me-central-1` `ExtendedSpecs` a module (pull #[2359](https://github.com/aws-cloudformation/cfn-lint/pull/2359))

### v0.64.0
###### Features
- Update `jsonschema` to be able to use version 3.0 and 4.0 (pull #[2336](https://github.com/aws-cloudformation/cfn-lint/pull/2336))
- Remove support for python 3.6 and add python 3.9 (pull #[2347](https://github.com/aws-cloudformation/cfn-lint/pull/2347))
###### CloudFormation Specifications
- Update CloudFormation specs to `87.0.0` (pull #[2353](https://github.com/aws-cloudformation/cfn-lint/pull/2353))
- Add support for region `me-central-1` (pull #[2351](https://github.com/aws-cloudformation/cfn-lint/pull/2351))
###### Fixes
- Disable the SAM validation checks when transforming a template (pull #[2350](https://github.com/aws-cloudformation/cfn-lint/pull/2350))

### v0.63.2
###### CloudFormation Specifications
- Patch in attributes for `AWS::RDS::DBCluster` (pull #[2344](https://github.com/aws-cloudformation/cfn-lint/pull/2344))

### v0.63.1
###### CloudFormation Specifications
- Update CloudFormation specs to `86.0.0` (pull #[2335](https://github.com/aws-cloudformation/cfn-lint/pull/2335))

### v0.63.0
###### Features
- support for AWS::LanguageExtensions transform features including DeletionPolicy,  UpdateReplacePolicy, Fn::Length and Fn::ToJsonString [docs](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference.html) (pull #[2339](https://github.com/aws-cloudformation/cfn-lint/pull/2339))
- Add rule [E1030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1030) to validate Fn::Length is configured correctly (pull #[2339](https://github.com/aws-cloudformation/cfn-lint/pull/2339))
- Add rule [E1031](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1030) to validate Fn::Length is configured correctly (pull #[2339](https://github.com/aws-cloudformation/cfn-lint/pull/2339))

### v0.62.0
###### Features
- Create new API to allow for easier integration of using cfn-lint as a library [docs](https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/getting_started/integration.md) (pull #[2285](https://github.com/aws-cloudformation/cfn-lint/pull/2285))
###### CloudFormation Specifications
- Update CloudFormation specs to `85.0.0` (pull #[2324](https://github.com/aws-cloudformation/cfn-lint/pull/2324))
- Update Lambda deprecation dates (pull #[2327](https://github.com/aws-cloudformation/cfn-lint/pull/2327))
###### Fixes
- Fix an issue with `RulesCollection` in which configurations would carry over between templates (pull #[2331](https://github.com/aws-cloudformation/cfn-lint/pull/2331))
- Add used rules into `RulesCollection` so we can print all the used rules in JUnit and Pretty formatting (pull #[2330](https://github.com/aws-cloudformation/cfn-lint/pull/2330))
- Update error message on [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) (pull #[2059](https://github.com/aws-cloudformation/cfn-lint/pull/2059))
- Update error description on [E1020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1020) (pull #[2329](https://github.com/aws-cloudformation/cfn-lint/pull/2329))

### v0.61.5
###### CloudFormation Specifications
- Update CloudFormation specs to `83.0.0` (pull #[2316](https://github.com/aws-cloudformation/cfn-lint/pull/2316))
###### Fixes
- Update rule [I3100](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3100) have proper path to resource (pull #[2309](https://github.com/aws-cloudformation/cfn-lint/pull/2309))
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2503) by removing `AllowedValues` for `AWS::ElasticLoadBalancingV2::LoadBalancer.LoadBalancerAttribute` (pull #[2184](https://github.com/aws-cloudformation/cfn-lint/pull/2184))
- Update rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) to include `<CommaDelimitedList` in SSM parameters (pull #[2320](https://github.com/aws-cloudformation/cfn-lint/pull/2320))
- Update rule [I3013](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3013) to not flag on Aurora instances (pull #[2317](https://github.com/aws-cloudformation/cfn-lint/pull/2317))

### v0.61.4
###### CloudFormation Specifications
- Update CloudFormation specs to `81.1.0` (pull #[2308](https://github.com/aws-cloudformation/cfn-lint/pull/2308))

### v0.61.3
###### CloudFormation Specifications
- Update CloudFormation specs to `81.0.0` (pull #[2306](https://github.com/aws-cloudformation/cfn-lint/pull/2306))
- Add `AWS::EC2::KeyPair` as a `Ref` for the value type `KeyPair` (pull #[2305](https://github.com/aws-cloudformation/cfn-lint/pull/2305))

### v0.61.2
###### CloudFormation Specifications
- Update CloudFormation specs to `78.1.0` (pull #[2292](https://github.com/aws-cloudformation/cfn-lint/pull/2292))
###### Fixes
- Add `utf-8` encoding to all `open` calls (pull #[2298](https://github.com/aws-cloudformation/cfn-lint/pull/2298))

### v0.61.1
###### CloudFormation Specifications
- Update CloudFormation specs to `76.0.0` (pull #[2282](https://github.com/aws-cloudformation/cfn-lint/pull/2282))
###### Fixes
- Suppress `PendingDeprecationWarning` for `pydot` in the `pygraphviz` package (pull #[2289](https://github.com/aws-cloudformation/cfn-lint/pull/2289))
- Update descriptiosn on rule [E1021](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1021), [E1015](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1015), [E1016](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1016), [E1020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1020), and [E1017](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1017) (pull #[2284](https://github.com/aws-cloudformation/cfn-lint/pull/2284))
- Update rule [E3033](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3033) to ignore dynamic references for string length (pull #[2281](https://github.com/aws-cloudformation/cfn-lint/pull/2281)) 

### v0.61.0
###### Features
- New rule [I3100](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3100) to validate new generation instance types are used (pull #[2267](https://github.com/aws-cloudformation/cfn-lint/pull/2267))
###### CloudFormation Specifications
- Update CloudFormation specs to `73.1.0` (pull #[2275](https://github.com/aws-cloudformation/cfn-lint/pull/2275))
- Add `AWS::OpenSearchService::Domain.AccessPolicies` to IAM rules (pull #[2269](https://github.com/aws-cloudformation/cfn-lint/pull/2269))
###### Fixes
- Reduce the calculated scenarios used when conditions match and one condition has many variants (pull #[2277](https://github.com/aws-cloudformation/cfn-lint/pull/2277))
- Update SARIF output to point to the general "Rules" documentation when a rule doesn't specify a `source_url` (pull #[2276](https://github.com/aws-cloudformation/cfn-lint/pull/2276))

### v0.60.1
###### CloudFormation Specifications
- Update CloudFormation specs to `72.0.0` (pull #[2272](https://github.com/aws-cloudformation/cfn-lint/pull/2272))
###### Fixes
- Don't allow regex expressions that result in a warning (pull #[2272](https://github.com/aws-cloudformation/cfn-lint/pull/2272))

### v0.60.0
###### Features
- Move null checks from the parsing engine into rules (pull #[2242](https://github.com/aws-cloudformation/cfn-lint/pull/2242))
- Add rule [E4002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E4002) to validate metadata config (pull #[2242](https://github.com/aws-cloudformation/cfn-lint/pull/2242))
- Update rule [E2001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2001) to error on null values (pull #[2242](https://github.com/aws-cloudformation/cfn-lint/pull/2242))
- Update rule [E3012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3012) to validate for null values in properties (pull #[2242](https://github.com/aws-cloudformation/cfn-lint/pull/2242))
###### CloudFormation Specifications
- Update CloudFormation specs to `69.0.0` (pull #[2261](https://github.com/aws-cloudformation/cfn-lint/pull/2261))

### v0.59.1
###### CloudFormation Specifications
- Update CloudFormation specs to `66.1.0` (pull #[2255](https://github.com/aws-cloudformation/cfn-lint/pull/2255))
###### Fixes
- Lambda runtime deprecation updates (python3.6) (pull #[2252](https://github.com/aws-cloudformation/cfn-lint/pull/2252))
- Update rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) to consider a list as valid JSON (pull #[2253](https://github.com/aws-cloudformation/cfn-lint/pull/2253))

### v0.59.0
###### Features
- Update `aws-sam-translator` to `1.45.0` (pull #[2245](https://github.com/aws-cloudformation/cfn-lint/pull/2245))
- Remove dependency on `six` (pull #[2204](https://github.com/aws-cloudformation/cfn-lint/pull/2204))
- New rule [E3504](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3504) to validate resources with `AWS::Backup::BackupPlan`. The property `DeleteAfterDays` cannot be less than 90 days from `MoveToColdStorageAfterDays` (pull #[2230](https://github.com/aws-cloudformation/cfn-lint/pull/2230))
###### CloudFormation Specifications
- Update CloudFormation specs to `66.0.0` (pull #[2245](https://github.com/aws-cloudformation/cfn-lint/pull/2245))

### v0.58.4
###### CloudFormation Specifications
- Update CloudFormation specs to `61.0.0` (pull #[2232](https://github.com/aws-cloudformation/cfn-lint/pull/2232))
###### Fixes
- Update SAM Transform pre work to add `ImageUri` when using `Image` as `PackageType` in `AWS::Serverless::Function` (pull #[2236](https://github.com/aws-cloudformation/cfn-lint/pull/2236))

### v0.58.3
###### CloudFormation Specifications
- Update CloudFormation specs to `59.0.0` (pull #[2225](https://github.com/aws-cloudformation/cfn-lint/pull/2225))
- Remove allowed values for `AWS::Config::ConfigurationRecorder.ResourceTypes` (pull #[2231](https://github.com/aws-cloudformation/cfn-lint/pull/2231))
###### Fixes
- Wrap creating a YAML map with try/except and create lint error on failure (pull #[2226](https://github.com/aws-cloudformation/cfn-lint/pull/2226))

### v0.58.2
###### CloudFormation Specifications
- Update CloudFormation specs to `58.0.0` (pull #[2217](https://github.com/aws-cloudformation/cfn-lint/pull/2217))
###### Fixes
- [W2506](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2506): Avoid false positives when using a `Ref` against a resource (pull #[2210](https://github.com/aws-cloudformation/cfn-lint/pull/2210))
- [E3502](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3502): Blank out functions in JSON size check to prevent false positives (pull #[2222](https://github.com/aws-cloudformation/cfn-lint/pull/2222))

### v0.58.1
###### CloudFormation Specifications
- Update CloudFormation specs to `56.0.0` (pull #[2207](https://github.com/aws-cloudformation/cfn-lint/pull/2207))

### v0.58.0
###### Features
- Update rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020) to validate that TTL isn't added for Alias records (pull #[2195](https://github.com/aws-cloudformation/cfn-lint/pull/2195))
- Remove imports to `pathlib2` with deprecation of Python 2.7, 3.4, and 3.5 (pull #[2205](https://github.com/aws-cloudformation/cfn-lint/pull/2205))
- Improvements to json parsing code (pull #[2199](https://github.com/aws-cloudformation/cfn-lint/pull/2199))
###### CloudFormation Specifications
- Update CloudFormation specs to `54.0.0` (pull #[2202](https://github.com/aws-cloudformation/cfn-lint/pull/2202))
###### Fixes
- Fix an issue checking values of `false` in custom rules (pull #[2208](https://github.com/aws-cloudformation/cfn-lint/pull/2208))

### v0.57.0
###### Features
- EOL of Python 2.7, 3.4, and 3.5 support (pull #[2195](https://github.com/aws-cloudformation/cfn-lint/pull/2195))
###### CloudFormation Specifications
- Update CloudFormation specs to `53.0.0` (pull #[2196](https://github.com/aws-cloudformation/cfn-lint/pull/2196))
- Fix an issue with rule [E2001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2001) to allow string parameter constraints for all AWS specific types (pull #[2193](https://github.com/aws-cloudformation/cfn-lint/pull/2193))

### v0.56.4
###### CloudFormation Specifications
- Update CloudFormation specs to `52.0.0` (pull #[2188](https://github.com/aws-cloudformation/cfn-lint/pull/2188))
- Add region `ap-southeast-3` (pull #[2192](https://github.com/aws-cloudformation/cfn-lint/pull/2192))

### v0.56.3
###### Features
- Update `aws-sam-translator` to `1.42.0` (pull #[2183](https://github.com/aws-cloudformation/cfn-lint/pull/2183))
###### CloudFormation Specifications
- Update CloudFormation specs to `50.0.0` (pull #[2180](https://github.com/aws-cloudformation/cfn-lint/pull/2180))

### v0.56.2
###### CloudFormation Specifications
- Update CloudFormation specs to `49.0.0` (pull #[2178](https://github.com/aws-cloudformation/cfn-lint/pull/2178))
- Expand `StatefulResources` to include `AWS::OpenSearchService::Domain` (pull #[2179](https://github.com/aws-cloudformation/cfn-lint/pull/2179))
- Add `AWS::EKS::Cluster.ClusterSecurityGroupId` to `GetAtt` list of `AWS::EC2::SecurityGroup.NameOrGroupId` (pull #[2177](https://github.com/aws-cloudformation/cfn-lint/pull/2177))

### v0.56.1
###### CloudFormation Specifications
- Update CloudFormation specs to `48.0.0` (pull #[2170](https://github.com/aws-cloudformation/cfn-lint/pull/2170))
- Add `AWS::OpenSearchService::Domain` to be in the list for `EnableVersionUpgrade` (pull #[2174](https://github.com/aws-cloudformation/cfn-lint/pull/2174))

### v0.56.0
###### Features
- Update `aws-sam-translator` to `1.40.0` (pull #[2165](https://github.com/aws-cloudformation/cfn-lint/pull/2165))
###### CloudFormation Specifications
- Update CloudFormation specs to `47.0.0` (pull #[2164](https://github.com/aws-cloudformation/cfn-lint/pull/2164))
###### Fixes
- Switching logging level for `samtranslator` to `CRITICAL` (pull #[2168](https://github.com/aws-cloudformation/cfn-lint/pull/2168))

### v0.55.0
###### Features
- Adds support for outputting results in SARIF (pull #[2126](https://github.com/aws-cloudformation/cfn-lint/pull/2126))
###### CloudFormation Specifications
- Update CloudFormation specs to `46.0.0` (pull #[2158](https://github.com/aws-cloudformation/cfn-lint/pull/2158))

### v0.54.4
###### CloudFormation Specifications
- Update CloudFormation specs to `45.0.0` (pull #[2153](https://github.com/aws-cloudformation/cfn-lint/pull/2153))
- Add `AWS::DynamoDB::GlobalTable` to `AWS::Lambda::EventSourceMapping.EventSourceArn` (pull #[2151](https://github.com/aws-cloudformation/cfn-lint/pull/2151))
- Expand stateful resource types to include `AWS::SecretsManager::Secret` (pull #[2154](https://github.com/aws-cloudformation/cfn-lint/pull/2154))
###### Fixes
- Add `InstanceRefresh` to allowed values for `SuspendProcesses` in rule [E3016](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3016) (pull #[2160](https://github.com/aws-cloudformation/cfn-lint/pull/2160))
- Strip conditions completely from `CodePipeline` definitions in rule [E2541](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2541) (pull #[2152](https://github.com/aws-cloudformation/cfn-lint/pull/2152))

### v0.54.3
###### Features
- Add exceptions to rule [E3031](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3031) (pull #[2143](https://github.com/aws-cloudformation/cfn-lint/pull/2143))
###### CloudFormation Specifications
- Update CloudFormation specs to `44.0.0` (pull #[2124](https://github.com/aws-cloudformation/cfn-lint/pull/2124))
- Update `AllowedValues` for `AWS::CloudTrail::Trail.DataResourceType` (pull #[2134](https://github.com/aws-cloudformation/cfn-lint/pull/2134))
###### Fixes
- Add support for `Fn::If` inside rule [E1024](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1024) (pull #[2140](https://github.com/aws-cloudformation/cfn-lint/pull/2140))
- Update `aws-sam-translator` to `1.39.0` (pull #[2129](https://github.com/aws-cloudformation/cfn-lint/pull/2129))


### v0.54.2
###### CloudFormation Specifications
- Update CloudFormation specs to `41.2.0` (pull #[2119](https://github.com/aws-cloudformation/cfn-python-lint/pull/2119))

### v0.54.1
###### Fixes
- Update `Serverless/ManagedPolicies.json` and create automation to keep it up to date going forward (pull #[2116](https://github.com/aws-cloudformation/cfn-lint/pull/2116))

### v0.54.0
###### Features
- Update default configuration on rule [E3012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3012) to no be strict (pull #[2103](https://github.com/aws-cloudformation/cfn-lint/pull/2103))
- Add rule [E3043](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3043) to validate nested stack parameters (pull #[2074](https://github.com/aws-cloudformation/cfn-lint/pull/2074))
###### CloudFormation Specifications
- Update CloudFormation specs to `41.0.0` (pull #[2111](https://github.com/aws-cloudformation/cfn-python-lint/pull/2111))
- Add `AWS::KMS::ReplicaKey` as a `Ref`/`GetAtt` for `AWS::KMS::Alias.TargetKeyId` (pull #[2110](https://github.com/aws-cloudformation/cfn-lint/pull/2110))

### v0.53.1
###### CloudFormation Specifications
- Update resource specs to `40.1.0` (pull #[2105](https://github.com/aws-cloudformation/cfn-python-lint/pull/2105))
- `AWS::ElasticLoadBalancingV2::LoadBalancer.LoadBalancerAttribute` `AllowedValues` expansion (pull #[2101](https://github.com/aws-cloudformation/cfn-lint/pull/2101))
###### Fixes
- Fix rule message string formatting for [E3013](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3013) (pull #[2099](https://github.com/aws-cloudformation/cfn-lint/pull/2099))

### v0.53.0
###### Features
- Update `aws-sam-translator` to `1.38.0` (pull #[2082](https://github.com/aws-cloudformation/cfn-lint/pull/2082))
- Signal the end of life for Python 3.5 (pull #[2052](https://github.com/aws-cloudformation/cfn-lint/pull/2052))
- Allow configuration of top level sections in rule [E1001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1001) (pull #[2090](https://github.com/aws-cloudformation/cfn-lint/pull/2090))
###### CloudFormation Specifications
- Update resource specs to `39.8.0` (pull #[2087](https://github.com/aws-cloudformation/cfn-python-lint/pull/2087))
- Add `StringMax` to `AWS::SNS::Topic.TopicName`, `AWS::IAM::Role.Name`, `AWS::SNS::Topic.TopicName`, `AWS::Lambda::Function` properties `Handler`, `Description`, `FunctionName`, and `AWS::Lambda::LayerVersion` properties `LayerName` (pull #[2089](https://github.com/aws-cloudformation/cfn-lint/pull/2089))
###### Fixes
- Update `RetentionPeriodHours` for `AWS::Kinesis::Stream` to `8760` (pull #[2071](https://github.com/aws-cloudformation/cfn-lint/pull/2071))
- Expand `expanding likely_stateful_resource_types` to include `AWS::DynamoDB::GlobalTable` (pull #[2079](https://github.com/aws-cloudformation/cfn-lint/pull/2079))

### v0.52.0
###### Features
- End support for Python 3.4 (pull #[2048](https://github.com/aws-cloudformation/cfn-lint/pull/2048))
- New rule [I3013](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3013) to validate retention period settings on applicable resources (pull #[2054](https://github.com/aws-cloudformation/cfn-lint/pull/2054))
###### CloudFormation Specifications
- Update resource specs to `39.3.0` (pull #[2047](https://github.com/aws-cloudformation/cfn-python-lint/pull/2047))
###### Fixes
- Update `ManagedPolicies.json` to include `AWSLambda_FullAccess` and `AWSLambda_ReadOnlyAccess` (pull #[2062](https://github.com/aws-cloudformation/cfn-lint/pull/2062))
- Fix a warning in setuptools with `description-file` needed to be `description_file` (pull #[2051](https://github.com/aws-cloudformation/cfn-lint/pull/2051))
- Update the `schema.json` for `.cfnlintrc` files to have the correct format for `custom_rules` (pull #[2055](https://github.com/aws-cloudformation/cfn-lint/pull/2055))
- Update rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to `not` look at `TemplatyBody` since it can be a nested template (pull #[2057](https://github.com/aws-cloudformation/cfn-lint/pull/2057))
- Update rule [E3012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3012) to think of a list as json (pull #[2067](https://github.com/aws-cloudformation/cfn-lint/pull/2067))

### v0.51.0
###### Features
- A new sub class to make working with `Fn::Sub` easier (pull #[2003](https://github.com/aws-cloudformation/cfn-lint/pull/2003))
###### CloudFormation Specifications
- Update resource specs to `39.1.0` (pull #[2044](https://github.com/aws-cloudformation/cfn-python-lint/pull/2044))
###### Fixes
- Fix an issue with `networkx` package nesting in the graph function (pull #[2035](https://github.com/aws-cloudformation/cfn-lint/pull/2033))
- Update rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to only alert when the value found is a parameter or a resource (pull #[2031](https://github.com/aws-cloudformation/cfn-lint/pull/2031))

### v0.50.0
###### Features
- Update rule [E2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2507) to validate resource configuration in an IAM policy (pull #[2023](https://github.com/aws-cloudformation/cfn-lint/pull/2023))
- Update `aws-sam-translator` to `1.36.0` (pull #[2027](https://github.com/aws-cloudformation/cfn-lint/pull/2027))
###### CloudFormation Specifications
- Update resource specs to `37.1.0` (pull #[2012](https://github.com/aws-cloudformation/cfn-python-lint/pull/2012))
- Update Lambda EOL for `dotnetcore2.1` (pull #[2015](https://github.com/aws-cloudformation/cfn-lint/pull/2015))
- UPdate Lambda EOL for `nodejs10.x` and `ruby2.5` (pull #[2033](https://github.com/aws-cloudformation/cfn-lint/pull/2033))
###### Fixes
- Fix an issue with rule [E7003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E7003) when a `Fn::Transform` was in a mapping (pull #[2017](https://github.com/aws-cloudformation/cfn-lint/pull/2017))
- Fix an issue when finding duplicate keys where the 2nd error wasn't to the key (pull #[2011](https://github.com/aws-cloudformation/cfn-lint/pull/2011))

### v0.49.2
###### CloudFormation Specifications
- Update resource specs to `36.0.0` (pull #[2001](https://github.com/aws-cloudformation/cfn-python-lint/pull/2001))
- Add Boston, Miami, Houston as local zones (pull #[2002](https://github.com/aws-cloudformation/cfn-python-lint/pull/2002))
###### Fixes
- Update the key regex for rule [E7003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E7003) (pull #[2006](https://github.com/aws-cloudformation/cfn-python-lint/pull/2006))

### v0.49.1
###### CloudFormation Specifications
- Update resource specs to `35.2.0` (pull #[1998](https://github.com/aws-cloudformation/cfn-python-lint/pull/1998))

### v0.49.0
###### CloudFormation Specifications
- Update resource specs to `35.0.0` (pull #[1986](https://github.com/aws-cloudformation/cfn-python-lint/pull/1986))
- Patch in Glue resources into `us-gov-west-1` (pull #[1993](https://github.com/aws-cloudformation/cfn-python-lint/pull/1993))
###### Fixes
- Require pyyaml to be at least `5.4` for versions of Python that support it (pull #[1992](https://github.com/aws-cloudformation/cfn-python-lint/pull/1992))
- Update `aws-sam-translator` dependency to be at least `1.35.0` (pull #[1991](https://github.com/aws-cloudformation/cfn-python-lint/pull/1991))
- Update rule [W1001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W1001) to not validate `Globals` when looking at Refs and GetAtts (pull #[1989](https://github.com/aws-cloudformation/cfn-python-lint/pull/1989))

### v0.48.3
###### CloudFormation Specifications
- Update resource specs to `33.0.0` (pull #[1981](https://github.com/aws-cloudformation/cfn-python-lint/pull/1981))
- Remove `AWS::AmazonMQ::Broker.EngineVersion AllowedValues` from manual upkeep based on amount of change (pull #[1975](https://github.com/aws-cloudformation/cfn-python-lint/pull/1975))
###### Fixes
- Update rule [E3502](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3502) to convert strings into json before checking the size of the json (pull #[1982](https://github.com/aws-cloudformation/cfn-python-lint/pull/1982))
- Update rule [E2504](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2504) to check for Iops when type is `io1` or `io2` (pull #[1978](https://github.com/aws-cloudformation/cfn-python-lint/pull/1978))

### v0.48.2
###### CloudFormation Specifications
- Update resource specs to `32.0.0` (pull #[1962](https://github.com/aws-cloudformation/cfn-python-lint/pull/1962))
- Add `AWS::Kinesis::StreamConsumer` as a REF for `AWS::Lambda::EventSourceMapping.EventSourceArn` (pull #[1961](https://github.com/aws-cloudformation/cfn-python-lint/pull/1961))
###### Fixes
- Update EOL dates for AWS::Lambda::Function.Runtime used by rule [E2531](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2531) (pull #[1965](https://github.com/aws-cloudformation/cfn-python-lint/pull/1965))

### v0.48.1
###### CloudFormation Specifications
- Add regex pattern for `AWS::CloudWatch::Alarm.MetricDataQuery` `Id` (pull #[1948](https://github.com/aws-cloudformation/cfn-python-lint/pull/1948))
###### Fixes
- Update update IAM policies to not fail on changing upstream IAM policies (pull #[1954](https://github.com/aws-cloudformation/cfn-python-lint/pull/1954))
- Switch RegexDict to only string match based on if the type is Module (pull #[1956](https://github.com/aws-cloudformation/cfn-python-lint/pull/1956))

### v0.48.0
###### Features
- Allow writing of custom rules in plain text (pull #[1702](https://github.com/aws-cloudformation/cfn-python-lint/pull/1702))
###### CloudFormation Specifications
- Update resource specs to `31.1.0` (pull #[1942](https://github.com/aws-cloudformation/cfn-python-lint/pull/1942))

### v0.47.2
###### CloudFormation Specifications
- Update resource specs to `31.0.0` (pull #[1939](https://github.com/aws-cloudformation/cfn-python-lint/pull/1939))
- Only flag rule [I3042](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3042) when the ARN is inside a `Fn::Sub` (pull #[1928](https://github.com/aws-cloudformation/cfn-python-lint/pull/1928))

### v0.47.1
###### CloudFormation Specifications
- Update resource specs to `30.1.0` (pull #[1936](https://github.com/aws-cloudformation/cfn-python-lint/pull/1936))
- Add `Analytics` to `AWS::CDK::Metadata` (pull #[1937](https://github.com/aws-cloudformation/cfn-python-lint/pull/1937))
- Patch in `Outputs` into `Attributes` for `AWS::ServiceCatalog::CloudFormationProvisionedProduct` (pull #[1934](https://github.com/aws-cloudformation/cfn-python-lint/pull/1934))

### v0.47.0
###### Features
- Add rule [I3042](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3042) to check for hardcoded partitions, account IDs, and regions in an ARN (pull #[1805](https://github.com/aws-cloudformation/cfn-python-lint/pull/1805))
- Allow for merging of list configurations using `--merge-configs` (pull #[1915](https://github.com/aws-cloudformation/cfn-python-lint/pull/1915))
###### CloudFormation Specifications
- Update resource specs to `30.0.0` (pull #[1911](https://github.com/aws-cloudformation/cfn-python-lint/pull/1911))
- Add Kinesis Data Firehose to permitted SNS subscription protocols (pull #[1924](https://github.com/aws-cloudformation/cfn-python-lint/pull/1924))
- Changed DMS endpoint engine name for `DocumentDB` to `docdb` (pull #[1920](https://github.com/aws-cloudformation/cfn-python-lint/pull/1920))
###### Fixes
- Update rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2532) to add `ResultSelector` field to Task, Parallel & Map in step functions (pull #[1912](https://github.com/aws-cloudformation/cfn-python-lint/pull/1912))
- Update rule [E1017](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1017) to add `Fn::Select` to allowed value in index field of `Fn::Select` (pull #[1922](https://github.com/aws-cloudformation/cfn-python-lint/pull/1922))

### v0.46.0
###### CloudFormation Specifications
- Update resource specs to `28.1.0` (pull #[1905](https://github.com/aws-cloudformation/cfn-python-lint/pull/1905))
###### Fixes
- Update `aws-sam-translator` to `1.34.0` (pull #[1910](https://github.com/aws-cloudformation/cfn-python-lint/pull/1910))
- Return two errors when finding duplicates in the decode phase (pull #[1900](https://github.com/aws-cloudformation/cfn-python-lint/pull/1900))

### v0.45.0
###### CloudFormation Specifications
- Get value constraints from AWS CloudFormation registry types (pull #[1867](https://github.com/aws-cloudformation/cfn-python-lint/pull/1867))
- Update resource specs to `28.0.0` (pull #[1899](https://github.com/aws-cloudformation/cfn-python-lint/pull/1899))

### v0.44.7
###### CloudFormation Specifications
- Update resource specs to `27.0.0` (pull #[1892](https://github.com/aws-cloudformation/cfn-python-lint/pull/1892))
###### Fixes
- Fix an issue with rule [E3037](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3037) when certain types aren't serializable and forcing them to strings (pull #[1887](https://github.com/aws-cloudformation/cfn-python-lint/pull/1887))

### v0.44.6
###### CloudFormation Specifications
- Update resource specs to `26.0.0` (pull #[1884](https://github.com/aws-cloudformation/cfn-python-lint/pull/1884))
###### Fixes
- Fix an issue when directives are checked and resources aren't a dict (pull #[1877](https://github.com/aws-cloudformation/cfn-python-lint/pull/1877))

### v0.44.5
###### CloudFormation Specifications
- Update resource specs to `25.0.0` (pull #[1873](https://github.com/aws-cloudformation/cfn-python-lint/pull/1873))

### v0.44.4
###### Features
- Add support for `AWS::SSO::PermissionSet` `InlinePolicy` to [E2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2507) (pull #[1864](https://github.com/aws-cloudformation/cfn-python-lint/pull/1864))
###### CloudFormation Specifications
- Update resource specs to `24.0.0` (pull #[1863](https://github.com/aws-cloudformation/cfn-python-lint/pull/1863))
- Update `AWS::DataBrew::Recipe.Action` `Parameters` `Type` to `Map` (pull #[1871](https://github.com/aws-cloudformation/cfn-python-lint/pull/1871))
###### Fixes
- Fix an issue when we parse a json string in [E2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2507) and used the parsed json to append to the location (pull #[1864](https://github.com/aws-cloudformation/cfn-python-lint/pull/1864))


### v0.44.3
###### CloudFormation Specifications
- Update spec files as of 2021.01.08 (pull #[1846](https://github.com/aws-cloudformation/cfn-python-lint/pull/1846))
- Update `AWS::Lambda::Function.MemorySize` to new service limits (pull #[1858](https://github.com/aws-cloudformation/cfn-python-lint/pull/1858))
###### Fixes
- Replace `ContentUri` to a s3 path when doing a SAM transform (pull #[1853](https://github.com/aws-cloudformation/cfn-python-lint/pull/1853))
- Add `RouteSelectionExpression` to exludes on rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) (pull #[1852](https://github.com/aws-cloudformation/cfn-python-lint/pull/1852))
- Remove newlines from parseable format messages (pull #[1854](https://github.com/aws-cloudformation/cfn-python-lint/pull/1854))

### v0.44.2
###### CloudFormation Specifications
- Expand Allowed Values for `AWS::AmazonMQ::Broker.EngineVersion` (pull #[1841](https://github.com/aws-cloudformation/cfn-python-lint/pull/1841))
- Update spec files as of 2020.12.30 (pull #[1831](https://github.com/aws-cloudformation/cfn-python-lint/pull/1831))
- Update `AWS::Lambda::EventSourceMapping.EventSourceArn` to allow `StreamARN` and `ConsumerARN` (pull #[1850](https://github.com/aws-cloudformation/cfn-python-lint/pull/1850))
###### Fixes
- Reinitialize [E3022](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3022) on every template (pull #[1848](https://github.com/aws-cloudformation/cfn-python-lint/pull/1848))
- Update rule [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3008) to allow for lists in getatt allowed values (pull #[1850](https://github.com/aws-cloudformation/cfn-python-lint/pull/1850))

### v0.44.1
###### Fixes
- Reinitialize the limits in rule [E3021](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3021) (pull #[1834](https://github.com/aws-cloudformation/cfn-python-lint/pull/1834))
- Add `registry_schemas` to be supported in the `.cfnlintrc` (pull #[1836](https://github.com/aws-cloudformation/cfn-python-lint/pull/1836))

### v0.44.0
###### Features
- Cache all rules to speed up reloading rules when scanning multiple templates (pull #[1789](https://github.com/aws-cloudformation/cfn-python-lint/pull/1789))
###### CloudFormation Specifications
- Update FSx Storage Capacity to a minimum of 32 (pull #[#1827](https://github.com/aws-cloudformation/cfn-python-lint/pull/1827))
- Update spec files as of 2012.12.14 (pull #[1821](https://github.com/aws-cloudformation/cfn-python-lint/pull/1821))
###### Fixes
- Loosen version requirements for python package six (pull #[1825](https://github.com/aws-cloudformation/cfn-python-lint/pull/1825))

### v0.43.0
###### Features
- Add support to validate private types from the CloudFormation Registry (pull #[1732](https://github.com/aws-cloudformation/cfn-python-lint/pull/1732))
###### CloudFormation Specifications
- Update allowed values for AWS::DocDB::DBCluster.EngineVersion (pull #[1810](https://github.com/aws-cloudformation/cfn-python-lint/pull/1810))
- Updated specs as of 2020.12.3 (pull #[1804](https://github.com/aws-cloudformation/cfn-python-lint/pull/1804))
###### Fixes
- Fix an issue with RegexDict to return the longest matched value (pull #[1815](https://github.com/aws-cloudformation/cfn-python-lint/pull/1815))
- Fix rule [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3008) to not fail when using `AWS::ServiceCatalog::CloudFormationProvisionedProduct` `Outputs` (pull #[1809](https://github.com/aws-cloudformation/cfn-python-lint/pull/1809))
- Loosen version constraints on `importlib_resources` (pull #[1808](https://github.com/aws-cloudformation/cfn-python-lint/pull/1808))

### v0.42.0
###### Features
- Add support for modules (pull #[1800](https://github.com/aws-cloudformation/cfn-python-lint/pull/1800) and pull #[1801](https://github.com/aws-cloudformation/cfn-python-lint/pull/1801))
- Colored Output and Pretty Formatting (pull #[1742](https://github.com/aws-cloudformation/cfn-python-lint/pull/1742))
###### CloudFormation Specifications
- Update CloudFormation specs to 21.0.0 (pull #[1799](https://github.com/aws-cloudformation/cfn-python-lint/pull/1799))
###### Fixes
- Patch AWS::EC2::CarrierGateway for Tags (pull #[1790](https://github.com/aws-cloudformation/cfn-python-lint/pull/1790))
- Make sure types are strings before assuming they are (pull #[1791](https://github.com/aws-cloudformation/cfn-python-lint/pull/1791))
- Add all for certain availability zone items (pull #[1798](https://github.com/aws-cloudformation/cfn-python-lint/pull/1798))


### v0.41.0
###### Features
- Remove rules [W2509](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2509), [E2004](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2004), [E2505](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2505), [E2510](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2510) and move logic to rules [E3030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3030), [E3031](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3031), and [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3008) (pull #[1750](https://github.com/aws-cloudformation/cfn-python-lint/pull/1750))
- Remove rule [E2530](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2530) and move logic to [W2030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W203) and [E3030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3030) (pull #[1749](https://github.com/aws-cloudformation/cfn-python-lint/pull/1749))
- Remove rule [E3028](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3028) and move logic to [E3018](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3018) (pull #[1769](https://github.com/aws-cloudformation/cfn-python-lint/pull/1769))
- Remove rule [E3029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3029) and move logic to [E3018](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3018) (pull #[1770](https://github.com/aws-cloudformation/cfn-python-lint/pull/1770))
- Remove rule [E3024](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3024) and move logic to [E3018](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3018) (pull #[1771](https://github.com/aws-cloudformation/cfn-python-lint/pull/1771))
- Update rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) to error when a singular function is used when a list is needed (pull #[1773](https://github.com/aws-cloudformation/cfn-python-lint/pull/1773))
- Update dates for Python 2.7 Lambda runtime support (pull #[1777](https://github.com/aws-cloudformation/cfn-python-lint/pull/1777))
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2503) to include more attributes for application load balancers and protocols (pull #[1783](https://github.com/aws-cloudformation/cfn-python-lint/pull/1783) and pull #[1784](https://github.com/aws-cloudformation/cfn-python-lint/pull/1784))
###### CloudFormation Specifications
- Update CloudFormation specs to 20.3.0 (pull #[1781](https://github.com/aws-cloudformation/cfn-python-lint/pull/1781))
- Expand Allowed Values for `AWS::AmazonMQ::Broker` `EngineVersion` (pull #[1778](https://github.com/aws-cloudformation/cfn-python-lint/pull/1778))
###### Fixes
- Update rule [E2529](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2529) to allow for two subscriptions per log group (pull #[1767](https://github.com/aws-cloudformation/cfn-python-lint/pull/1767))
- Allow SAM translation for `AutoPublishAlias` in `Globals` (pull #[1768](https://github.com/aws-cloudformation/cfn-python-lint/pull/1768))
- Allow numbers and booleans when doing a `Fn::Sub` parameter (pull #[1774](https://github.com/aws-cloudformation/cfn-python-lint/pull/1774))


### v0.40.0
###### Features
- Add rule [E3017](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3017) to validate when properties are required based on a value of another property (pull #[1746](https://github.com/aws-cloudformation/cfn-python-lint/pull/1746))
- Add rule [E3018](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3018) to validate when properties are unwanted based on the value of another property (pull #[1759](https://github.com/aws-cloudformation/cfn-python-lint/pull/1759))
- Remove rule [E3040](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3040) and replace with rule [E3031](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3031) (pull #[1754](https://github.com/aws-cloudformation/cfn-python-lint/pull/1754))
- Remove rule [E3023](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3023) and replace with rule [E3017](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3017) (pull #[1758](https://github.com/aws-cloudformation/cfn-python-lint/pull/1758))
###### CloudFormation Specifications
- Update CloudFormation specs to 20.0.0 (pull #[1760](https://github.com/aws-cloudformation/cfn-python-lint/pull/1760))
- Add allowed values for `AWS::Lambda::EventSourceMapping` (pull #[1748](https://github.com/aws-cloudformation/cfn-python-lint/pull/1748))

### v0.39.0
###### Features
- Allow ignoring of [E0000](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E0000) and [E0001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E0001) (pull #[1580](https://github.com/aws-cloudformation/cfn-python-lint/pull/1580))
- Update rule [E3005](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3005) to include resource based conditions (pull #[1738](https://github.com/aws-cloudformation/cfn-python-lint/pull/1738))
- Update template limits to new [standards](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html) (pull #[1747](https://github.com/aws-cloudformation/cfn-python-lint/pull/1747))
###### CloudFormation Specifications
- Update CloudFormation specs to 19.0.0 (pull #[1751](https://github.com/aws-cloudformation/cfn-python-lint/pull/1751))
- Add `ap-northeast-2d` to the list of approved Availibility Zones (pull #[1739](https://github.com/aws-cloudformation/cfn-python-lint/pull/1739))
- Add AllowedValues to `AWS::CloudFormation::StackSet.PermissionModel` from botocore (pull #[1741](https://github.com/aws-cloudformation/cfn-python-lint/pull/1741))

### v0.38.0
###### Features
- Expand `likely_stateful_resource_types` for explicit UpdateReplacePolicy/DeletionPolicy rule [I3011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3011) to include `AWS::SQS::Queue` (pull #[1736](https://github.com/aws-cloudformation/cfn-python-lint/pull/1736))
###### CloudFormation Specifications
- Update CloudFormation specs to 18.7.0 (pull #[1734](https://github.com/aws-cloudformation/cfn-python-lint/pull/1734))
###### Fixes
- Fix an issue with rule [E3003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3003) to handle `Ref: AWS::Novalue` (pull #[1720](https://github.com/aws-cloudformation/cfn-python-lint/pull/1720))

### v0.37.1
###### CloudFormation Specifications
- Update CloudFormation specs to 18.6.0 (pull #[1726](https://github.com/aws-cloudformation/cfn-python-lint/pull/1726))
- Add `AllowedValues` for `AWS::DMS::Endpoint.EngineName` (pull #[1725](https://github.com/aws-cloudformation/cfn-python-lint/pull/1725))
###### Fixes
- Fix an issue with rule [E2521](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2521) and [E2520](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2520) to handle `Ref: AWS::Novalue` (pull #[1717](https://github.com/aws-cloudformation/cfn-python-lint/pull/1717), #[1719](https://github.com/aws-cloudformation/cfn-python-lint/pull/1719))

### v0.37.0
###### CloudFormation Specifications
- Update CloudFormation specs to 18.5.0 (pull #[1715](https://github.com/aws-cloudformation/cfn-python-lint/pull/1715))
- Get `AllowedValues` from Botocore during `--update-specs` (pull #[1682](https://github.com/aws-cloudformation/cfn-python-lint/pull/1682))
- Add string length requirements for `AWS::Config::ConfigRule.Description` (pull #[1712](https://github.com/aws-cloudformation/cfn-python-lint/pull/1712))
- Patch `AWS::StepFunctions::Activity` to include `Name` and remove `Arn` (pull #[1722](https://github.com/aws-cloudformation/cfn-python-lint/pull/1722))
###### Fixes
- Fix an issue with rule `E3002` to better handle when conditions are used at the root level of a list (pull #[1714](https://github.com/aws-cloudformation/cfn-python-lint/pull/1714))
- Update core node libraries to remove `Ref: AWS::NoValue` from returned properties (pull #[1716](https://github.com/aws-cloudformation/cfn-python-lint/pull/1716))

### v0.36.1
###### CloudFormation Specifications
- Update CloudFormation specs to 18.4.0 (pull #[1707](https://github.com/aws-cloudformation/cfn-python-lint/pull/1707))
- Add `ap-northeast-3` to `scripts/update_specs_services_from_ssm.py` (pull #[1703](https://github.com/aws-cloudformation/cfn-python-lint/pull/1703))

### v0.36.0
###### Features
- Update rule [E2541](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2541) to validate that input artifacts are output artifacts from a previous action and that output artifact names are unique in the pipeline (pull #[1690](https://github.com/aws-cloudformation/cfn-python-lint/pull/1690))
- New rule [E3007](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3007) to validate parameter and resource names are unique (pull #[1698](https://github.com/aws-cloudformation/cfn-python-lint/pull/1698))
###### CloudFormation Specifications
- Update CloudFormation specs to 18.3.0 (pull #[1697](https://github.com/aws-cloudformation/cfn-python-lint/pull/1697))
- Expand `AllowedValues` for `AWS::AmazonMQ::Broker.EngineVersion` and `AWS::Glue::Trigger.Condition.State` (pull #[1680](https://github.com/aws-cloudformation/cfn-python-lint/pull/1680), #[1681](https://github.com/aws-cloudformation/cfn-python-lint/pull/1681))
###### Fixes
- Expand `templated_exceptions` property types that require package command for rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) and [W3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W3002) (pull #[1684](https://github.com/aws-cloudformation/cfn-python-lint/pull/1684))
- Pin pyrsistent to `0.16.0` with Python versions less than `3.5` (pull #[1693](https://github.com/aws-cloudformation/cfn-python-lint/pull/1693))
- Fix an issue with SSM Spec patching that resulted in resource `PropertyTypes` not being added to the spec patches (pull #[1696](https://github.com/aws-cloudformation/cfn-python-lint/pull/1696))
- Update directives to use the resource name key as the start (pull #[1692](https://github.com/aws-cloudformation/cfn-python-lint/pull/1692))

### v0.35.1
###### CloudFormation Specifications
- Update CloudFormation specs to 18.1.0 (pull #[1671](https://github.com/aws-cloudformation/cfn-python-lint/pull/1671))
- Expand `AllowedValues` for `AWS::CloudFront::Distribution.MinimumProtocolVersion`, `AWS::Config::ConfigurationRecorder.ResourceTypes`, and `AWS::Glue::Connection.ConnectionInput.ConnectionType` (pull #[1661](https://github.com/aws-cloudformation/cfn-python-lint/pull/1661), #[1664](https://github.com/aws-cloudformation/cfn-python-lint/pull/1664), #[1673](https://github.com/aws-cloudformation/cfn-python-lint/pull/1673))
- Add localzone `us-west-2-lax-1b` (pull #[1670](https://github.com/aws-cloudformation/cfn-python-lint/pull/1670))
###### Fixes
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2503) to include `routing.http.desync_mitigation_mode` (pull #[1660](https://github.com/aws-cloudformation/cfn-python-lint/pull/1660))
- Update excludes for rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to include `ResponseMappingTemplate` (pull #[1667](https://github.com/aws-cloudformation/cfn-python-lint/pull/1667))
- Update rule [E1019](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1019) and [E1010](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1010) to handle resource attributes of type `Map` (pull #[1659](https://github.com/aws-cloudformation/cfn-python-lint/pull/1659))

### v0.35.0
###### CloudFormation Specifications
- Update CloudFormation specs to 17.0.0 (pull #[1653](https://github.com/aws-cloudformation/cfn-python-lint/pull/1653))
- Fix ElasticMapReduce and ManagedBlockchain InstanceType patching (pull #[1654](https://github.com/aws-cloudformation/cfn-python-lint/pull/1654))
- Include a regex pattern to check MetricValue is either a number or starts with `$` (pull #[1647](https://github.com/aws-cloudformation/cfn-python-lint/pull/1647))
- Add more types to `AWS::ApplicationAutoScaling::ScalingPolicy.PredefinedMetricSpecification.PredefinedMetricType` (pull #[1652](https://github.com/aws-cloudformation/cfn-python-lint/pull/1652))
- Add more values to `AWS::Lambda::Function.Runtime` (pull #[1651](https://github.com/aws-cloudformation/cfn-python-lint/pull/1651) and pull #[1649](https://github.com/aws-cloudformation/cfn-python-lint/pull/1649))
- Add more values to `AWS::Budgets::Budget.BudgetType` (pull #[1643](https://github.com/aws-cloudformation/cfn-python-lint/pull/1643))
###### Fixes
- Update rule [E3031](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3031) to convert int or float to string before doing an allowed pattern match on it (pull #[1647](https://github.com/aws-cloudformation/cfn-python-lint/pull/1647))
- Add exceptions to rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) (pull #[1646](https://github.com/aws-cloudformation/cfn-python-lint/pull/1646) and pull #[1648](https://github.com/aws-cloudformation/cfn-python-lint/pull/1648))
- Update rule [E8003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E8003) to look for string based parameters (pull #[1640](https://github.com/aws-cloudformation/cfn-python-lint/pull/1640))

### v0.34.1
###### CloudFormation Specifications
- Update CloudFormation specs to 16.3.0 (pull #[1635](https://github.com/aws-cloudformation/cfn-python-lint/pull/1635))
###### Fixes
- Update rule [E3001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3001) to catch when Resource `Type` is not a string (pull #[1631](https://github.com/aws-cloudformation/cfn-python-lint/pull/1631))
- Update rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to handle `${}` in Step Function State Machines and Definition Substitutions (pull #[1628](https://github.com/aws-cloudformation/cfn-python-lint/pull/1628))
- Update rule [W4002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W4002) to only look at `Ref` and `Sub` (pull #[1627](https://github.com/aws-cloudformation/cfn-python-lint/pull/1627))

### v0.34.0
###### Features
- Add rule [W4002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W4002) that checks if `Metadata` references a `NoEcho` parameter (pull #[1613](https://github.com/aws-cloudformation/cfn-python-lint/pull/1613))
###### CloudFormation Specifications
- Update CloudFormation specs to 16.1.0 (pull #[1622](https://github.com/aws-cloudformation/cfn-python-lint/pull/1622))
- Remove `AWS::EC2::LaunchTemplate.BlockDeviceMapping` from `OnlyOne` (pull #[1617](https://github.com/aws-cloudformation/cfn-python-lint/pull/1617))
- Add more `AllowedValues` to `AWS::Glue::Trigger.Predicate.Logical` (pull #[1616](https://github.com/aws-cloudformation/cfn-python-lint/pull/1616))
- Add more `AllowedValues` to `AWS::ApplicationAutoScaling::ScalingPolicy.PredefinedMetricSpecification.PredefinedMetricType` (pull #[1604](https://github.com/aws-cloudformation/cfn-python-lint/pull/1604))
- Add more `AllowedValues` to `AWS::S3::Bucket.TopicConfiguration.Event` (pull #[1606](https://github.com/aws-cloudformation/cfn-python-lint/pull/1606))
- Add more `AllowedValues` to `AWS::EC2::CapacityReservation.InstancePlatform` (pull #[1605](https://github.com/aws-cloudformation/cfn-python-lint/pull/1605))
- Fix an issue for applying `AllowedValues` to `AWS::RDS::DBInstance MonitoringInterval` and `PerformanceInsightsRetentionPeriod` (pull #[1607](https://github.com/aws-cloudformation/cfn-python-lint/pull/1607))
- Fix an issue for applying `Maximum` and `Minimum` to `AWS::ElasticLoadBalancingV2::ListenerRule.Priority` (pull #[1608](https://github.com/aws-cloudformation/cfn-python-lint/pull/1608))
###### Fixes
- Update rule [E3503](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3503) to not fail on if ValidationDomain or DomainName aren't present (pull #[1620](https://github.com/aws-cloudformation/cfn-python-lint/pull/1620))

### v0.33.2
###### Features
- Upgrade SAM Translator to v1.25.0 (pull #[1594](https://github.com/aws-cloudformation/cfn-python-lint/pull/1594))
###### CloudFormation Specifications
- Update CloudFormation specs to 15.3.0 (pull #[1600](https://github.com/aws-cloudformation/cfn-python-lint/pull/1600))
###### Fixes
- Update rule [E3401](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3401) to not fail on Apex records (pull #[1599](https://github.com/aws-cloudformation/cfn-python-lint/pull/1599))

### v0.33.1
###### CloudFormation Specifications
- Update CloudFormation specs to 15.1.0 (pull #[1593](https://github.com/aws-cloudformation/cfn-python-lint/pull/1593))
- Add additional allowed values for `AWS::SecretsManager::SecretTargetAttachment.TargetType` (pull #[1573](https://github.com/aws-cloudformation/cfn-python-lint/pull/1573))
- Add property types for `AvailabilityZone` in the `AWS::DMS::ReplicationInstance` and `AWS::EC2::Subnet` resources (pull #[1585](https://github.com/aws-cloudformation/cfn-python-lint/pull/1585))
- Expand allowed values for `AWS::CodeBuild::Project.Environment.Type` (pull #[1589](https://github.com/aws-cloudformation/cfn-python-lint/pull/1589))
###### Fixes
- Update rule [E2004](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2004) to not check AllowedValues when the Type is `AWS::SSM::Parameter::Value<String>` (pull #[1571](https://github.com/aws-cloudformation/cfn-python-lint/pull/1571))
- Update Transform logic to not update DefinitionUri to S3 when not using DefinitionUri originally (pull #[1576](https://github.com/aws-cloudformation/cfn-python-lint/pull/1576))

### v0.33.0
###### Features
- Upgrade SAM Translator to v1.24.0 (pull #[1562](https://github.com/aws-cloudformation/cfn-python-lint/pull/1562))
- Warning messages for Python 3.4 and 2.7 (pull #[1337](https://github.com/aws-cloudformation/cfn-python-lint/pull/1337))
- Add `--output-file` parameter to output the results into a file (pull #[1511](https://github.com/aws-cloudformation/cfn-python-lint/pull/1511))
- Remove usage of jsonpointer (pull #[1546](https://github.com/aws-cloudformation/cfn-python-lint/pull/1546))
- Add rule [E3042](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3042) that checks AWS::ECS::TaskDefinition.ContainerDefinition has at least one essential container (pull #[1548](https://github.com/aws-cloudformation/cfn-python-lint/pull/1548))
###### CloudFormation Specifications
- Update CloudFormation specs to 14.4.0 (pull #[1555](https://github.com/aws-cloudformation/cfn-python-lint/pull/1555))
- Add allowed patterns and values for properties in `AWS::S3::Bucket.InventoryConfiguration` (pull #[1551](https://github.com/aws-cloudformation/cfn-python-lint/pull/1551))
###### Fixes
- Update Transform logic to support local files for the state machine defintion (pull #[1562](https://github.com/aws-cloudformation/cfn-python-lint/pull/1562)) 

### v0.32.1
###### Features
- Adding [`Hooks`](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/blue-green.html) template section to rule [E1001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1001) (pull #[1543](https://github.com/aws-cloudformation/cfn-python-lint/pull/1543))

### v0.32.0
###### Features
- New rule [E3041](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3041) to check if `HostedZoneName` is a super domain for `Name` (pull #[1483](https://github.com/aws-cloudformation/cfn-python-lint/pull/1483))
- Update SAM Translator dependency to `1.23.0` (pull #[1536](https://github.com/aws-cloudformation/cfn-python-lint/pull/1536))
- Move Template and Runner classes into their own files (pull #[1523](https://github.com/aws-cloudformation/cfn-python-lint/pull/1523))
###### CloudFormation Specifications
- Update CloudFormation specs to 14.3.0 (pull #[1538](https://github.com/aws-cloudformation/cfn-python-lint/pull/1538))
- Add instance type allowed values to ElastiCache, Elasticsearch, ElasticMapReduce, ManagedBlockchain, GameLift, and AppStream (pull #[1535](https://github.com/aws-cloudformation/cfn-python-lint/pull/1535) and #[1541](https://github.com/aws-cloudformation/cfn-python-lint/pull/1541))

### v0.31.1
###### Fixes
- Exempting resource types [AWS::Serverless transform](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/transform-aws-serverless.html) creates that violated rule [W3011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W3011) (pull #[1529](https://github.com/aws-cloudformation/cfn-python-lint/pull/1529))

### v0.31.0
###### Features
- Add support for `.cfnlintrc.yaml` and `.cfnlintrc.yml` (pull #[1504](https://github.com/aws-cloudformation/cfn-python-lint/pull/1504))
- Add JUnit XML output format (pull #[1506](https://github.com/aws-cloudformation/cfn-python-lint/pull/1506))
###### CloudFormation Specifications
- Update CloudFormation specs to 14.2.0 (pull #[1526](https://github.com/aws-cloudformation/cfn-python-lint/pull/1526))
- Update `AWS::AutoScaling::LaunchConfiguration` `SecurityGroups` to support GroupID and Names (pull #[1505](https://github.com/aws-cloudformation/cfn-python-lint/pull/1505))
- Add min max and allowed values for multiple WAFv2 rate rules `Limit` rules (pull #[1507](https://github.com/aws-cloudformation/cfn-python-lint/pull/1507))

### v0.30.1
###### Features
- Add the ability to specify a config file using parameter `--config-file` (pull #[1462](https://github.com/aws-cloudformation/cfn-python-lint/pull/1462))
- Speed up `--update-specs` to not download files if they haven't updated (pull #[1383](https://github.com/aws-cloudformation/cfn-python-lint/pull/1383))
###### CloudFormation Specifications
- Add region `eu-south-1` (pull #[1496](https://github.com/aws-cloudformation/cfn-python-lint/pull/1496))
- Add region `af-south-1` (pull #[1494](https://github.com/aws-cloudformation/cfn-python-lint/pull/1494))
- Update CloudFormation specs to 14.0.0 (pull #[1494](https://github.com/aws-cloudformation/cfn-python-lint/pull/1494))
- Add new Config supported types `AWS::SecretsManager::Secret` and `AWS::SNS::Topic` (pull #[1492](https://github.com/aws-cloudformation/cfn-python-lint/pull/1492))
###### Fixes
- Update rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to have an exception for `RequestMappingTemplate` in AppSync (pull #[1488](https://github.com/aws-cloudformation/cfn-python-lint/pull/1488))
- Update rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to have an exception for `ConnectionID` in API Gateway (pull #[1493](https://github.com/aws-cloudformation/cfn-python-lint/pull/1493))

### v0.29.6
###### CloudFormation Specifications
- Update Lambda runtimes to support `dotnetcore3.1` (pull #[1469](https://github.com/aws-cloudformation/cfn-python-lint/pull/1469))
- Update DMS Engine approved values with multiple items (pull #[1472](https://github.com/aws-cloudformation/cfn-python-lint/pull/1472))
- Add description allowed value regex to `AWS::EC2::SecurityGroup` Ingress/Egress (pull #[1476](https://github.com/aws-cloudformation/cfn-python-lint/pull/1476))
- Update CloudFormation specs to 13.0.0 (pull #[1480](https://github.com/aws-cloudformation/cfn-python-lint/pull/1480))
###### Fixes
- Set `importlib_resources` to 1.4 for all Pythons except 3.4 (pull #[1479](https://github.com/aws-cloudformation/cfn-python-lint/pull/1479))

### v0.29.5
###### CloudFormation Specifications
- Update CloudFormation specs to 12.3.0 (pull #[1464](https://github.com/aws-cloudformation/cfn-python-lint/pull/1464))
###### Fixes
- Fix an issue when including `cfn-lint` and needing `networkx` (pull #[1458](https://github.com/aws-cloudformation/cfn-python-lint/issues/1458))

### v0.29.4
###### Features
- Add `--build-graph` parameter to create a graph of dependencies (pull #[1411](https://github.com/aws-cloudformation/cfn-python-lint/pull/1411))
###### CloudFormation Specifications
- Update CloudFormation specs to 12.1.0 (pull #[1455](https://github.com/aws-cloudformation/cfn-python-lint/pull/1455))
###### Fixes
- Add `found unknown escape character` to start of err problem to determine when to use json parsing (pull #[1454](https://github.com/aws-cloudformation/cfn-python-lint/pull/1454))

### v0.29.3
###### CloudFormation Specifications
- Update CloudFormation specs to 12.0.0 (pull #[1448](https://github.com/aws-cloudformation/cfn-python-lint/pull/1448))
###### Fixes
- Add region `ca-central-1d` (pull #[1447](https://github.com/aws-cloudformation/cfn-python-lint/pull/1447))

### v0.29.2
###### Fixes
- Update exceptions in rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to include `BuildSpec` (pull #[1444](https://github.com/aws-cloudformation/cfn-python-lint/pull/1444))

### v0.29.1
###### Features
- Switch DB Instance Engine check from [E3030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3030) to [E3040](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3040) so the comparison is case insensitive (pull #[1441](https://github.com/aws-cloudformation/cfn-python-lint/pull/1441))
###### CloudFormation Specifications
- Update CloudFormation specs to 11.6.0 (pull #[1433](https://github.com/aws-cloudformation/cfn-python-lint/pull/1433))
- Add `ruby2.7` to supported list of ruby runtimes (pull #[1436](https://github.com/aws-cloudformation/cfn-python-lint/pull/1436))
###### Fixes
- Update regex in rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to be more optimal and not hang on large strings (pull #[1430](https://github.com/aws-cloudformation/cfn-python-lint/pull/1430))

### v0.29.0
###### Features
- Update SAM Translator package to 1.21.0 (pull #[1406](https://github.com/aws-cloudformation/cfn-python-lint/pull/1406))
- Update rule [E3027](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3027) to check that either Day of Month or Day of Week is a question mark (pull #[1405](https://github.com/aws-cloudformation/cfn-python-lint/pull/1405))
- New rule [E3029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3029) to check `AWS::RDS::DBInstance` `Aurora` databases don't have certain properties (pull #[1409](https://github.com/aws-cloudformation/cfn-python-lint/pull/1409))
- Build a resource graph for checking circular dependencies (pull #[1391](https://github.com/aws-cloudformation/cfn-python-lint/pull/1391))
###### CloudFormation Specifications
- Update Exclusive and Only One specs to include additional rules around Security Group Rules (pull #[1407](https://github.com/aws-cloudformation/cfn-python-lint/pull/1407))
- Update CloudFormation specs to 11.5.0 (pull #[1416](https://github.com/aws-cloudformation/cfn-python-lint/pull/1416))
- Patch spec so that TTL is Long on Route53 Change Record Sets (pull #[1417](https://github.com/aws-cloudformation/cfn-python-lint/pull/1417))

### v0.28.4
###### CloudFormation Specifications
- Update CloudFormation specs to 11.4.0 (pull #[1403](https://github.com/aws-cloudformation/cfn-python-lint/pull/1403))
###### Fixes
- Properly display yaml parse errors when the error was a tab (pull #[1402](https://github.com/aws-cloudformation/cfn-python-lint/pull/1402))

### v0.28.3
###### Features
- Define an initial Docker file (pull #[1361](https://github.com/aws-cloudformation/cfn-python-lint/pull/1361))
###### CloudFormation Specifications
- Update CloudFormation specs to 11.2.0 (pull #[1390](https://github.com/aws-cloudformation/cfn-python-lint/pull/1390))
- Add allowed values for `AWS::RDS::DBInstance` `Engine` (pull #[1398](https://github.com/aws-cloudformation/cfn-python-lint/pull/1398))
###### Fixes
- Update rule [E3039](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3039) to properly filter down attributes before checking values (pull #[1392](https://github.com/aws-cloudformation/cfn-python-lint/pull/1392))
- Update rule [E1019](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1019) to not join GetAtt if they aren't strings (pull #[1389](https://github.com/aws-cloudformation/cfn-python-lint/pull/1389))
- Consolidate region and spec information into singular item (pull #[1357](https://github.com/aws-cloudformation/cfn-python-lint/pull/1357))

### v0.28.2
###### CloudFormation Specifications
- Update CloudFormation specs to 11.1.0 (pull #[1380](https://github.com/aws-cloudformation/cfn-python-lint/pull/1380))
- Patch specs from updated SSM and pricing data as of 2020.02.21 (pull #[1380](https://github.com/aws-cloudformation/cfn-python-lint/pull/1380))
- Update AWS Config supported types to those active on 2020.02.20 (pull #[1378](https://github.com/aws-cloudformation/cfn-python-lint/pull/1378))
###### Fixes
- Update condition logic to return dict_node instead of the standard dict node (pull #[1375](https://github.com/aws-cloudformation/cfn-python-lint/pull/1375))
- Fix `--update-specs` on Windows to have the appropriate seperator (pull #[1371](https://github.com/aws-cloudformation/cfn-python-lint/pull/1371))
- Update the documentation for `--update-documentation` (pull #[1374](https://github.com/aws-cloudformation/cfn-python-lint/pull/1374))

### v0.28.1
###### Features
- Add option to disable [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) using a regex pattern on the variable name (pull #[1362](https://github.com/aws-cloudformation/cfn-python-lint/pull/1362))
###### Fixes
- Update decode node class to pass back an empty list when default is None and the key doesn't exist (pull #[1364](https://github.com/aws-cloudformation/cfn-python-lint/pull/1364))

### v0.28.0
###### Features
- Add rule [E3028](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3028) to check that `ScalingConfiguration` is only specified with Aurora databases (pull #[1338](https://github.com/aws-cloudformation/cfn-python-lint/pull/1338))
- Add rule [E3039](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3039) to check that `AttributeDefinitions` match `KeySchemas` (pull #[1284](https://github.com/aws-cloudformation/cfn-python-lint/pull/1284))
###### CloudFormation Specifications
- Add `AFTER_7_DAYS` to `TransitionToIA` as accepted value (pull #[1352](https://github.com/aws-cloudformation/cfn-python-lint/pull/1352))
- Update CloudFormation specs to 11.0.0 (pull #[1355](https://github.com/aws-cloudformation/cfn-python-lint/pull/1355))
- Patch specs from updated SSM and pricing data as of 2020.02.15 (pull #[1356](https://github.com/aws-cloudformation/cfn-python-lint/pull/1356))

### v0.27.5
###### Features
- Add scripts to build an offline installer (pull #[1307](https://github.com/aws-cloudformation/cfn-python-lint/pull/1307))
###### CloudFormation Specifications
- Update CloudFormation specs to 10.5.0 (pull #[1347](https://github.com/aws-cloudformation/cfn-python-lint/pull/1347))
- Patch specs from updated SSM and pricing data as of 2020.02.09 (pull #[1348](https://github.com/aws-cloudformation/cfn-python-lint/pull/1348))

### v0.27.4
###### Features
- Add Python 3.8 support (pull #[1334](https://github.com/aws-cloudformation/cfn-python-lint/pull/1334))
- Add more resources to rule [I3011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3011) (pull #[1331](https://github.com/aws-cloudformation/cfn-python-lint/pull/1331))
###### CloudFormation Specifications
- Patch specs from updated SSM service data as of 2020.01.30 (pull #[1339](https://github.com/aws-cloudformation/cfn-python-lint/pull/1339))
- Patch more wafv2 resources (pull #[1343](https://github.com/aws-cloudformation/cfn-python-lint/pull/1343))
###### Fixes
- Pin version of jsonpatch for Python 3.4 (pull #[1336](https://github.com/aws-cloudformation/cfn-python-lint/pull/1336))

### v0.27.3
###### CloudFormation Specifications
- Update CloudFormation specs to 10.4.0 (pull #[1330](https://github.com/aws-cloudformation/cfn-python-lint/pull/1330))

### v0.27.2
###### Fixes
- Update rule [E3026](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3026) to better check for condition scenarios and not fail (pull #[1327](https://github.com/aws-cloudformation/cfn-python-lint/pull/1327))

### v0.27.1
###### CloudFormation Specifications
- Update CloudFormation patches to include pricing and SSM data from 2020.01.20 (pull #[1322](https://github.com/aws-cloudformation/cfn-python-lint/pull/1322))
###### Fixes
- Update rule [E6001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E6001) to allow `Fn::Transform` (pull #[1321](https://github.com/aws-cloudformation/cfn-python-lint/pull/1321))

### v0.27.0
###### Features
- Add additional configuration checks to rule [E2001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2001) (pull #[1301](https://github.com/aws-cloudformation/cfn-python-lint/pull/1301))
- Add additional configuration checks to rule [E6001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E6001) (pull #[1301](https://github.com/aws-cloudformation/cfn-python-lint/pull/1301))
- Move `Export` `Name` required from `Outputs` in rule [E6002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E6002) to [E6001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E6001) (pull #[1301](https://github.com/aws-cloudformation/cfn-python-lint/pull/1301))
- Move checking for list in `Outputs` `Value` in rule [E6003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E6003) to [E6001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E6001) (pull #[1301](https://github.com/aws-cloudformation/cfn-python-lint/pull/1301))
- Add rules [I1002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I1002), [I1003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I1003), [I2010](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I2010), [I2011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I2011), [I2012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I2012), [I3010](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3010), [I3011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3011), [I6010](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I6010), [I6011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I6011), [I6012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I6012), [I7010](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I7010), [I7011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I7011), [I7012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I7012) to alert when approaching limits (pull #[1271](https://github.com/aws-cloudformation/cfn-python-lint/pull/1271))
###### CloudFormation Specifications
- Update CloudFormation specs to 10.3.0 (pull #[1317](https://github.com/aws-cloudformation/cfn-python-lint/pull/1317))
- Patch wafV2 Resources in the CloudFormation spec (pull #[1313](https://github.com/aws-cloudformation/cfn-python-lint/pull/1313))
###### Fixes
- Update rules [E6001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E6001), [E6002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E6002), [E6003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E6003) to filter out unneeded columns when processing conditions (pull #[1316](https://github.com/aws-cloudformation/cfn-python-lint/pull/1316))
- Update rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to allow for exlusions in `NotResource` (pull #[1315](https://github.com/aws-cloudformation/cfn-python-lint/pull/1315))
- Update rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020) to check for string types before doing regex (pull #[1311](https://github.com/aws-cloudformation/cfn-python-lint/pull/1311))

### v0.26.3
###### Features
- Add extra attributes to rules [E1024](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1024), [E3027](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3027), [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020) (pull #[1272](https://github.com/aws-cloudformation/cfn-python-lint/pull/1272))
###### CloudFormation Specifications
- Move `AWS::S3::Bucket.RoutingRuleCondition` properties from OnlyOne to AtLeastOne (pull #[1283](https://github.com/aws-cloudformation/cfn-python-lint/pull/1283))
- Add `AWS::SSM::Parameter.Value` to the `AWS::EC2::VPC.Id` type (pull #[1288](https://github.com/aws-cloudformation/cfn-python-lint/pull/1288))
- Add `CNAME` as an allowed value to `ServiceDiscoveryDnsType` (pull #[1296](https://github.com/aws-cloudformation/cfn-python-lint/pull/1296))
- Patch `AWS::WAFv2::RegexPatternSet.RegularExpressionList` removing extra layer (pull #[1300](https://github.com/aws-cloudformation/cfn-python-lint/pull/1300))
- Add `LambdaProvisionedConcurrencyUtilization` as allowed value to Application Autoscaling Metric (pull #[1303](https://github.com/aws-cloudformation/cfn-python-lint/pull/1303))
- Add some exclusive attributes to `AWS::CloudWatch::Alarm` for `Metrics` and `Threshold` (pull #[1306](https://github.com/aws-cloudformation/cfn-python-lint/pull/1306))
###### Fixes
- pyyaml has ended support for Python 3.4.  Pin pyyaml to version 5.2 for Python 3.4 (pull #[1290](https://github.com/aws-cloudformation/cfn-python-lint/pull/1290))
- Convert from using imp to importlib for python 3.x (pull #[1292](https://github.com/aws-cloudformation/cfn-python-lint/pull/1292))

### v0.26.2
###### Features
- Update `aws-sam-translator` to `1.19.1` (pull #[1275](https://github.com/aws-cloudformation/cfn-python-lint/pull/1275))
###### CloudFormation Specifications
- Update CloudFormation specs to 10.2.0 (pull #[1273](https://github.com/aws-cloudformation/cfn-python-lint/pull/1273))
- Update EOL dates for Python 2.7 (pull #[1270](https://github.com/aws-cloudformation/cfn-python-lint/pull/1270))
###### Fixes
- Update rule [W3011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W3011) /[I3011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3011)  to include resource path in message (pull #[1266](https://github.com/aws-cloudformation/cfn-python-lint/pull/1266))

### v0.26.1
###### Features
- New rule [I3011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3011) to check stateful resources have a set UpdateReplacePolicy/DeletionPolicy (pull #[1232](https://github.com/aws-cloudformation/cfn-python-lint/pull/1232))
###### CloudFormation Specifications
- Update CloudFormation specs to 10.1.0 (pull #[1255](https://github.com/aws-cloudformation/cfn-python-lint/pull/1255))
- Add `ALLOW_` values to `ExplicitAuthFlows` (pull #[1261](https://github.com/aws-cloudformation/cfn-python-lint/pull/1261))
###### Fixes
- Update rule [W3011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W3011) to ignore W3011 if explicit DeletionPolicy/UpdateReplacePolicy value is Delete (pull #[1253](https://github.com/aws-cloudformation/cfn-python-lint/pull/1253))
- Update rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to not alert when looking at Parameters (pull #[1256](https://github.com/aws-cloudformation/cfn-python-lint/pull/1256))
- Update rule [E2504](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2504) to allow for ephemeral(0-23) (pull #[1260](https://github.com/aws-cloudformation/cfn-python-lint/pull/1260))

### v0.26.0
###### Features
- Created a new `mandatory-checks` parameter to require rules to be reported on and not ignored (pull #[1243](https://github.com/aws-cloudformation/cfn-python-lint/pull/1243))
- Allow using modules when doing `append-rules` (pull #[1216](https://github.com/aws-cloudformation/cfn-python-lint/pull/1216))
- Add support for the new zone `us-west-2-lax-1a` (pull #[1241](https://github.com/aws-cloudformation/cfn-python-lint/pull/1241))
###### CloudFormation Specifications
- Update CloudFormation specs to 10.0.0 (pull #[1247](https://github.com/aws-cloudformation/cfn-python-lint/pull/1247))
###### Fixes
- Update rule [E8001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E8001) to allow for `Condition` (pull #[1246](https://github.com/aws-cloudformation/cfn-python-lint/pull/1246))

### v0.25.7
###### CloudFormation Specifications
- Update pricing and services from 2019.12.02 (pull #[1237](https://github.com/aws-cloudformation/cfn-python-lint/pull/1237))
- Update to specs to 9.1.1 (pull #[1237](https://github.com/aws-cloudformation/cfn-python-lint/pull/1237))
###### Fixes
- `EnableVersionUpgrade` added to the recognized values for `UpdatePolicy` (pull #[1231](https://github.com/aws-cloudformation/cfn-python-lint/pull/1231))
- Include `pathlib2` in python 3.4 requirements (pull #[1236](https://github.com/aws-cloudformation/cfn-python-lint/pull/1236))
- Look at the top level Condition operator (pull #[1235](https://github.com/aws-cloudformation/cfn-python-lint/pull/1235))
- Include more testing for using cfn-lint as a module (pull #[1234](https://github.com/aws-cloudformation/cfn-python-lint/pull/1234))

### 0.25.5
###### CloudFormation Specifications
- Update CloudFormation specs to 9.1.0 (pull #[1224](https://github.com/aws-cloudformation/cfn-python-lint/pull/1224))
- Add Allowed Pattern to Bucket Names (pull #[1208](https://github.com/aws-cloudformation/cfn-python-lint/pull/1208))
###### Fixes
- Update rule [E2001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2001) to look for required properties (pull #[1227](https://github.com/aws-cloudformation/cfn-python-lint/pull/1227))
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2503) to allow `routing.http.drop_invalid_header_fields.enabled` for application load balancers (pull #[1220](https://github.com/aws-cloudformation/cfn-python-lint/pull/1220))
- Update rule [E1028](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1028) to check that Fn::If value is a list of length 3 (pull #[1226](https://github.com/aws-cloudformation/cfn-python-lint/pull/1226))

### 0.25.3
###### CloudFormation Specifications
- Change DocDB allowed EngineVersion value to 3.6.0 (pull #[1213](https://github.com/aws-cloudformation/cfn-python-lint/pull/1213))
###### Fixes
- Update rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) to handle nested IFs when looking at lists (pull #[1212](https://github.com/aws-cloudformation/cfn-python-lint/pull/1212))
- Update rule [W2501](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2501) to only look at a Resource Properties (pull #[1214](https://github.com/aws-cloudformation/cfn-python-lint/pull/1214))

### 0.25.2
###### CloudFormation Specifications
- Add capacityOptimized to spot fleet allocation strategy (pull #[1200](https://github.com/aws-cloudformation/cfn-python-lint/pull/1200))
- Update Lambda runtime options to be valid as of 2019.11.19 (pull #[1204](https://github.com/aws-cloudformation/cfn-python-lint/pull/1204))

### 0.25.1
###### CloudFormation Specifications
- Update allowed values for AWS Config types (pull #[1197](https://github.com/aws-cloudformation/cfn-python-lint/pull/1197))
- Update CloudFormation specs to 8.1.0 (pull #[1197](https://github.com/aws-cloudformation/cfn-python-lint/pull/1197))

### 0.25.0
###### Features
- Add rule [I1022](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I1022) to recommend Sub over Join when join is using empty delimiter (pull #[1067](https://github.com/aws-cloudformation/cfn-python-lint/pull/1067))
- Remove setuptools requirement (pull #[1188](https://github.com/aws-cloudformation/cfn-python-lint/pull/1188))
###### CloudFormation Specifications
- Update Lambda runtime versions EOL date (pull #[1180](https://github.com/aws-cloudformation/cfn-python-lint/pull/1180))
- Update CloudFormation specs to 8.0.0 (pull #[1187](https://github.com/aws-cloudformation/cfn-python-lint/pull/1187))
- Update Pricing and SSM data to 2019.11.08 (pull #[1187](https://github.com/aws-cloudformation/cfn-python-lint/pull/1187))
###### Fixes
- Update rule [W2501](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2501) to include more properties to validate security of a parameter (pull #[1181](https://github.com/aws-cloudformation/cfn-python-lint/pull/1181))
- Fix YAML parsing to not fail on merging and aliases (pull #[1182](https://github.com/aws-cloudformation/cfn-python-lint/pull/1182))
- Fix an issue with SAM when CORS is present in pre-transformed template (pull #[1185](https://github.com/aws-cloudformation/cfn-python-lint/pull/1185))
- Update rule [W7001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W7001) to look at pre-transformed FindInMaps (pull #[1186](https://github.com/aws-cloudformation/cfn-python-lint/pull/1186))

### 0.24.8
###### CloudFormation Specifications
- Update CloudFormation specs to 7.2.0 (pull #[1177](https://github.com/aws-cloudformation/cfn-python-lint/pull/1177))
- Update Pricing and SSM data to 2019.11.01 (pull #[1177](https://github.com/aws-cloudformation/cfn-python-lint/pull/1177))

### 0.24.7
###### CloudFormation Specifications
- Patch in Tags for SNS Topics (pull #[1174](https://github.com/aws-cloudformation/cfn-python-lint/pull/1174))
- Update Pricing and SSM data to 2019.10.31 (pull #[1175](https://github.com/aws-cloudformation/cfn-python-lint/pull/1175))
###### Fixes
- Consolidate PSEUDOPARAMS into cfnlint.helpers (pull #[1172](https://github.com/aws-cloudformation/cfn-python-lint/pull/1172))

### 0.24.6
###### Features
- Update SAM Translator to 1.15.1 (pull #[1166](https://github.com/aws-cloudformation/cfn-python-lint/pull/1166))

### 0.24.5
###### CloudFormation Specifications
- Update CloudFormation specs to 7.1.0 (pull #[1163](https://github.com/aws-cloudformation/cfn-python-lint/pull/1163))
- Update Pricing and SSM data to 2019.10.21 (pull #[1163](https://github.com/aws-cloudformation/cfn-python-lint/pull/1163))
###### Fixes
- Update rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2532) to support parameters inside a map type (pull #[1164](https://github.com/aws-cloudformation/cfn-python-lint/pull/1164))
- Update rule [E2510](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2510) to allow SSM parameter types for CIDR blocks (pull #[1162](https://github.com/aws-cloudformation/cfn-python-lint/pull/1162))

### 0.24.4
###### CloudFormation Specifications
- Update CloudFormation specs to 6.3.0 (pull #[1155](https://github.com/aws-cloudformation/cfn-python-lint/pull/1155))
- Update Pricing and SSM data to 2019.10.05 (pull #[1155](https://github.com/aws-cloudformation/cfn-python-lint/pull/1155))
- Update Update CloudWatch alarm comparison operators (pull #[1154](https://github.com/aws-cloudformation/cfn-python-lint/pull/1154))
###### Fixes
- Update rule [E1022](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1022) to allow lists in custom resources (pull #[1151](https://github.com/aws-cloudformation/cfn-python-lint/pull/1151))

### 0.24.3
###### Features
- Add link to updated IntelliJ integration (pull #[1138](https://github.com/aws-cloudformation/cfn-python-lint/pull/1138))
- Add link to emacs integration (pull #[1118](https://github.com/aws-cloudformation/cfn-python-lint/pull/1118))
###### CloudFormation Specifications
- Update CloudFormation specs to 6.2.0 (pull #[1145](https://github.com/aws-cloudformation/cfn-python-lint/pull/1145))
- Update Pricing and SSM data to 2019.09.28 (pull #[1145](https://github.com/aws-cloudformation/cfn-python-lint/pull/1145))
- Remove manual patches that are no longer needed (pull #[1146](https://github.com/aws-cloudformation/cfn-python-lint/pull/1146))
- Update CloudFormation spec links for a few regions that using old links (pull #[1148](https://github.com/aws-cloudformation/cfn-python-lint/pull/1148))
###### Fixes
- Update rule [E3001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3001) to allow `DeletionPolicy` and `UpdateReplacePolicy` to be allowed on all resources (pull #[1139](https://github.com/aws-cloudformation/cfn-python-lint/pull/1139))
- Update rule [W2030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2030) to not check Paramter default values when using a Resource Condition (pull #[1140](https://github.com/aws-cloudformation/cfn-python-lint/pull/1140))
- Update rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2532) to allow new types in Step Functions (pull #[1143](https://github.com/aws-cloudformation/cfn-python-lint/pull/1143))

### 0.24.2
###### CloudFormation Specifications
- Add missing values for LifecyclePolicy API (pull #[1128](https://github.com/aws-cloudformation/cfn-python-lint/pull/1128))
- Update CloudFormation specs to 6.1.0 (pull #[1134](https://github.com/aws-cloudformation/cfn-python-lint/pull/1134))
- Update Pricing and SSM data to 2019.09.20 (pull #[1134](https://github.com/aws-cloudformation/cfn-python-lint/pull/1134))
###### Fixes
- Update [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029)
to include cognito-identity keys to list of excluded resourse when checking if Fn sub is needed (pull #[1136](https://github.com/aws-cloudformation/cfn-python-lint/pull/1136))

### 0.24.1
###### CloudFormation Specifications
- Update CloudFormation specs to 6.0.0 (pull #[1126](https://github.com/aws-cloudformation/cfn-python-lint/pull/1126))
###### Fixes
- Update AWS::SQS::Queue.ReceiveMessageWaitTimeSeconds to allow 0 value (pull #[1123](https://github.com/aws-cloudformation/cfn-python-lint/pull/1123))
- AWS::EC2::SecurityGroup.Description StringMin and StringMax should be integers (pull #[1125](https://github.com/aws-cloudformation/cfn-python-lint/pull/1125))
- AWS::ApiGateway::GatewayResponse.ResponseType typo (pull #[1126](https://github.com/aws-cloudformation/cfn-python-lint/pull/1126))

### 0.24.0
###### Features
- Move rule classes from cfnlint into cfnlint.rules (pull #[1098](https://github.com/aws-cloudformation/cfn-python-lint/pull/1098))
###### CloudFormation Specifications
- Update IAM policies as of 2019.09.03 (pull #[1120](https://github.com/aws-cloudformation/cfn-python-lint/pull/1120))
- Update CloudFormation specs from pricing and SSM data as of 2019.09.03 (pull #[1120](https://github.com/aws-cloudformation/cfn-python-lint/pull/1120))
- Add a lot of min/max values to the specs (pull #[1110](https://github.com/aws-cloudformation/cfn-python-lint/pull/1110) and pull #[1116](https://github.com/aws-cloudformation/cfn-python-lint/pull/1116))
###### Fixes
- Add me-south-1 to supported regions (pull #[1113](https://github.com/aws-cloudformation/cfn-python-lint/pull/1113))
- Fix an issue where the spec file was referencing instance profiles for Glue Resources (pull #[1114](https://github.com/aws-cloudformation/cfn-python-lint/pull/1114))

### 0.23.5
###### CloudFormation Specifications
- Switch AWS Batch SpotIamFleetRole to Role Arn (pull #[1111](https://github.com/aws-cloudformation/cfn-python-lint/pull/1111))

### 0.23.4
###### CloudFormation Specifications
- Update CloudFormatin specs to 5.3.0 (pull #[1108](https://github.com/aws-cloudformation/cfn-python-lint/pull/1108))
- Update CloudFormatin specs from pricing and SSM data on 2019.08.22 (pull #[1104](https://github.com/aws-cloudformation/cfn-python-lint/pull/1104))
- Add 416 to the CloudFront Error Codes (pull #[1100](https://github.com/aws-cloudformation/cfn-python-lint/pull/1100))
- Move a lot of types into separate files (pull #[1074](https://github.com/aws-cloudformation/cfn-python-lint/pull/1074))
###### Fixes
- Don't fail getting directives when resources are malformed (pull #[1099](https://github.com/aws-cloudformation/cfn-python-lint/pull/1099))

### 0.23.3
###### CloudFormation Specifications
- Add me-east-1 CloudFormation spec (pull #[1095](https://github.com/aws-cloudformation/cfn-python-lint/pull/1095))
- Update CloudFormatin specs to 5.1.0 (pull #[1093](https://github.com/aws-cloudformation/cfn-python-lint/pull/1093))
- Update spec patching from SSM and pricing to 2019.08.13 (pull #[1093](https://github.com/aws-cloudformation/cfn-python-lint/pull/1093))
###### Fixes
- Remove requests and switch to urllib(2) (pull #[1093](https://github.com/aws-cloudformation/cfn-python-lint/pull/1093))
- Fix rule [E3003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3003) to not fail when running into a basic property in the CloudFormation spec (pull #[1096](https://github.com/aws-cloudformation/cfn-python-lint/pull/1096))

### 0.23.2
###### CloudFormation Specifications
- Update CloudFormation spec to version 5.0.0 (pull #[1087](https://github.com/aws-cloudformation/cfn-python-lint/pull/1087))
- Remove Ref check from IAM Policy Name (pull #[1087](https://github.com/aws-cloudformation/cfn-python-lint/pull/1087))

### 0.23.1
###### Fixes
- Fix an issue where anything piped into cfn-lint would result in ignoring the templates parameter (pull #[1081](https://github.com/aws-cloudformation/cfn-python-lint/pull/1081))

### 0.23.0
###### Features
- Add support for regions cn-north-1 and cn-northwest-1 (pull #[1051](https://github.com/aws-cloudformation/cfn-python-lint/pull/1051))
- Add rule [E3027](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3027) to validate the format of AWS Event ScheduleExpression (pull #[1028](https://github.com/aws-cloudformation/cfn-python-lint/pull/1028))
- Update SAM Translator support to release 1.13.0 (pull #[1054](https://github.com/aws-cloudformation/cfn-python-lint/pull/1054))
- Extend rule [W2509](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2509) and [E2004](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2004) to check for more types of CIDR properties (pull #[1058](https://github.com/aws-cloudformation/cfn-python-lint/pull/1058))
- Add Availability Zones for me-south-1 region (pull #[1070](https://github.com/aws-cloudformation/cfn-python-lint/pull/1070))
- Update README to document using cfn-lint with github actions (pull #[1072](https://github.com/aws-cloudformation/cfn-python-lint/pull/1072))
###### CloudFormation Specifications
- Restructure some of the patching to make organization easier (pull #[1030](https://github.com/aws-cloudformation/cfn-python-lint/pull/1030))
- Update specs from pricing and SSM data as of 2019.08.01 (pull #[1078](https://github.com/aws-cloudformation/cfn-python-lint/pull/1078))
- Remove IAM::User Tags and move IAM::Role Tag support to regions where it works (pull #[1077](https://github.com/aws-cloudformation/cfn-python-lint/pull/1077))
###### Fixes
- Apply SAM Transform when template Transforms are a list (pull #[1056](https://github.com/aws-cloudformation/cfn-python-lint/pull/1056))
- Fix an issue where templates provided via stdin where not getting linted (pull #[1060](https://github.com/aws-cloudformation/cfn-python-lint/pull/1060))
- Fix rule [E2015](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2015) to convert integers to string when testing min/max length (pull #[1063](https://github.com/aws-cloudformation/cfn-python-lint/pull/1063))
- Update excludes for [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to include TopicRulePayload (pull #[1066](https://github.com/aws-cloudformation/cfn-python-lint/pull/1066))

### 0.22.4
###### Features
- Add ALL_REGIONS option for -r flag (pull #[1026](https://github.com/aws-cloudformation/cfn-python-lint/pull/1026))
###### CloudFormation Specifications
- Add SSM parameter type values to [E2510](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2510) (pull #[1036](https://github.com/aws-cloudformation/cfn-python-lint/pull/1036))
- Add allowed values for AWS::IAM Resources (pull #[1027](https://github.com/aws-cloudformation/cfn-python-lint/pull/1027))
- Update CloudFormation spec to version 4.3.0 (pull #[1048](https://github.com/aws-cloudformation/cfn-python-lint/pull/1048))
- Update specs from pricing and SSM data as of 2019.07.25
###### Fixes
- Removed duplicate from list of Availability Zones (pull #[1035](https://github.com/aws-cloudformation/cfn-python-lint/pull/1035))
- Fixed example regex in CIDR rule (pull #[1029](https://github.com/aws-cloudformation/cfn-python-lint/pull/1029))
- Support for Serverless transform when it's in a list of one Transforms (pull #[1042](https://github.com/aws-cloudformation/cfn-python-lint/pull/1042))
- Don't fail rules that include a Transform (pull #[1041](https://github.com/aws-cloudformation/cfn-python-lint/pull/1041))
- Don't fail when AWS::NoValue used when we're looking for a list (pull #[1039](https://github.com/aws-cloudformation/cfn-python-lint/pull/1039))
- Fixed [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) to support AWS::NoValue (pull #[1038](https://github.com/aws-cloudformation/cfn-python-lint/pull/1038))
- Added FindInMap as valid function within Fn::Cidr (pull #[1034](https://github.com/aws-cloudformation/cfn-python-lint/pull/1034))

### 0.22.3
###### CloudFormation Specifications
- Patch in `AWS::SageMaker::CodeRepository` to the CloudFormation spec (issue #[1005](https://github.com/aws-cloudformation/cfn-python-lint/issues/1005))
- Patch in Tags into IAM Roles and Users (issue #[1015](https://github.com/aws-cloudformation/cfn-python-lint/issues/1015))
- Update CloudFormation spec to version 4.2.0 (pull #[1023](https://github.com/aws-cloudformation/cfn-python-lint/pull/1023))
- Update specs from pricing and SSM data as of 2019.07.13
###### Fixes
- Add more Availability Zones (pull #[1021](https://github.com/aws-cloudformation/cfn-python-lint/pull/1021))

### 0.22.2
###### CloudFormation Specifications
- Patch in `AWS::Cognito::UserPool` resource information for `ap-south-1` and `ap-southeast-1` (issue #[1002](https://github.com/aws-cloudformation/cfn-python-lint/issues/1002))
- Remove manual patching for `AWS::Backup::BackupPlan` resource information and fix a few spec issues (pull #[1006](https://github.com/aws-cloudformation/cfn-python-lint/pull/1006))
- Fix a few spec regex patterns that were missing escapes of `-` inside `[]` (issue #[997](https://github.com/aws-cloudformation/cfn-python-lint/issues/997))
- Update pricing script to include bare metal instance types (issue #[998](https://github.com/aws-cloudformation/cfn-python-lint/issues/998))
- Create a regex pattern for IAM Policy Names (issue #[996](https://github.com/aws-cloudformation/cfn-python-lint/issues/996))
- Patch CloudFormation specs from SSM data on 2019.07.10
###### Fixes
- Fix a warning when loading resources using a `\` in the prefix (issue #[1009](https://github.com/aws-cloudformation/cfn-python-lint/issues/1009))

### 0.22.1
###### CloudFormation Specifications
- Add `INSTANCE` to `DLMPolicyResourceType` allowed values (pull #[995](https://github.com/aws-cloudformation/cfn-python-lint/pull/995))
- Update specs from weird 4.1.0 release (pull #[994](https://github.com/aws-cloudformation/cfn-python-lint/pull/994))
- Update instance types and patches from SSM to date 2019.07.04 (pull #[1001](https://github.com/aws-cloudformation/cfn-python-lint/pull/1001))
- Add all the allowed values of the AWS::EFS Resources (pull #[990](https://github.com/aws-cloudformation/cfn-python-lint/pull/990))
###### Fixes
- Fix an issue where rules were being loaded twice (pull #[980](https://github.com/aws-cloudformation/cfn-python-lint/pull/980))
- Fix an issue with rule [E1010](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1010) to split GetAtt strings into two values (issue #[986](https://github.com/aws-cloudformation/cfn-python-lint/issues/986))
- Update rules [E8004](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E8004), [E8003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E8003), [E8005](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E8005), and [E8006](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E8006) to not flag functions used in Service Catalog rules section (issue #[979](https://github.com/aws-cloudformation/cfn-python-lint/issues/979))
- Patched testing for Lambda Runtime EOL and end dates to test as if a specific date (pull #[999](https://github.com/aws-cloudformation/cfn-python-lint/pull/999))

### 0.22.0
###### CloudFormation Specifications
- Update specs to 4.1.0
- Added LaunchTemplateId/LaunchTemplateName of the AutoScalingGroup to the OnlyOne
- Patch resource AWS::EC2::LaunchTemplate property TagSpecifications
- Add AWS::EC2::LaunchTemplate property to LaunchTemplateName min/max/pattern
- Add AWS::EC2::LaunchTemplate allowed values for the ResourceType property
- Remove/Add services to region tables based on SSM endpoints
###### Fixes
- Update JsonSchem to 3.0 to support the new version 1.12.0 of aws-sam-translator
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2503) to allow NLBs to use UDP
- Update rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020) to include many special characters for DNS records
- Sort filenames when getting a bunch of templates from a folder
- Fix typos in the integration documentation

### 0.21.6
###### Features
- Remove rule [W2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2507) and use rule [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3008) instead
- Remove rule [W2508](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2508) and use rule [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3008) instead
###### CloudFormation Specifications
- Update specs to 3.4.0
- Add all the allowed values of the AWS::ECS Resources.
- Update CloudFormation Spec to include the Backup Resources
- Add Cognito RefreshTokenValidity number limits
###### Fixes
- Fix copy-paste typo in Not function check
- Don't fail when conditions are used with parameters and allowed values
- More IAM Resource exceptions for Sub Needed check

### 0.21.5
###### Features
- Update rule [E3001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3001) to validate that a Resource Condition is a string
###### CloudFormation Specifications
- Add all the allowed values of the AWS::EC2 CapacityReservation Resources
- Update Launch Configuration IamInstanceProfile to support Ref or GetAtt to an IAM Instance Profile
###### Fixes
- Fix `lessthan` type in a bunch of rules
- Update rule [E2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2507) to handle intrinsics when testing the values for `Effect`
- Fix rule [E8002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E8002) to not error when the Condition isn't a string

### 0.21.4
###### Features
- Include more resource types in [W3037](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W30307)
###### CloudFormation Specifications
- Add Resource Type `AWS::CDK::Metadata`
###### Fixes
- Uncap requests dependency in setup.py
- Check Join functions have lists in the correct sections
- Pass a parameter value for AutoPublishAlias when doing a Transform
- Show usage examples when displaying the help

### 0.21.3
###### Fixes
- Support dumping strings for datetime objects when doing a Transform

### 0.21.2
###### CloudFormation Specifications
- Update CloudFormation specs to 3.3.0
- Update instance types from pricing API as of 2019.05.23

### 0.21.1
###### Features
- Add `Info` logging capability and set the default logging to `NotSet`
###### Fixes
- Only do rule logging (start/stop/time) when the rule is going to be called
- Update rule [E1019](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1019) to allow `Fn::Transform` inside a `Fn::Sub`
- Update rule [W2001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2001) to not break when `Fn::Transform` inside a `Fn::Sub`
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2503) to allow conditions to be used and to not default to `network` load balancer when an object is used for the Load Balancer type

### 0.21.0
###### Features
- New rule [E3038](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3038) to check if a Serverless resource includes the appropriate Transform
- New rule [E2531](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2531) to validate a Lambda's runtime against the deprecated dates
- New rule [W2531](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2531) to validate a Lambda's runtime against the EOL dates
- Update rule [E2541](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2541) to include updates to Code Pipeline capabilities
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2503) to include checking of values for load balancer attributes
###### CloudFormation Specifications
- Update CloudFormation specs to 3.2.0
- Update instance types from pricing API as of 2019.05.20
###### Fixes
- Include setuptools in setup.py requires

### 0.20.3
###### CloudFormation Specifications
- Update instance types from pricing API as of 2019.05.16
###### Fixes
- Update [E7001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E7001) to allow float/doubles for mapping values
- Update [W1020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W1020) to check pre-transformed Fn::Sub(s) to determine if a Sub is needed
- Pin requests to be below or equal to 2.21.0 to prevent issues with botocore

### 0.20.2
###### Features
- Add support for List<String> Parameter types
###### CloudFormation Specifications
- Add allowed values for AWS::EC2 EIP, FlowLog, CustomerGateway, DHCPOptions, EC2Fleet
- Create new property type for Security Group IDs or Names
- Add new Lambda runtime environment for NodeJs 10.x
- Move AWS::ServiceDiscovery::Service Health checks from Only One to Exclusive
- Update Glue Crawler Role to take an ARN or a name
- Remove PrimitiveType from MaintenanceWindowTarget Targets
- Add Min/Max values for Load Balancer Ports to be between 1-65535
###### Fixes
- Include License file in the pypi package to help with downstream projects
- Filter out dynamic references from rule [E3031](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3031) and [E3030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3030)
- Convert Python linting and Code Coverage from Python 3.6 to 3.7

### 0.20.1
###### Fixes
- Update rule [E8003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E8003) to support more functions inside a Fn::Equals

### 0.20.0
###### Features
- Allow a rule's exception to be defined in a [resource's metadata](https://github.com/aws-cloudformation/cfn-python-lint/#resource-based-metadata)
- Add rule [configuration capabilities](https://github.com/aws-cloudformation/cfn-python-lint/#configure-rules)
- Update rule [E3012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3012) to allow for non strict property checking
- Add rule [E8003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E8003) to test Fn::Equals structure and syntax
- Add rule [E8004](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E8004) to test Fn::And structure and syntax
- Add rule [E8005](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E8005) to test Fn::Not structure and syntax
- Add rule [E8006](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E8006) to test Fn::Or structure and syntax
- Include Path to error in the JSON output
- Update documentation to describe how to install cfn-lint from brew
###### CloudFormation Specifications
- Update CloudFormation specs to version 3.0.0
- Add new region ap-east-1
- Add list min/max and string min/max for CloudWatch Alarm Actions
- Add allowed values for EC2::LaunchTemplate
- Add allowed values for EC2::Host
- Update allowed values for Amazon MQ to include 5.15.9
- Add AWS::Greengrass::ResourceDefinition to GreenGrass supported regions
- Add AWS::EC2::VPCEndpointService to all regions
- Update AWS::ECS::TaskDefinition ExecutionRoleArn to be a IAM Role ARN
- Patch spec files for SSM MaintenanceWindow to look for Target and not Targets
- Update ManagedPolicyArns list size to be 20 which is the hard limit.  10 is the soft limit.
###### Fixes
- Fix rule [E3033](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3033) to check the string size when the string is inside a list
- Fix an issue in which AWS::NotificationARNs was not a list
- Add AWS::EC2::Volume to rule [W3010](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W3010)
- Fix an issue with [W2001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2001) where SAM translate would remove the Ref to a parameter causing this error to falsely trigger
- Fix rule [W3010](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W3010) to not error when the availability zone is 'all'

### 0.19.1
###### Fixes
- Fix core Condition processing to support direct Condition in another Condition
- Fix the W2030 to check numbers against string allowed values

### 0.19.0
###### Features
- Add NS and PTR Route53 record checking to rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020)
- New rule [E3050](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3050) to check if a Ref to IAM Role has a Role path of '/'
- New rule [E3037](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3037) to look for duplicates in a list that doesn't support duplicates
- New rule [I3037](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3037) to look for duplicates in a list when duplicates are allowed
###### CloudFormation Specifications
- Add Min/Max values to AWS::ElasticLoadBalancingV2::TargetGroup HealthCheckTimeoutSeconds
- Add Max JSON size to AWS::IAM::ManagedPolicy PolicyDocument
- Add allowed values for AWS::EC2 SpotFleet, TransitGateway, NetworkAcl
NetworkInterface, PlacementGroup, and Volume
- Add Min/max values to AWS::Budgets::Budget.Notification Threshold
- Update RDS Instance types by database engine and license definitions using the pricing API
- Update AWS::CodeBuild::Project ServiceRole to support Role Name or ARN
- Update AWS::ECS::Service Role to support Role Name or ARN
###### Fixes
- Update [E3025](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3025) to support the new structure of data in the RDS instance type json
- Update [E2540](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2540) to remove all nested conditions from the object
- Update [E3030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2540) to not do strict type checking
- Update [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020) to support conditions nested in the record sets
- Update [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3008) to better handle CloudFormation sub stacks with different GetAtt formats

### 0.18.1
###### CloudFormation Specifications
- Update CloudFormation Specs to 2.30.0
- Fix IAM Regex Path to support more character types
- Update AWS::Batch::ComputeEnvironment.ComputeResources InstanceRole to reference an
InstanceProfile or GetAtt the InstanceProfile Arn
- Allow VPC IDs to Ref a Parameter of type String
###### Fixes
- Fix [E3502](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3502) to check the size of the property instead of the parent object

### 0.18.0
###### Features
- New rule [E3032](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3032) to check the size of lists
- New rule [E3502](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3502) to check JSON Object Size using definitions in the spec file
- New rule [E3033](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3033) to test the minimum and maximum length of a string
- New rule [E3034](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3034) to validate the min and max of a number
- Remove Ebs Iops check from [E2504](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2504) and use rule [E3034](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3034) instead
- Remove rule [E2509](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2509) and use rule [E3033](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3033) instead
- Remove rule [E2508](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2508) as it replaced by [E3032](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3032) and [E3502](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3502)
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2503) to check that there are at least two 2 Subnets or SubnetMappings for ALBs
- SAM requirement upped to minimal version of 1.10.0
###### CloudFormation Specifications
- Extend specs to include:
  - `ListMin` and `ListMax` for the minimum and maximum size of a list
  - `JsonMax` to check the max size of a JSON Object
  - `StringMin` and `StringMax` to check the minimum and maximum length of a String
  - `NumberMin` and `NumberMax` to check the minimum and maximum value of a Number, Float, Long
- Update State and ExecutionRoleArn to be required on AWS::DLM::LifecyclePolicy
- Add AllowedValues for PerformanceInsightsRetentionPeriod for AWS::RDS::Instance
- Add AllowedValues for the AWS::GuardDuty Resources
- Add AllowedValues for AWS::EC2 VPC and VPN Resources
- Switch IAM Instance Profiles for certain resources to the type that only takes the name
- Add regex pattern for IAM Instance Profile when a name (not Arn) is used
- Add regex pattern for IAM Paths
- Add Regex pattern for IAM Role Arn
- Update OnlyOne spec to require require at least one of Subnets or SubnetMappings with ELB v2
###### Fixes
- Fix serverless transform to use DefinitionBody when Auth is in the API definition
- Fix rule [W2030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2030) to not error when checking SSM or List Parameters

### 0.17.1
###### Features
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2503) to make sure NLBs don't have a Security Group configured
###### CloudFormation Specifications
- Add all the allowed values of the `AWS::Glue` Resources
- Update OnlyOne check for `AWS::CloudWatch::Alarm` to only `MetricName` or `Metrics`
- Update Exclusive check for `AWS::CloudWatch::Alarm` for properties mixed with `Metrics` and `Statistic`
- Update CloudFormation specs to 2.29.0
- Fix type with MariaDB in the AllowedValues
- Update pricing information for data available on 2018.3.29
###### Fixes
- Fix rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to not look for a sub is needed when looking for iot strings in policies
- Fix rule [E2541](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2541) to allow for ActionId Versions of length 1-9 and meets regex `[0-9A-Za-z_-]+`
- Fix rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2532) to allow for `Parameters` inside a `Pass` action
- Fix an issue when getting the location of an error in which numbers are causing an attribute error

### 0.17.0
###### Features
- Add new rule [E3026](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3026) to validate Redis cluster settings including AutomaticFailoverEnabled and NumCacheClusters.  Status: Released
- Add new rule [W3037](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W3037) to validate IAM resource policies.  Status: Experimental
- Add new parameter `-e/--include-experimental` to allow for new rules in that aren't ready to be fully released
###### CloudFormation Specifications
- Update Spec files to 2.28.0
- Add all the allowed values of the AWS::Redshift::* Resources
- Add all the allowed values of the AWS::Neptune::* Resources
- Patch spec to make AWS::CloudFront::Distribution.LambdaFunctionAssociation.LambdaFunctionARN required
- Patch spec to make AWS::DynamoDB::Table AttributeDefinitions required
###### Fixes
- Remove extra blank lines when there is no errors in the output
- Add exception to rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to have exceptions for EMR CloudWatchAlarmDefinition
- Update rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to allow for literals in a Sub
- Remove sub checks from rule [E3031](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3031) as it won't match in all cases of an allowed pattern regex check
- Correct typos for errors in rule [W1001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W1001)
- Switch from parsing a template as Yaml to Json when finding an escape character
- Fix an issue with SAM related to transforming templates with Serverless Application and Lambda Layers
- Fix an issue with rule [E2541](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2541) when non strings were used for Stage Names

### 0.16.0
###### Features
- Add rule [E3031](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3031) to look for regex patterns based on the patched spec file
- Remove regex checks from rule [E2509](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2509)
- Add parameter `ignore-templates` to allow the ignoring of templates when doing bulk linting
###### CloudFormation Specifications
- Update Spec files to 2.26.0
- Add all the allowed values of the AWS::DirectoryService::* Resources
- Add all the allowed values of the AWS::DynamoDB::* Resources
- Added AWS::Route53Resolver resources to the Spec Patches of ap-southeast-2
- Patch the spec file with regex patterns
- Add all the allowed values of the AWS::DocDb::* Resources
###### Fixes
- Update rule [E2504](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2504) to have '20000' as the max value
- Update rule [E1016](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1016) to not allow ImportValue inside of Conditions
- Update rule [E2508](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2508) to check conditions when providing limit checks on managed policies
- Convert unicode to strings when in Py 3.4/3.5 and updating specs
- Convert from `awslabs` to `aws-cloudformation` organization
- Remove suppression of logging that was removed from samtranslator >1.7.0 and incompatibility with
samtranslator 1.10.0

### 0.15.0
###### Features
- Add scaffolding for arbitrary Match attributes, adding attributes for Type checks
- Add rule [E3024](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3024) to validate that ProvisionedThroughput is not specified with BillingMode PAY_PER_REQUEST
###### CloudFormation Specifications
- Update Spec files to 2.24.0
- Update OnlyOne spec to have BlockDeviceMapping to include NoDevice with Ebs and VirtualName
- Add all the allowed values of the AWS::CloudFront::* Resources
- Add all the allowed values of the AWS::DAX::* Resources
###### Fixes
- Update config parsing to use the builtin Yaml decoder
- Add condition support for Inclusive [E2521](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2521), Exclusive [E2520](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2520), and AtLeastOne [E2522](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2522) rules
- Update rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to better check Resource strings inside IAM Policies
- Improve the line/column information of a Match with array support

### 0.14.1
###### CloudFormation Specifications
- Update CloudFormation Specs to version 2.23.0
- Add allowed values for AWS::Config::* resources
- Add allowed values for AWS::ServiceDiscovery::* resources
- Fix allowed values for Apache MQ
###### Fixes
- Update rule [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3008) to not error when using a list from a custom resource
- Support simple types in the CloudFormation spec
- Add tests for the formatters

### 0.14.0
###### Features
- Add rule [E3035](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3035) to check the values of DeletionPolicy
- Add rule [E3036](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3036) to check the values of UpdateReplacePolicy
- Add rule [E2014](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2014) to check that there are no REFs in the Parameter section
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2503) to support TLS on NLBs
###### CloudFormation Specifications
- Update CloudFormation spec to version 2.22.0
- Add allowed values for AWS::Cognito::* resources
###### Fixes
- Update rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) to allow GetAtts to Custom Resources under a Condition

### 0.13.2
###### Features
- Introducing the cfn-lint logo!
- Update SAM dependency version
###### Fixes
- Fix CloudWatchAlarmComparisonOperator allowed values.
- Fix typo resoruce_type_spec in several files
- Better support for nested And, Or, and Not when processing Conditions

### 0.13.1
###### CloudFormation Specifications
- Add allowed values for AWS::CloudTrail::Trail resources
- Patch spec to have AWS::CodePipeline::CustomActionType Version included
###### Fixes
- Fix conditions logic to use AllowedValues when REFing a Parameter that has AllowedValues specified

### 0.13.0
###### Features
- New rule [W1011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W1011) to check if a FindInMap is using the correct map name and keys
- New rule [W1001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W1001) to check if a Ref/GetAtt to a resource that exists when Conditions are used
- Removed logic in [E1011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1011) and moved it to [W1011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W1011) for validating keys
- Add property relationships for AWS::ApplicationAutoScaling::ScalingPolicy into Inclusive, Exclusive, and AtLeastOne
- Update rule [E2505](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2505) to check the netmask bit
- Include the ability to update the CloudFormation Specs using the Pricing API
###### CloudFormation Specifications
- Update to version 2.21.0
- Add allowed values for AWS::Budgets::Budget
- Add allowed values for AWS::CertificateManager resources
- Add allowed values for AWS::CodePipeline resources
- Add allowed values for AWS::CodeCommit resources
- Add allowed values for EC2 InstanceTypes from pricing API
- Add allowed values for RedShift InstanceTypes from pricing API
- Add allowed values for MQ InstanceTypes from pricing API
- Add allowed values for RDS InstanceTypes from pricing API
###### Fixes
- Fixed README indentation issue with .pre-commit-config.yaml
- Fixed rule [E2541](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2541) to allow for multiple inputs/outputs in a CodeBuild task
- Fixed rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020) to allow for a period or no period at the end of a ACM registration record
- Update rule [E3001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3001) to support UpdateReplacePolicy
- Fix a cli issue where `--template` wouldn't be used when a .cfnlintrc was in the same folder
- Update rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) and [E1024](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W3002) to support packaging of AWS::Lambda::LayerVersion content

### 0.12.1
###### CloudFormation Specifications
- Add AWS::WorkSpaces::Workspace.WorkspaceProperties ComputeTypeName, RunningMode allowed values
- Fix AWS::CloudWatch::Alarm to point Metrics at AWS::CloudWatch::Alarm.MetricDataQuery
###### Fixes
- Update rule [E1024](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1024) to support Fn::Sub inside Fn::Cidr

### 0.12.0
###### Features
- Update rule [E1019](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1019) to not allow for lists directly when doing a Ref or GetAtt to a list
- Move parameter checks from rule [E3030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3030) to a new rule [W2030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2030)
###### CloudFormation Specifications
- Updated to version 2.19.0
- Add S3 Bucket Allowed Values
- Add Route53 Allowed Values
- Add CodeDeploy Allowed Values
- Add AWS::SecretsManager::SecretTargetAttachment TargetType Allowed Values
- Add AWS::SES::ReceiptRule.Rule TlsPolicy Allowed Values
- Add AWS::AutoScaling::AutoScalingGroup, AWS::Route53::RecordSetGroup, and AWS::AutoScaling::AutoScalingGroup to OnlyOne
###### Fixes
- Improve [W7001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W7001) error message

### 0.11.1
###### CloudFormation Specifications
- Support Ref to IAM::Role or IAM::InstanceProfile with values looking for an ARN
- AWS::Batch::ComputeEnvironment InstanceRole is an InstanceProfile not Role
###### Fixes
- Add debug options to print a stack trace for rule E0002
- Update rule [E2015](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2015) to include a try/catch around AllowedPattern testing to catch errors caused by non Python supported regex

### 0.11.0
###### Features
- Add rule [E3030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3030) to use the newly patched spec to check resource properties values.  Update the following rules replaced by [E3030](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3030).
  - Delete rule [W2512](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2512)
  - Delete rule [E2531](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2531)
  - Move allowed values check in rule [E2505](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2505)
- Add rule [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3008) to use the newly patched spec to check a resource properties Ref and GetAtt.  Update the following rules replaced by [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3008).
  - Delete rule [E2502](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2502)
  - Delete rule [W2505](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2505)
- Improve rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020) to check MX records
###### CloudFormation Specifications
- Update CloudFormation specs to 2.18.1
- Append the CloudFormation spec to include:
  - AllowedValues for resource properties
  - Allowed Ref/GetAtts for resource properties
- Add specs for regions `eu-north-1`, `us-gov-east-1`, `us-gov-west-1`
- Add `AWS::StepFunctions::StateMachine` in all supported regions
- Add `AWS::CloudWatch::Alarm.Metric`, `AWS::CloudWatch::Alarm.MetricDataQuery` and `AWS::CloudWatch::Alarm.MetricStat` in all supported regions
- Add `AWS::Lambda::LayerVersion`, `AWS::Lambda::LayerVersion.Content`, and `AWS::Lambda::LayerVersionPermission` in all supported regions
###### Fixes
- Fix description on rule [W2501](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2501) to be more informative
- Update rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2532) to allow `Parameters` in a `Task` in a Step Function
- Fix rule [E1010](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1010) to allow Refs in the GetAtt attribute section
- Add `AWS::CloudFormation::Init` as an exception for rule E1029
- Add `Informational` error messages to JSON outputs
- Fix file searching `**/*` to recursively search in Python 3.5 and greater
- Update CopyRight from 2018 to 2019

### 0.10.2
###### Features
- Code coverage testing integrated into the CI process
- Update CloudFormation specs to 2.18.0
###### Fixes
- Fix rule [E2505](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2505) to allow for SSM parameters when checking Cidr and Tenancy parameters
- Fix rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to not error on API Gateway stageVariables

### 0.10.1
###### Features
- Support stdin for reading and testing templates
###### Fixes
- Remove dependency on regex package as it requires gcc
- Remove rule [E3507](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3507) because it depends on regex package

### 0.10.0
###### Features
- Update specs to version 2.16.0
###### Fixes
- Require pathlib2 in Python versions earlier than 3.4.0
- Update aws-sam-translator to v1.8.0
- Update requests dependency to be at least version 2.15.0
- Add Python 3.7 support for Lambda
- Provide valid Python runtimes in rule [E2531](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2531) error message
- Allow Fn::Sub inside a Fn::Sub for rule [E1019](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1019)
- Add hardcoded list check as invalid in rule [E6003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E6003)
- Fix home expansion with when looking for .cfnlintrc in Python 3.4
- Add testing in Travis for Py34, Py35, Py37
- Prevent spaces after the comma in spec file
- Update allowed Lambda Runtimes to include provided and ruby

### 0.9.2
###### Features
- Update specs to version 2.15.0
###### Fixes
- Fix rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020) to allow multiple text records of up to 255 characters
- Fix rule [E3016](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3016) to handle conditions in Update Policies
- Fix rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2532) to not fail when using a Fn::Sub and a number for a param

### 0.9.1
###### Features
- Add support for eu-west-3 and ap-northeast-3
- Add Resource Type AWS::CloudFormation::Macro to CloudFormation Spec
###### Fixes
- Fix the error message for YAML null being off by 1 line and 1 column number
- Add Custom Error for when trying to access an attribute in the classes that make up the template
- Fix an issue with deepcopy not creating copies with start and end marks
- Fix 4 rules that would fail when trying to create the path of the error and running into an integer
- Fix rule [E2015](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2015) to force parameter default values to be a string when testing against the AllowedPattern regex pattern
- Fix a bug in the config engine in which append rules would have gone to override spec
- Remove exit calls from functions that are used in integrations preventing pre-mature failures
- Fix rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) [E3003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3003) to support functions that may be able to support objects

### 0.9.0
###### Features
- Add rule [E8002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E8002) to validate if resource Conditions or Fn::If conditions are defined
- Improve rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) to validate custom resources when custom specs are addended to the resource spec using override-spec
- Allow for configuration of cfn-lint using configuration files in the project and home folder called .cfnlintrc
- Updated specs to versions release 2.12.0
###### Fixes
- Fix rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) to not fail when looking for lists of objects and using a FindInMap or GetAtt to a custom resource as both could suppliy a list of objects
- Remove rule [E1025](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1025) which was duplicative to the more extensive rule E8002
- Fix rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020) to allow for quotes when checking the length
- Add generic exception handling to SAM transforming functions
- Complete redo how we handle arguments to fix issues created when linting multiple files with cfn-lint configurations in the file
- New CloudFormation spec patch to not require CidrBlock on resource type AWS::EC2::NetworkAclEntry
- New updates to AtLeastOne.json definition to require CidrBlock or Ipv6CidrBlock on resource type AWS::EC2::NetworkAclEntry
- A few documentation improvements

### 0.8.3
###### Features
- Add rule [E3022](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3022) to validate that there is only one SubnetRouteTableAssociation per subnet
###### Fixes
- Fix rule [E2502](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2502) to check Arn and Name for AWS::EC2::LaunchTemplate resources
- Fix rule [E3016](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3016) to remove use of Path which may not be defined in certain scenarios
- Fix base rule Class so that resource_property_types and resource_sub_property_types is initialized from on every new rule and not copied from previous rules that were initialized
- Fix conversions of transformed templates in which keys stayed as str(s) instead of str_node(s)

### 0.8.2
###### Fixes
- Update rule [E2502](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2502) to allow GetAtt against a nested stack or custom resource
- Update rules [E2541](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2541) and [E2540](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2540) to support conditions inside the CodePipeline
- Fix types in rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2532) to now include InputPath and OutputPath
- Update rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to skip missing sub when looking at parameters in IAM policies
- Update rule [E2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2507) to allow for strings in the IAM policy
- Update rule [E2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2507) to allow the policy statement to be an object along with a list

### 0.8.1
###### Features
- Update Specs to the versions released October 19th, 2018
###### Fixes
- Fix rule [E2541](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2541) to not fail on non-string values

### 0.8.0
###### Features
- Created a process to patch the CloudFormation Spec and patched a bunch of issues
- Support pre-commit hooks for linting templates
- Add rule [E3021](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3021) to that 5 or less targets are added to a CloudWatch Event
- Add rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1029) to look for Sub variables that aren't inside a Sub
- Add rule [I3011](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#I3011) to validate that DynamDB Tables have deletion policy specified as the default is to delete the database.
- Add support for `info` errors
###### Fixes
- Update search_deep_keys to look for items in the Global section which is lost in a Transformation
- Clean up failures when loading files that are not yaml or json

### 0.7.4
###### Features
- Support parsing multiple files from the command line
- New rule [E3016](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3016) to validate a resources UpdatePolicy configuration
###### Fixes
- Removes sub parameter check from rule [E1012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1012). The same check is covered by
[E1019](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1019)
- Fix rule [E1010](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1010) when using a string not an array with Fn::Sub
- Fix rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020) ignore intrinsic functions when checking values

### 0.7.3
###### Features
- Update the custom objects for the template to directly allow the calling of getting items and checking items that is condition safe
- Update CloudFormation Specs to 2018-09-21 released specs
###### Fixes
- Fix rule [E2540](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2540) to not fail when the stage names aren't strings
- Fix rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) to not fail when processing Ref AWS::NoValue
- Core functionality updated to fail when extending rules directory doesn't exist
- Fix rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) metadata isn't supported as a resource property
- Fix rule [E2509](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2509) to not error when using a function for description

### 0.7.2
###### Fixes
- Fix rule [W2501](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2501) to support dashes in KMS Key name
- Fix rule [E2543](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2543) to not fail when the type of a step isn't known
- Fix rule [E2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2507) to have an exception for ECR Policies.  Resource isn't required.
- Several Python cleanup items around initializing lists, how version is loaded, and dropping 'discover' in testing

### 0.7.1
###### Fixes
- Fix core decoding so the true error of a template parsing issue is visible to the user

### 0.7.0
###### Features
- New Rule [W1019](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W1019) to make sure any Sub variables are used in the string
- New Rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2532) to start basic validation of state machine syntax
- New Rule [W1020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W1020) to see if Sub is needed and variables are being used
- New Rule [E1028](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1028) validate that first element in a Fn::If array is a string
- New Rule [W3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W3002) to warn when templated templates are used
- Update Rule [E2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2507) to check resource base policies
- Add Rule [W2511](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2511) to warn when using an older version of IAM Policy Version
###### Fixes
- Update Rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) to allow for templated code
- Update Rule [E1024](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1024) to allow Cidr function to use GetAtt
- Fix core functionality to not error if the template is an array or string instead of an object

### 0.6.1
###### Fixes
- Fixes an issue where Template.get_values would return `Ref: AWS::NoValue`. This will no longer be returned as it is considered to be a Null value.

### 0.6.0
###### Features
- Update formatters to be similar from JSON and text outputs and modularize for easier growth later
- Don't raise an error with [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020) when doing ACM DNS validation registration
- Add rule [E7003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E7003) to validate that mapping keys are strings.  
- Add rule [E1027](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1027) to validate that dynamic reference secure strings are to supported properties
- Add rule [E1004](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1004) to validate that the Template Description is only a string
- Add rule [E6005](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E6005) to validate that an Output Description is only a string
- Add rule [E6012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E6012) to validate that an Output Description is less than the maximum length
###### Fixes
- Fix core libraries to handle conditions around resource properties so that the resource and property checks still run
- Fix core libraries to handle the special property type `Tag` so that its checked when a rule is doing a Property Check

### 0.5.2
###### Fixes
- Support additional attributes in spec file for [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3003)
- Check custom resources as if they are 'AWS::CloudFormation::CustomResource' in rule [E3003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3003)
- Fix [W6001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W6001) when an ImportValue is used to another function
- Fix [W2501](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W2501) to support the new dynamic reference feature

### 0.5.1
###### Features
- Update rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020) to support CAA and CNAME record checks
- Update specs to ones released on August 16, 2018

### 0.5.0
###### Features
- Load all instances of CloudFormationLintRule in a file. Class doesn't need to match the filename anymore
- Allow load yaml to accept a string allowing people to use cfn-lint as a module
- Add rule [W6001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W6001) to test outputs that are just using an import value
- Update specs to ones released on August 10, 2018
###### Fixes
- Update [E2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2507) to support conditions and using get_values to test all condition paths
- Update [E2521](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2521), [E2523](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2523) to support conditions and using get_values to test all condition paths
- Rewrite [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2503) to support intrinsic functions and conditions and lower case protocols
- Fix [E1018](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1018) to support Sub inside a Split function
- Fix [E3003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3003) description messages to be more informative
- Fix [E3001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3001) to not require parameters when CreationPolicy is used
- Fix SAM region when no region is available from a local AWS profile or environment variable.

### 0.4.2
###### Features
- Update rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020) to support AAAA record checks
###### Fixes
- Fix many rules that would fail if a sub parameter had a space at the beginning or end
- Fix crashing issues when trying to get resources that aren't properly configured

### 0.4.1
###### Features
- Update CloudFormation Specs to July 20th, 2018
###### Fixes
- Fix an issue with Exclusive resource properties and RDS with Snapshot and Password

### 0.4.0
###### Features
- Update CloudFormation specs to July 16th, 2018
- Support comma lists for regions, append rules, and ignore check parameters
- Added documentation explaining Resource Specification based rules
###### Fixes
- Fix a bunch of typos across many different rules
- Support DeepCopy with Template and custom String classes used for marking up templates
- Fix Rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) to support CommaDelimitedList when looking for List Parameters
- Fix core engine to check that something is a Dict instead of assuming it is

### 0.3.5
###### Features
- Update CloudFormation Specs to July 12th, 2018
- Rule [E7012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E7012) added to check the limits of attributes in a Mapping
- Rule [E2012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2012) added to check maximum size of a parameter value
- Rule [E1003](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1003) added to check the maximum length of the template Description
- Guide created to help new users write new rules
###### Fixes
- Catch KeyError when trying to discover the line and column number of an error
- Update Lambda rules to support dotnet core
- Fix rule [E1017](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1017) so we unpack first element of select as a dict
- Fix rule [E1024](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1024) to support ImportValue and appropriately checking number for the last element

### 0.3.3
###### Features
- Support for Yaml C Parser when available.
- Catch rule processing errors and raise a lint error in their place.
- Add rules for the limit on Parameter, Mapping, Resource and Output names
- Add Rule [W3005](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W3005) to warn for when DependsOn is specified but not needed
- Add Rule [E2509](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2509) to check if Security Group Descriptions are properly configured
- Add `source_url` to rules so rule reference documentation can be provided
###### Fixes
- Fixed issues when Conditions had lists for values
- Fixed issue where underscore was allowed for AlphaNumeric names

### 0.3.2
###### Features
- Try/Catch added to rule processing so code failures in rules won't crash cfn-lint
- Parse YAML files using C parser when available.  Greatly speeds up YAML parsing.
###### Fixes
- Template class updated to handle conditions where lists are in the true/false values
- Fix regex for checking Resource, Output, etc. names to not include underscore

### 0.3.1
###### Features
- Update rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020) to validate A recordsets
###### Fixes
- Require "aws-sam-translator" dependency be at least 1.6.0
- Add support for wildcards in rule [E3013](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3013) - Support conditions in Lists for rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3002) - Include filename when we run into Null and Duplicate values when parsing yaml
- Rule W2510 now allows for AllowedValues instead of just Min/MaxValue for compliance of Lambda MemorySize
- Rule [E2530](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2530) updated to checked AllowedValues for compliance of Lambda MemorySize

### 0.3.0
###### Features
- Serverless Transforms now handled by SAM libraries
- Add Rule [E2508](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2508): Add checks for IAM
  - Managed Policies attached to IAM user, group or role can't be more than 10
  - An IAM user can be a member of no more than 10 groups
  - There can only be 1 role in an instance profile
  - AssumeRolePolicyDocument size is less than <2048 characters
- Add Rule [E1002](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1002): Check overall template size to make sure its below
- Add Rule [E3013](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3013): CloudFront aliases should contain valid domain names
- Add Rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3020): Check if all RecordSets are correctly configured
  - Strings end and start with double quotes
  - Size is less than 256 characters
  - Record Types are within the specification
- Short hand parameter switches and no longer need --template
###### Fixes
- Don't report a Condition not being used if it is used by another Condition

### 0.2.2
###### Fixes
- Fixed issues with Yaml and Json parsing for complex strings in Python 2.7
- Added eu-central-1 Availability Zones to acceptable AZ list
- Added nodejs8.10 to supported Lambda
- Added Version as an attribute for a Custom Resource
- Parseable output is now colon(:) delimited

### 0.2.1
###### Features
- Added AllowedValues for Cidr parameter checking Rule W2509
- Add Rule [E2004](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E2004) to check Allowed values for Cidr parameters are a valid Cidr range
- Disable mapping Name checks [W7001](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#W7001) if dynamic mapping names are used (Ref, FindInMap)
- New Rule [E1026](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1026) to make sure Ref's in 'Conditions' are to parameters and not resources
- Updated CloudFormation specs to June 5th, 2018
###### Fixes
- Fixed an issue with Rule [E1019](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E1019) not giving errors when there was a bad pseudo parameter
- Fixed an issue where conditions with Refs were validated as strings instead of Refs
- Fix crash errors when an empty yaml file is provided
- Updated condition functions to return the full object (Ref isn't translated while looking for AWS::NoValue)
- Support Map Type properties when doing PrimitiveType check [E3012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3012) - Fix an issue when boolean values not being checked when using check_value

### 0.2.0
###### Features
- Standard cfn-lint Errors ([E0000](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E0000)) for null, duplicate, and parse errors
- Add a new check for CloudFormation limits
- Add a new check for Parameter, Resource, Output, and Mapping names
- Update specs to those released on May 25th, 2018
- Strong type checking for property values result in Errors ([E3012](https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/rules.md#E3012))
###### Fixes
- Transform logic updated to not add a Role if one is specified for a serverless function
- Fixed logic around Fn::If when the result is an object
- Fix conditions when checking property value structure

### 0.1.0
###### Features
- Update CloudFormation specs to include recent releases
- Add checks for duplicate resource names
- Add checks for null values in templates
- Add support in Circular Dependency checks to go multiple levels deep
- Add check for unused mappings
- Add check for unused and not found conditions
- Convert Errors to Warnings that don't cause a failure when implementing a template
###### Fixes
- Fix check for cfn-lint configurations in templates
- Fix Sub Functions checks failing on sub stacks or custom resources
- Fix Serverless Transforms not failing when trying to create multiple RestApiIds
- Fix TOX encoding issues with certain JSON files
- Update Lambda Memory size to 3008
- Fix FindInMap failing when the first parameter is also FindInMap
- Fix key search function to appropriately respond to nested finds (FindInMap inside a FindInMap)

### 0.0.10
###### Features
- Capability to merge and modify the CloudFormation spec with provided JSON
  - Allows for changing what properties are required
  - Can change what resource types are allowed
- Remove warnings that were in error checks to keep errors focused on issues preventing success
- Improve circular dependency checks to go multiple levels deep
- Check null and duplicate values in JSON and YAML templates
###### Fixes
- Some primitive type properties were not getting checked
- Include support for Long as a number based check
- Improve get condition values to support more complex scenarios

### 0.0.8
###### Features
- Added a rule to check for only one resource property in a set
- Added a rule for more than one of resource properties in a set
- Added a rule for mutually exclusive resource properties

###### Fixes
- Support parsing JSON files that have tabs
- Better error handling for when a property is a list instead of an object
- Error handling for when files can't be read or don't exist

### 0.0.7
###### Features
- Fix for supporting more parameter types when checking REFs to parameters for Security Groups

### 0.0.6
###### Features
- Exit code non zero on errors or warnings

### 0.0.5
###### Features
- Testing CloudFormation resources against the Resource Spec
- Test Functions against supported included functions
- Test overall CloudFormation structure
- Test Regionalization of a template against the Resource Spec
- Ability to add additional rules on parameter
- In depth checks of values around AWS::EC2::VPC, AWS::EC2::Subnet, and AWS::EC2::SecurityGroup
