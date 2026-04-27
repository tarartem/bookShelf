---
description: Moves a task through Architect, Dev, QA, and DevOps.
---

Step 1: Act as @UX_Strategist. 
   - Interview Human for requirements.
   - Generate `CONCEPT.md`. 
   - [HALT] Wait for Human Approval.

Step 2: Act as @UX_Strategist (SUT Phase).
   - Load `.agents/personas/target_users.json`.
   - Run `simulate_user_flow` against the concept.
   - Present "Synthetic Friction Report" to Human.
   - [HALT] Wait for Human Confirmation.

Step 3: Act as @Architect.
   - Convert `CONCEPT.md` + User Feedback into `TECHNICAL_SPEC.md`.
   - Map all impacted components.

Step 4: Act as @FullStackDev.
   - Implement based on `TECHNICAL_SPEC.md`.
   - Continuous linting and type-checking.

Step 5: Act as @QAGuardian.
   - Perform `visual_regression_check`.
   - Performs testing in browser checking a new functionality and if everything else works correctly (nothing was broken), records the session and gives a summary.
   - Perform test on mobile application.
   - Perform test on desktop version.
   - Pay attention to the layout so UI elements won't overlap.
   - If success: Act as @DevOps to stage PR.
   - If fail: Return to Step 4 with error logs.

Step 6: Act as @DevOps.
   - Commit changes to GitHub using a descriptive conventional commit.
   - Trigger production deployment to Render.com using the Secure API Key.
   - Monitor the Render Deploy Hook until status is "Live".
   - Notify Human: "Feature is now live at [URL]".