---
description: Moves a task through Architect, Dev, QA, and DevOps.
---

Step 1: Act as @Architect.
   - Analize a list of bugs
   - Make a strategic decision how to fix those bugs, in what order.
   - Create well formatted bug list document from the reported bugs `BUG LIST.md`.

Step 2: Act as @FullStackDev.
   - Fix bugs based on order and details provided in `BUG LIST.md`.

Step 3: Act as @QAGuardian.
   - Perform verification of fixed bugs based on document `BUG LIST.md`
   - Perform `visual_layout_audit`.
   - Performs testing in browser checking a new functionality and if everything else works correctly (nothing was broken), records the session and gives a summary.
   - Perform test on mobile application.
   - Perform test on desktop version.
   - Pay attention to the layout so UI elements won't overlap.
  
Step 4: Act as @DevOps.
   - Commit changes to GitHub using a descriptive conventional commit.
   - Trigger production deployment to Render.com using the Secure API Key.
   - Monitor the Render Deploy Hook until status is "Live".
   - Notify Human: "Feature is now live at [URL]".