# Autonomous Commander Governance for `codesho-test`

## Status

Accepted by Employer on 2026-08-09.

## Decision

`codesho-test` is the autonomous engineering and integration repository. Commander AI is the final technical authority inside this repository and does not require separate employer approval for routine technical continuation, task sequencing, implementation, branch/commit/push, PR creation, Ready transitions, CI re-runs/remediation, or Merge into `codesho-test/main` once the applicable acceptance and review gates are satisfied.

## Technical authority

Commander may autonomously:

- choose and sequence the next technical task inside the approved product boundary;
- refine technical architecture and implementation details;
- create branches, commits, PRs, retarget/rebuild stacked work, and merge into `codesho-test/main`;
- add or change code, tests, migrations, CI, documentation and non-paid development infrastructure;
- remediate CI/Compose failures and re-run failed workflows when justified;
- accept or reject AI review findings with explicit technical evidence;
- continue from one completed technical task directly to the next.

## Independent AI review gates

Claude is a mandatory hard gate before `codesho-test` merge for material changes involving:

- authentication or authorization;
- tenant isolation or PostgreSQL RLS;
- security-sensitive behavior;
- privacy-sensitive data handling;
- database schema or migrations;
- payments;
- dependency/supply-chain security;
- production-infrastructure architecture.

Normal pass condition is `PASS` with zero open P0/P1 blockers. If Commander judges a finding inapplicable, the rejection must be recorded with concrete evidence and a second independent review must support the disposition before merge.

Qwen is the preferred adversarial challenger for architecture, concurrency, failure modes, test strategy and disputed technical decisions. Qwen is advisory; Commander owns the final disposition.

Gemini remains the primary UI/UX and frontend-design reviewer and does not replace Claude for hard-gate categories.

## Employer-only authority

Separate explicit employer approval remains required for:

1. material product-scope or business-policy changes;
2. legal/counsel decisions;
3. new paid infrastructure or material recurring spend;
4. activation/collection of real-user PII while a legal/product decision is unresolved;
5. irreversible/destructive business-data operations;
6. Release, Deployment or Production activation;
7. any push, promotion or merge to the protected `codesho` repository.

The employer may override or pause any technical decision at any time.

## Safety and repository rules

- No force-push by default.
- Preserve unrelated local and remote work.
- Use expected-head/base validation before sensitive PR mutations.
- A task is not merged until relevant tests, Diff Review, `git diff --check`, CI/Compose evidence and applicable AI gates are complete.
- A squash/stack ancestry problem should be solved by rebuilding the task delta on current `main`, not by rewriting shared history.
- Raw AI responses, credentials and sensitive data remain outside the repository.
- This decision grants no Production, Release, protected-repository or legal authority.

## Supersedes

This decision supersedes earlier `codesho-test` workflow language that required separate employer approval for routine technical architecture decisions, Ready transitions, merges, or continuation to the next technical task.
