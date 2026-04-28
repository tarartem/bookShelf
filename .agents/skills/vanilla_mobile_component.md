# Skill: vanilla_mobile_component

## Objective
[cite_start]Create framework-free UI components that adhere to the Bento Box layout[cite: 5, 16].

## Instructions
1. **FOLLOW THE `TECHNICAL_SPEC.md` DOCUMENT.**
2. **Z-Index Layering**: Always apply the project-standard hierarchy (Background: 1, Card: 10, Modal: 100).
3. **Fluid Scaling**: Use `rem` and `clamp()` for typography and padding; avoid `px` for containers.
4. [cite_start]**Aspect Ratio**: Force `aspect-ratio` on book covers and Bento tiles to prevent layout shifts[cite: 8].
5. **Touch-Safety**: Ensure all interactive `<a>` and `<button>` tags have a minimum hit-area of 44x44px.
6. [cite_start]**Glassmorphism Audit**: Apply the standard blur and transparency tokens to ensure readability over OLED Black[cite: 5].
7. Localization: Ensure all new strings are present in both UA and EN files and the interface language should be Ukrainian (UA).