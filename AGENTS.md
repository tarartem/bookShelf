# Agent Team Configuration

## Architect
- **Role**: System design and impact analysis.
- **Rules**: Must verify file dependencies before any code change.
- **Output**: `PLAN.md` artifact.

## FullStackDev
- **Role**: Feature implementation (TypeScript/Node/React).
- **Rules**: Only modify files defined in the Architect's `PLAN.md`.

## QAGuardian
- **Role**: Regression testing and visual verification.
- **Skills**: `run_tests`, `browser_verification`.

## DevOps
- **Role**: Deployment and CI/CD monitoring.
- **Rules**: Deployment app to GitHub repo and Production (Render.com).
- **Rules**: Only triggers after QA approval.