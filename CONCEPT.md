# UX Concept: "My Library" (Unlocked Books View)

## 1. Overview
Currently, when a user permanently unlocks (downloads/emails) a book, there is no centralized place to view all their unlocked books. They have to search the global catalog to find them again.
This feature resolves that UX friction by creating a "My Library" location—a dedicated view where users can quickly access their purchased/unlocked items.

## 2. Target Personas Addressed
* **The Casual Commuter (Maya)**: Needs to find her books in < 30 seconds. A dedicated "My Library" view prevents her from having to search or filter the global catalog on a spotty connection.
* **The Silver Reader (Elena)**: Needs simple discovery. Having a dedicated space for "her books" makes the app feel more like a personal bookshelf, reducing tech friction.

## 3. Proposed User Flow & UI Layout
* **Integration Point**: The `profile.html` page will host the tabbed view, but access will be heavily simplified via the main navigation.
* **Tabbed Interface**: We will transform the "My Contributions" section in `profile.html` into a tabbed interface.
  * **Tab 1: My Library (Unlocked Books)** - *Default View*. Displays all books the user has spent credits on or unlocked.
  * **Tab 2: My Uploads (Contributions)** - Displays the books the user has uploaded to the platform.
* **Navigation**: A dedicated "My Books" element will be added directly to the floating navigation bar (the top nav island). Clicking this icon will take the user instantly to the "My Library" tabbed interface in `profile.html`, bypassing the need to navigate through general profile settings.
* **Visuals**: Books in "My Library" will be displayed using the existing `mini-book-card` component for consistency and fast loading (important for Maya and Amina). We'll add an action button (e.g., "Download" or "Send to Kindle") directly on these cards to minimize clicks.

## 4. Friction Thresholds Maintained
* **max_clicks_to_action**: Improved. Click "My Books" in Nav -> Read/Download (2 clicks).
* **mobile_ergonomics**: The tabbed interface will be optimized for thumb reach, placed clearly under the profile header.
* **total_page_weight_kb**: Using the `mini-book-card` ensures we don't load heavy UI elements, keeping it under the 800kb limit for Amina.

## 5. Technical Considerations (High-Level)
* Need a backend endpoint (e.g., `/api/books/unlocked`) to fetch the user's unlocked books.
* Update `profile.html` to include the tabbed UI logic.
* Update `translations.js` for the new UI text ("My Library", "My Uploads").

---
**Status**: Awaiting Human Approval before proceeding to SUT Phase (Step 2) or Architecture (Step 3).
