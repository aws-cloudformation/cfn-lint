# Where Schemas Come From

**Most property constraints do not belong in this repository.** Getting this
wrong wastes the whole change: edits to the downloaded provider schemas are
gitignored and silently overwritten on the next `--update-specs`.

Authoritative reference: [`docs/internal.md`](../../docs/internal.md).

## Two repositories

| | Repository | Contains |
|---|---|---|
| **Schemas** | [`resource-provider-enhanced-schemas`](https://github.com/aws-cloudformation/resource-provider-enhanced-schemas) | Raw CFN provider schemas + patches, assembled and published as `schemas-cfn-lint.zip` |
| **Rules** | this repo | Rule logic, schema *extensions*, the validator, the CLI |

cfn-lint downloads the published artifact at runtime:

```shell
cfn-lint --update-specs          # add --force to re-download
```

It extracts into two **gitignored** directories:

- `src/cfnlint/data/schemas/providers/` — per-region index: which types exist, plus content hashes
- `src/cfnlint/data/schemas/resources/` — the schema bodies, content-addressed as `<hash>.json`

Editing either one is never the fix. Your change vanishes on the next update,
and it was never in version control to begin with.

## Decision tree

**Is the constraint a plain value restriction** — `pattern`, `enum`, `minimum`,
`maximum`, `minLength`, `maxLength`, `required` — **on a single property?**

→ It belongs in **enhanced-schemas**, as an RFC 6902 patch at
`schemas/patches/extensions/<resource_type>/manual.json`. It flows into cfn-lint
on the next schema sync. Nothing changes in this repo.

**Does it depend on another property of the same resource?**

→ Schema **extension** in this repo:
`src/cfnlint/data/schemas/extensions/<resource_type>/<name>.json`, using
`if`/`then`, plus a `CfnLintJsonSchema` rule. This is the common case for a new
rule ID. Example: `aws_lambda_function/capacity_provider_timeout.json` (E3717).

**Does it depend on a different resource, reached by `Ref` or `GetAtt`?**

→ Schema extension using `cfnGather`. See the `cfnGather` section of
[`docs/cfn-schema-specification.md`](../../docs/cfn-schema-specification.md).
Examples: `aws_sqs_queue/queue_dlq.json`, `aws_ecs_service/service_fargate.json`.

**Is it template-wide analysis** (circular dependencies, graph properties,
cross-section consistency)?

→ A custom Python rule extending `CloudFormationLintRule`.

**Is the schema simply wrong or missing a property?**

→ enhanced-schemas, not here. Do not work around a schema bug with a rule; fix
the schema so every consumer benefits.

## In-repo patches are nearly gone

`src/cfnlint/data/schemas/patches/` still exists but holds only a handful of
files. It is **not** the place for new constraints — that work moved to
enhanced-schemas. If you believe you need a patch here, say why in the PR.

## Working in enhanced-schemas

Notes that save time, confirmed against that repo:

- Patch precedence is `format` < `lifecycle` < `manual` < `smithy`.
- `smithy` **auto-defers to `manual`**: the generator skips emitting any field
  `manual.json` already governs. To override one smithy constraint, add just
  that single field to `manual.json` — siblings keep coming from smithy.
- Assembly forces `us-east-1` first and deduplicates by content, so one content
  variant per type serves all regions. The per-region files record which types
  *exist*, not content differences.

## Verifying a schema change before it is released

You do not have to wait for a release. Point cfn-lint at a locally built
schema set with `XDG_CACHE_HOME`, making sure the built `version.json` date
beats the bundled one. See `verification.md`.
