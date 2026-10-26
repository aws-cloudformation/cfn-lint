# Rule Development Standards

Read [`../context/false-positives.md`](../context/false-positives.md) first. A
rule that fires on a valid template is worse than no rule at all, and that
constraint shapes every decision below.

Before writing a rule, confirm it belongs here at all — most property
constraints belong in enhanced-schemas. See
[`../context/schema-sources.md`](../context/schema-sources.md).

## Rule Types

Listed in order of preference. Choose the simplest one that expresses the
constraint.

### 1. Schema Extension + `CfnLintJsonSchema` (the common case)

A JSON Schema file carries the logic; the Python class carries the rule ID and
the error message. Use for anything conditional on a sibling property.

**Requires both a Python rule and a JSON schema file.**

```python
import cfnlint.data.schemas.extensions.aws_lambda_function
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class FunctionCapacityProviderTimeout(CfnLintJsonSchema):
    id = "E3717"
    shortdesc = "Validate Lambda function Timeout based on CapacityProviderConfig"
    description = (
        "The maximum Timeout of 900 seconds only applies to functions without "
        "CapacityProviderConfig."
    )
    source_url = "https://docs.aws.amazon.com/lambda/latest/dg/configuration-timeout.html"
    tags = ["resources", "lambda"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::Lambda::Function/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_function,
                filename="capacity_provider_timeout.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return f"{instance.get('Timeout')} is greater than the maximum of 900 ..."
```

Schema at `src/cfnlint/data/schemas/extensions/<resource_type>/<name>.json`:

```json
{
  "if": {
    "properties": { "CapacityProviderConfig": false },
    "required": []
  },
  "then": {
    "properties": { "Timeout": { "maximum": 900 } }
  }
}
```

Use `CfnLintJsonSchemaRegional` when the constraint differs by region.

### 2. Cross-Resource Extension (`cfnGather`)

Same shape as above, but the schema uses `cfnGather` to follow `Ref`/`GetAtt`
into another resource. Documented in
[`../../docs/cfn-schema-specification.md`](../../docs/cfn-schema-specification.md).
Examples: `aws_sqs_queue/queue_dlq.json`, `aws_ecs_service/service_fargate.json`.

### 3. Template Path Rule (`CfnLintKeyword`)

Validates the value at a template path, when the check needs Python but not
cross-resource data. Pass `keywords=[...]`; wildcards are supported.

### 4. Custom Python Rule (`CloudFormationLintRule`)

Full control, for template-wide analysis — circular dependencies, graph
properties, cross-section consistency. **Rare: roughly 25 of 400 rule files.**
Do not reach for this by default.

### 5. Schema Correction or Value Constraint — not in this repo

A plain `pattern`, `enum`, `minimum`, or `maximum` on one property belongs in
[`resource-provider-enhanced-schemas`](https://github.com/aws-cloudformation/resource-provider-enhanced-schemas)
as an RFC 6902 patch in `schemas/patches/extensions/<resource_type>/manual.json`.
It reaches cfn-lint on the next schema sync. Editing
`src/cfnlint/data/schemas/providers/` or `resources/` never works — both are
gitignored and overwritten by `--update-specs`.

## Rule Metadata

- **id** — correct category (see Rule ID System in `structure.md`); find the
  next free ID in `docs/rules.md`
- **shortdesc** — one line, no period
- **description** — why this matters; state the constraint precisely
- **source_url** — the AWS documentation that establishes the constraint
- **tags** — `["resources", "<service>"]`

## Severity

Severity follows consequence, not confidence:

- **`E`** — CloudFormation **will** reject the deployment. If any valid account
  configuration deploys successfully, it is not an error.
- **`W`** — valid but inadvisable, or quota- and opt-in-dependent.
- **`I`** — informational, opt-in via `-c I`.

## Validation Approach

1. **Prove the constraint.** A real deployment first, then real templates known
   to deploy, then a service-level API probe, then AWS docs. Never the base CFN
   schema alone, and never `aws cloudformation validate-template` for a property
   constraint — it invokes no resource provider, though it does establish
   control-plane structure such as parameter types. Then check whether the
   number is a soft account quota, which is never an
   `E` — see [`../context/verification.md`](../context/verification.md).
2. **Decide where it belongs** — this repo or enhanced-schemas.
3. **Pick the simplest rule type** that expresses it.
4. **Handle unresolvable values.** `Ref`, `GetAtt`, `Sub`, `Fn::If`, mappings
   and nestings of them must produce no error.
5. **Handle conditions** when the resource can be conditional.

## Error Messages

State the actual value, the limit, and the condition under which the limit
applies. The reader is looking at their template, not at your rule.

> `5400 is greater than the maximum of 900 for functions without 'CapacityProviderConfig'`

## Before Submitting

Full command reference in
[`../context/verification.md`](../context/verification.md).

```shell
.venv/bin/python -m pytest test/unit/rules/resources/<service>/test_<rule>.py
.venv/bin/cfn-lint -t /tmp/bad.yaml                              # must fire
.venv/bin/cfn-lint -t /tmp/good.yaml                             # must be silent
.venv/bin/cfn-lint -t "test/fixtures/templates/good/**/*.yaml"   # no regressions
pre-commit run --all-files
```

## Documentation

- Add the rule to `docs/rules.md`
- Record the evidence for the constraint in the PR description: account, region,
  date and the verbatim error for a deployment; account, region and date for a
  service API probe
