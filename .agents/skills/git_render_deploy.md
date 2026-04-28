# Skill: git_render_deploy

## Objective
Securely commit code and trigger a production build on Render.com.

## Instructions
1. **Pre-Flight**: Confirm `QAGuardian` status is "PASS."
2. **Commit**: Stage all changes and commit using the pattern `feat/fix(scope): description`.
3. **Push**: Sync changes to the `main` branch on GitHub.
4. **Deploy**: 
   - Call the Render.com Deploy Hook using `process.env.RENDER_API_KEY`.
   - Monitor the deployment URL for a `200 OK` status.
5. **Persistence Verification**: Confirm the app connects to the Neon PostgreSQL DB after restart.