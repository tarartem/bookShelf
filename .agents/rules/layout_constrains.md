---
trigger: always_on
---

# Rule: Mobile-First Layout Physics

- **Fluid over Fixed**: Forbidden to use `width` or `height` in `px` for layout containers. Use `rem`, `%`, or `vw/vh`.
- **The Overlap Ban**: Glassmorphism layers must follow a strict Z-index hierarchy:
    - Background: `z-index: 1`
    - Content Cards: `z-index: 10`
    - Bento Box Dividers: `z-index: 20`
    - "Green Velvet" Modals: `z-index: 100`.
- **Touch-Target Safety**: Every interactive element (pills, buttons, toggles) MUST have a minimum hit area of `44px x 44px` to ensure mobile usability[cite: 15].
- **Bento Constraints**: On viewports < 600px, "Bento Box" grids must collapse into a single-column `flex-direction: column` to prevent squashed elements.