# Skill: git_render_deploy

## Objective
Securely commit code and trigger a production build on Render.com.

## Instructions
1. **Pre-Flight**: Confirm `QAGuardian` status is "PASS."
2. **Commit**: Stage all changes and commit using the pattern `feat/fix(scope): description`.
3. **Push**: Sync changes to the `main` branch on GitHub.
4. **Deploy**: 
    - Trigger the build using the Render API:
      ```bash
      # // turbo
      curl -s -X POST -H "Authorization: Bearer $RENDER_API_KEY" "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys"
      ```
    - Monitor the deployment for a `build_in_progress` or `live` status.
5. **Persistence Verification**: Confirm the app connects to the Neon PostgreSQL DB after restart.