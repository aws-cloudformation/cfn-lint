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

Severity follows blast radius: `E` means CloudFormation **will** reject the
deployment. If a valid account configuration makes the template deploy fine, it
is not an `E`.

### 4. Prove the constraint before encoding it

Never derive a constraint from the base CloudFormation resource schema alone —
it is frequently silent or wrong about real limits.

Evidence, strongest first:

1. **Real templates that deploy.** The most persuasive evidence, and often
   better than an API probe: if templates in the wild use a value you are about
   to reject, your constraint is wrong. Search `test/fixtures/templates/`, this
   repo's issues, and public template corpora.
2. **A live API probe.** Call the service and observe what it accepts and
   rejects. Record the account, region, and date in the PR.
3. **AWS documentation.** Good for intent, often stale on exact numbers.
4. The base CFN schema. Weakest. Treat as a hint only.

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

## Reviewing someone else's rule

Ask, in order:

1. What is the evidence for this constraint, and is it traceable?
2. Which valid templates does this now reject? Name one, or prove there are none.
3. Is `E` the right severity, or does some valid account configuration deploy this?
4. Does it stay silent on `Ref`, `GetAtt`, `Fn::If`, and a non-scalar?
5. Does this belong in a rule at all, or in enhanced-schemas? See `schema-sources.md`.
6. Run it. See `verification.md` — do not accept the author's claim untested.
