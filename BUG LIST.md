# BUG LIST — BookShelf My Library Release
> Version: v1.1 | Reported: 2026-04-28 | Strategy: 3 Batched Fixes

---

## Fix Strategy

The 5 bugs are grouped into **3 batches** based on shared files to avoid double-touching the same code and to keep commits atomic and reviewable.

| Batch | Bugs | Files Touched | Priority |
| :--- | :--- | :--- | :--- |
| **Batch 1** | BUG-006, BUG-002, BUG-003 | `profile.html` | 🔴 Critical — Fix first |
| **Batch 2** | BUG-001, BUG-004 | `app.js`, `index.css` | 🟡 Medium |
| **Batch 3** | BUG-005 | `index.css` | 🔴 High — CSS-only |

---

## BUG-001 · Desktop: Book Icon Overlaps Search Bar in Header

- **Platform**: Desktop
- **Severity**: 🟡 Medium
- **Batch**: 2 (with BUG-004)
- **Status**: `Open`

**Description**
The "My Library" icon/button added to the header navigation bar overlaps with the search bar on desktop viewports. Elements are not properly spaced or z-indexed.

**Affected Files**
- `frontend/app.js` — header rendering logic
- `frontend/index.css` — `.top-nav-island`, `.nav-actions` layout rules

**Acceptance Criteria**
The book icon and search bar must never intersect. Minimum 12px gap required between all header elements on viewports ≥ 768px.

---

## BUG-002 · Desktop & Mobile: "Approved" Chip Visible in My Library Tab

- **Platform**: Desktop + Mobile
- **Severity**: 🟢 Low
- **Batch**: 1 (with BUG-003)
- **Status**: `Open`

**Description**
The `status-badge status-approved` chip ("Approved") is rendered on every book card inside the **My Library** tab. This badge is only meaningful in the **My Uploads** tab where users track their submission status. In My Library, all books are already unlocked and accessible — the badge is misleading and clutters the UI.

**Affected Files**
- `frontend/profile.html` — `loadMyBooks()` function, card `innerHTML` template

**Acceptance Criteria**
`status-badge` must not render when `activeTab === 'library'`. It should only appear in the Uploads tab.

---

## BUG-003 · Desktop & Mobile: Library Book Cards are Non-Interactive

- **Platform**: Desktop + Mobile
- **Severity**: 🟡 Medium
- **Batch**: 1
- **Status**: ✅ `Fixed`

**Description**
In the current implementation, clicking a book card in the **My Library** tab does nothing (click is suppressed). Users find this "broken" as they expect to interact with their books.
**Strategic Decision:**
Instead of suppressing the click or navigating away to the catalog, we should:
1. Allow the card to navigate back to the catalog ONLY IF it's to the specific book details view.
2. OR (Better) Open a small contextual modal in the profile page for "Download / Send to Kindle".
3. **Decision:** We will restore navigation to the catalog page with the `?book=ID` parameter, but ensure the "Back" button in the catalog returns the user to the Profile page if they came from there.

**Affected Files**
- `frontend/profile.html`
- `frontend/app.js` (for back button logic)

**Acceptance Criteria**
1. Clicking a library card must take the user to the book's detail view in the catalog.
2. The user must be able to return to the Profile page easily (smart "Back" button).

---

## BUG-004 · Mobile: My Library Icon Visible in Header Navigation Bar

- **Platform**: Mobile only
- **Severity**: 🟢 Low
- **Batch**: 2 (with BUG-001)
- **Status**: `Open`

**Description**
The My Library icon/link is displayed in the mobile header navigation bar. On mobile, this consumes scarce navigation space and breaks the thumb-zone layout defined in the Bento Constraints rule. The profile page is already accessible via the user avatar navigation.

**Affected Files**
- `frontend/app.js` — nav bar rendering
- `frontend/index.css` — responsive visibility rules for `.top-nav-island` children

**Acceptance Criteria**
The My Library icon must be hidden on viewports < 600px (`display: none` or a responsive utility class). Mobile navigation must remain single-column and uncluttered.

---

## BUG-005 · Mobile: Profile Page — Settings & My Profile Sections Overflow the Screen

- **Platform**: Mobile only
- **Severity**: 🔴 High
- **Batch**: 3 (standalone)
- **Status**: `Open`

**Description**
On mobile viewports (≤ 393px), the "My Profile" stats card and "Settings" card in the profile sidebar are wider than the viewport, causing horizontal overflow and a broken layout. This violates two project rules:
- **Mobile-First Layout Physics**: No `width` in `px` for layout containers.
- **Bento Constraints**: Grids must collapse to a single-column `flex-direction: column` on viewports < 600px.

**Affected Files**
- `frontend/index.css` — `.profile-sidebar`, `.profile-card`, `.profile-grid` responsive breakpoint rules
- `frontend/profile.html` — sidebar HTML structure

**Acceptance Criteria**
The "Green Velvet" and "Bento Box" components must fit within `100vw`. No horizontal scrolling permitted.

---

## BUG-006 · Desktop & Mobile: Profile Data Not Loading (Empty State)

- **Platform**: All
- **Severity**: 🔴 Critical
- **Batch**: 1
- **Status**: ✅ `Fixed`

**Description**
Authenticated users see empty placeholders (`...`, `0`, `#000`) instead of their email, credits, and library data. 
**Root Cause Analysis:**
1. A JavaScript `TypeError` occurs in `profile.html` at line 422 because it attempts to call `.addEventListener()` on `document.getElementById('nav-feedback-trigger')`, which is `null` (element missing from HTML). This stops all subsequent script execution, including `applyLanguage()` and `loadProfile()`.
2. The translation helper `t()` needs to be more robust against browser locales not present in `translations.js`.

**Affected Files**
- `frontend/profile.html`
- `frontend/translations.js`

**Acceptance Criteria**
1. Fix the `null` reference crash in `profile.html`.
2. Implement robust language detection with a mandatory fallback to `uk`.
3. User information must load regardless of browser locale.
4. Script errors must be caught to prevent total page failure.

---

## Status Tracker

| ID | Title | Batch | Severity | Status | Fixed In |
| :--- | :--- | :---: | :--- | :--- | :--- |
| BUG-001 | Book icon overlaps search bar | 2 | 🟡 Medium | ✅ `Fixed` | `index.html`, `index.css` |
| BUG-002 | "Approved" chip in My Library | 1 | 🟢 Low | ✅ `Fixed` | `profile.html` |
| BUG-003 | Library Book Cards are Interactive | 1 | 🟡 Medium | ✅ `Fixed` | `profile.html`, `app.js` |
| BUG-004 | My Library icon on mobile header | 2 | 🟢 Low | ✅ `Fixed` | `index.html`, `app.js` |
| BUG-005 | Profile sidebar overflow on mobile | 3 | 🔴 High | ✅ `Fixed` | `index.css` |
| BUG-006 | Profile Data Not Loading (Empty State) | 1 | 🔴 Critical | ✅ `Fixed` | `profile.html`, `app.js` |
