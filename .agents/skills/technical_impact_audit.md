# Skill: technical_impact_audit

## Objective
[cite_start]Identify all files and modules impacted by the proposed changes[cite: 1].

## Instructions
1. [cite_start]Scan `models.py` for changes to `user_credits` or `books` tables[cite: 16, 17].
2. Identify every Vanilla JS module that imports the modified functions.
3. Check "Green Velvet" CSS variables: If a variable is changed, list every component using it.
4. [cite_start]Verify "Zero-Bloat" Compliance: Ensure no new dependencies are being introduced[cite: 16].
5. Output: A `BLAST_RADIUS_MAP` listing files that require mandatory QA testing.
6. Transform `CONCEPT.md` and human feedback into a `TECHNICAL_SPEC.md`.
7. Dependency Mapping: List all impacted FastAPI routes and Vanilla JS modules.
8. Database Audit: Map any changes required for Neon PostgreSQL schemas, specifically regarding the Credit Economy.