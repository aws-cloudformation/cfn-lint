# False Positives

A false positive is the most expensive bug this project can ship. Users run
cfn-lint in CI. A rule that fires on a valid template breaks builds for people
whose templates were always correct, and they cannot fix it — they can only
disable the rule or pin an old version.

Read this before writing any rule or approving any PR that adds one.

## The doctrine

### 1. A rule that fires on a valid template is worse than no rule at all

A missed error costs one failed deployment, and CloudFormation reports it
clearly. A false positive costs every user with that pattern, and they blame
cfn-lint rather than their template. When in doubt, ship nothing.

### 2. If you cannot resolve the value, stay silent

Values reach rules wrapped in `Ref`, `GetAtt`, `Sub`, `Fn::If`, `Fn::Select`,
mappings, and nested combinations of all of them. When a value cannot be fully
resolved, do not guess and do not warn — return no errors.

This is a promise the project makes in its README:

> it's a best effort to validate those values but the promise is to not fail
> if we can't understand or translate all the things that could be going on

Mechanically, this means a rule validates the shape it was handed. It does not
assume a plain scalar. Tests must include a non-scalar case (see
`testing-standards.md`).

### 3. Pick the right scope — do not flatten it to "always"

cfn-lint carries per-region schema knowledge, so "this is only true in some
regions" is **not** a reason to abandon a check. It is a reason to encode it in
the right place:

| The constraint is... | Encode it as |
|---|---|
| True everywhere, always | Rule or schema constraint |
| True only in some regions | `CfnLintJsonSchemaRegional`, or a per-region schema constraint in enhanced-schemas |
| Dependent on another property | `if`/`then` schema extension |
| Dependent on another *resource* | `cfnGather` extension |
| Account-, quota-, or opt-in-dependent | Warning (`W`) at most, often nothing |
| A style or preference judgment | Warning or informational (`I`), never an error |

Telling a soft quota from a hard bound is a lookup, not a guess: see "A
deployment rejection does not tell you the limit is universal" in
`verification.md`. Encoding a limit that Service Quotas marks `Adjustable: true`
is a false positive for every account that has had it raised.

Severity follows blast radius: `E` means CloudFormation **will** reject the
deployment. If a valid account configuration makes the template deploy fine, it
is not an `E`.

### 4. Prove the constraint before encoding it

Never derive a constraint from the base CloudFormation resource schema alone —
it is frequently silent or wrong about real limits.

Evidence, strongest first:

1. **A real deployment.** `CreateStack` or `UpdateStack` succeeding on a
   template that uses the value you would reject proves your constraint is
   wrong. A deployment failing with CloudFormation's own error proves it is
   right. Record the account, region, date, and the verbatim error.
2. **Real templates in the wild that are known to deploy.** Often beats a probe,
   and costs nothing. Search `test/fixtures/templates/`, this repo's issues, and
   public template corpora.
3. **A service-level API probe.** Call the service that owns the constraint
   (`lambda CreateFunction`, `s3 CreateBucket`, `rds CreateDBInstance`) and
   observe accept/reject. Second-best, because the service may accept what
   CloudFormation's provider rejects, or the reverse. Record account, region,
   and date.
4. **AWS documentation.** Good for intent, frequently stale on exact numbers.
5. **The base CFN resource schema.** Weakest. A hint, never proof.

**`aws cloudformation validate-template` is not evidence for a property-level
constraint.** It invokes no resource provider, so a property value, limit, enum
or cross-property rule can only be established by a deployment or by the owning
service's API — never cite `validate-template` as a probe for one. It *is*
evidence for what the control plane itself parses: parameter types, section
structure, name rules, intrinsic function shape, template size. For those it
returns the same error `CreateStack` does — see `verification.md`.

For a parameter constraint a deployment is free, because `Default` is validated
before any resource exists — see the parameter probe in `verification.md`.

Write the evidence into the PR description. A reviewer cannot validate a
magic number they cannot trace.

### 5. Every rule needs a test proving it stays silent

Firing on the bad case is the easy half. The test that matters is the
**near-miss valid case** — the value just inside the boundary, the same
property under the condition that makes it legal, the unresolvable function.

For every rule, the suite must contain:

- the invalid case (rule fires, with the expected message)
- the boundary valid case (rule silent)
- the same property made legal by a sibling property or condition (rule silent)
- a non-scalar / unresolvable value (rule silent)
- the property absent entirely (rule silent)

If a PR adds a rule and only tests the failing case, that is a blocking review
comment.

## Reviewing someone else's change

Ask, in order:

1. **What does this change reach?** Name every rule, schema and resource type that
   inherits the new behaviour. A change under `src/cfnlint/jsonschema/`, to a shared
   helper, or to a schema in `data/schemas/other/` is a change to the engine, not to
   a rule — enumerate the callers before judging anything else. If you cannot state
   the surface, you cannot review the fix.
2. **What does it stop reporting?** A change that only removes findings still needs
   justifying, and it will generate no user complaints to correct it later.
3. What is the evidence for this constraint, and is it traceable? A deployment
   or the owning service's API — not `validate-template`, not the base schema.
4. Which valid templates does this now reject? Name one, or prove there are none.
5. Is `E` the right severity, or does some valid account configuration deploy this?
6. Does it stay silent on `Ref`, `GetAtt`, `Fn::If`, and a non-scalar?
7. Does this belong in a rule at all, or in enhanced-schemas? See `schema-sources.md`.
8. Run it. See `verification.md` — do not accept the author's claim untested.
