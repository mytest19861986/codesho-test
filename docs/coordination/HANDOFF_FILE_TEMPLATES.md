# AI Coordination File Protocol

Coordination root on the employer workstation: `H:\codesho\codesho`.
Use the existing Claude/Gemini/ChatGPT folders; folder-name matching is
case-insensitive. Do not put source code in coordination folders.

## ChatGPT folder

- `COMMANDER_TO_CODEX.md`: current approved task, priority and acceptance criteria.
- `CODEX_TO_COMMANDER.md`: latest implementation/test/blocker report.
- `EMPLOYER_DECISIONS.md`: approved gates only; never infer approval from silence.

## Claude folder

- `REVIEW_REQUEST.md`: exact question, architecture context, commit and file manifest.
- `FILES_MANIFEST.md`: no more than 19 files per review package.
- `REVIEW_RESPONSE.md`: Claude output copied without alteration.
- `REVIEW_RESOLUTION.md`: Commander/Codex disposition for every finding.

## Gemini folder

- `UI_TASK.md`: screen, persona, states, responsive/accessibility requirements.
- `UI_REFERENCES.md`: locations and provenance of employer-provided samples.
- `UI_RESPONSE.md`: Gemini proposal or review.
- `UI_REVIEW_RESOLUTION.md`: accepted/rejected items and implementation mapping.

## Required report fields

Every request/report should contain:

- Timestamp and authoring agent
- Repository, branch and commit
- Goal and scope
- Files included or changed
- Acceptance criteria
- Commands/tests and actual results
- Risks, blockers and decisions needed
- Explicit next owner and next action
