# 💨 Smoke Test Checklist: BookShelf

This document tracks the essential manual and automated checks to ensure the BookShelf application is production-ready.

---

## 📱 Mobile UI & Navigation
- [ ] **Author Filter Expansion**: Click "Filter by Author" button.
    - *Expected*: Filter pills row should expand.
    - *Expected*: Button should turn green and stay focused.
- [ ] **Search Auto-focus**: Click the search icon in the bottom nav.
    - *Expected*: Search overlay opens AND the keyboard/cursor focuses the input automatically.
- [ ] **Sticky Nav**: Scroll through the grid.
    - *Expected*: Bottom navigation stays pinned.
- [ ] **Back Navigation**: From a Book Details page, click "Back".
    - *Expected*: Returns to the library grid without a full page reload.

## 🖥️ Desktop UI
- [ ] **Desktop Search**: Type in the top-right search bar.
    - *Expected*: Books grid filters in real-time.
- [ ] **Author Chips**: Select an author pill.
    - *Expected*: "Reset Filters" button appears immediately.
- [ ] **Responsiveness**: Resize browser from Desktop to Mobile width.
    - *Expected*: Layout shifts to Bento-style (2 columns) and desktop search hides.

## 🌍 Localization & Content
- [ ] **Translation Consistency**: Check "Back" button on Details page.
    - *Expected (EN)*: `Back` (Single arrow via CSS).
    - *Expected (UK)*: `← Назад до бібліотеки`.
- [ ] **Placeholder Text**: Check search inputs.
    - *Expected (UK)*: `Знайти наступну книгу...`.
- [ ] **Dynamic Counts**: Check author pills.
    - *Expected*: Number of books for each author is displayed next to their name.

## 🔐 Core Business Logic (Backend)
- [ ] **Combined Filtering**: Select an author, THEN type in the search bar.
    - *Expected*: Results should match BOTH (Author AND Title/Search query).
- [ ] **Credit System**: Unlock a book (costs 1 credit).
    - *Expected*: Credit balance in Profile decrements.
    - *Expected*: "Unlock" button disappears, replaced by "Download/Email" options.
- [ ] **Email Delivery**: Send a book to a test email.
    - *Expected*: Toast "Book sent successfully" appears.
    - *Expected*: (Manual) Check inbox for EPUB attachment.

## 🧪 Automated Coverage
- [ ] **Backend Unit Tests**: Run `PYTHONPATH=. pytest tests/`.
    - *Expected*: 8/8 tests pass.
- [ ] **Smoke Test Script**: Run `python3 scripts/smoke_test.py`.
    - *Expected*: Health check returns `healthy`.

---

## 🚀 Deployment Status
- **Environment**: [Production (Render)](https://bookshelf-qtlv.onrender.com)
- **Last Verified Commit**: `6bff470`
- **Database**: Neon PostgreSQL
