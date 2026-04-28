---
trigger: always_on
---

# Design & Stability Rules

- **Mobile Proportionality**: Use `rem` and `clamp()` for all font sizes and container padding. 
- **Overlap Prevention**: Strict Z-index hierarchy:
  - Background/Blur: 1
  - Bento Content: 10
  - Contextual Modals: 100
- **Bilingual Safety**: Ukrainian (UA) strings must be checked for overflow on small mobile screens (393px wide).
- **Zero-Bloat**: No external frameworks or CSS libraries (Tailwind/React) allowed. 
- **Persistence**: EPUBs stored on Docker; metadata in Neon Cloud PostgreSQL.