# TECHNICAL SPECIFICATION: "My Library" Feature

## 1. Overview
This specification details the technical implementation of the "My Library" feature as approved in `CONCEPT.md`. The goal is to provide users with a tabbed interface in their profile to view both their permanently unlocked books and their uploaded contributions, with easy access via the floating navigation bar.

## 2. Impacted Components

### 2.1 Backend (`backend/routers/books.py`)
* **Status**: ✅ Already implemented.
* **Endpoints**:
  * `GET /api/books/library`: Returns the list of books the user has permanently unlocked (joined via `UserLibrary`).
  * `GET /api/books/my`: Returns the list of books the user has uploaded.
* **Action Required**: None. The backend is fully prepared.

### 2.2 Frontend: Main Navigation (`frontend/index.html`)
* **Component**: Floating Top Navigation (`#site-header`).
* **Changes**:
  * Add a "My Books" icon/button next to the existing profile trigger.
  * Clicking this element should navigate to `profile.html?tab=library`.
* **Component**: Mobile Bottom Navigation (`.mobile-bottom-nav`).
* **Changes**:
  * Add "My Books" item to the mobile bottom navigation for quick access on small screens.

### 2.3 Frontend: Profile Page (`frontend/profile.html`)
* **Component**: Main Section (`.profile-main`).
* **Changes**:
  * Convert the single `h3` header ("My Contributions") into a tabbed navigation structure.
  * **Tab 1: "My Library"** (Active by default if `?tab=library` is set).
  * **Tab 2: "My Uploads"**.
  * Add JavaScript logic to handle tab switching.
    * When "My Library" is active: fetch from `/api/books/library`.
    * When "My Uploads" is active: fetch from `/api/books/my`.
  * URL Parameter support: On page load, read the `tab` query parameter to decide which tab to open automatically.

### 2.4 Frontend: Translations (`frontend/translations.js`)
* **Changes**:
  * Add translation keys to support the new UI elements:
    * `myLibrary`: "My Library" (EN), "Моя Бібліотека" (UK)
    * `myUploads`: "My Uploads" (EN), "Мої Завантаження" (UK)
    * `myBooks`: "My Books" (EN), "Мої Книги" (UK)

## 3. Data Flow
1. User clicks "My Books" in the navigation.
2. Browser navigates to `profile.html?tab=library`.
3. `profile.html` JS reads the URL parameter, sets the "My Library" tab as active.
4. JS fetches `GET /api/books/library` using the auth token.
5. `mini-book-card` elements are rendered.

---
**Status**: Implemented.
