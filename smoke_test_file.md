# 💨 Smoke Test Checklist: BookShelf

This document tracks the essential manual and automated checks to ensure the BookShelf application is production-ready, covering all key modules from authentication to the credit economy.

---

## 📱 1. Core UI & Navigation (Mobile-First)
- [ ] **Author Filter Expansion**: Click "Filter by Author" button.
    - *Expected*: Filter pills row should expand vertically on mobile.
    - *Expected*: Button should turn emerald green and stay active.
- [ ] **Search Auto-focus**: Click the search icon in the bottom nav.
    - *Expected*: Full-screen search overlay opens AND cursor focuses the input automatically.
- [ ] **Sticky Bottom Nav**: Scroll through the grid.
    - *Expected*: Bottom navigation items (Home, Search, Feedback) stay pinned.
- [ ] **Back Navigation Persistence**: Open book details, then click "Back".
    - *Expected*: Returns to the library grid, maintaining previous scroll position and search results.
- [ ] **Featured Carousel**: Swipe/click through the carousel.
    - *Expected*: Smooth transitions between featured book covers.
    - *Expected*: Books are randomized on every page load (Discovery mode).

## 🖥️ 2. Desktop & Responsive UX
- [ ] **Desktop Search**: Type in the header search bar.
    - *Expected*: Books grid filters in real-time without hiding other UI elements.
- [ ] **Adaptive Grid**: Resize browser from Desktop to Mobile width.
    - *Expected*: Layout shifts from multi-column to Bento-style (2 columns).
- [ ] **Reset Filters**: Select an author pill.
    - *Expected*: "Reset Filters" button appears immediately.
    - *Expected*: Clicking it clears all selections and search inputs.

## 🔐 3. Authentication & User Safety
- [ ] **Signup & Verification**: Register a new account.
    - *Expected*: System sends verification email (check console logs in dev mode).
    - *Expected*: Clicking link verifies account and redirects to login.
- [ ] **Forgot Password**: Use the recovery flow.
    - *Expected*: Temporary token allows setting a new password.
- [ ] **JWT Session Stability**: Log in, then refresh the page.
    - *Expected*: User remains logged in (session persists in localStorage).
- [ ] **Guest Profile Access**: Visit page without logging in.
    - *Expected*: Profile icon (SVG) is visible and clicking it redirects to `/login.html`.
- [ ] **Account Deletion**: Delete account from Profile settings.
    - *Expected*: Logs out user and purges all personal contributions from database.

## 💎 4. Credit Economy & Rewards
- [ ] **One-Time Bonus**: Opt-in for email notifications in Profile.
    - *Expected*: Account balance increases by **+10 credits** immediately.
- [ ] **Unlock Workflow**: Click "Unlock Book (1 Credit)" on an unowned book.
    - *Expected*: Balance decrements by 1.
    - *Expected*: "Download" and "Email" buttons appear.
- [ ] **Persistent Library**: Check "My Library" in Profile.
    - *Expected*: All previously unlocked books are visible in the grid.
- [ ] **Transaction Log**: Check profile statistics.
    - *Expected*: Member ID, Join Date, and correct Credit Balance are displayed.

## 📦 5. Contributions & Moderation
- [ ] **EPUB Upload**: Upload a valid .epub file in Profile.
    - *Expected*: "Preparing upload" status appears.
    - *Expected*: Metadata (Title, Author, Cover) is extracted automatically.
- [ ] **Duplicate Prevention**: Try uploading the same file again.
    - *Expected*: Error "This exact file already exists" (File Hashing test).
- [ ] **Admin Moderation**:
    - [ ] **Approval**: Admin approves a pending book.
        - *Expected*: Uploader receives **+5 credits**.
        - *Expected*: Book status badge turns Emerald "Approved".
    - [ ] **Rejection**: Admin rejects a book.
        - *Expected*: Book status badge turns Velvet "Rejected".

## 👑 6. Admin Dashboard
- [ ] **Bento Stats**: Access `/admin.html`.
    - *Expected*: Visual cards showing Total Users, Books, and System Health.
- [ ] **Manual Adjustments**: Change a user's credit balance via Admin UI.
    - *Expected*: Balance updates correctly in the database and user's profile.
- [ ] **User Voices**: Check the Feedback feed.
    - *Expected*: New feedback submissions appear with OLED-styled message bubbles.

## 🐘 7. Infrastructure & Persistence
- [ ] **Cloud Persistence (Neon)**: Log in and unlock a book, then trigger a server restart (or push to main).
    - *Expected*: Account details and "My Library" remain intact (survives ephemeral wipe).
- [ ] **Translation Toggle**: (If language switcher exists) Change language.
    - *Expected*: All UI elements (including buttons/placeholders) shift between UA/EN.

---

## 🧪 8. Automated Verification
- [ ] **Unit Tests**: Run `export PYTHONPATH=. && pytest tests/`.
    - *Expected*: All 8/8 functional tests pass (Auth, API, Library).
- [ ] **SMTP Check**: Run `python3 test_smtp.py`.
    - *Expected*: Test email is successfully queued and dispatched.
