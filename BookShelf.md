# BookShelf App

## 1. Project Overview
The webapplication where users can forward available books in epub format to their email address. The application will be used by me and my friends.    

## Persona
i'm a product owner with basic software development skills. I want to create a webapplication. I want app to be simple yet reliable. 

## Objective
1.  **Immersive Browsing**: User can browse books in a modern, "Bento Box" and "Glassmorphism" styled interface (OLED Black theme).
2.  **Dedicated Content**: Each book has its own dedicated full-page view (instead of a popup) with immersive background effects.
3.  **Discovery**: A "Featured Carousel" automatically promotes top volumes at the start of the library.
4.  **Advanced Filtering**: Users can search by title/author AND filter by multiple authors simultaneously using interactive "pills".
5.  **Localization**: The interface is multilingual, defaulting to **Ukrainian (UA)** with an English (EN) fallback for the UI.
6.  **Secure Delivery**: Users receive EPUBs via validated email with unique-send tracking.
7.  **Admin Control**: Admin managed library (Upload/Delete/Analyze) and feedback review.

## Tech Stack
-   **Backend**: Python (FastAPI) + SQLite
-   **Frontend**: Vanilla JS (ES6 Modules) + CSS Custom Properties (No heavy frameworks for speed/reliability).
-   **Storage**: Local storage for EPUBs/Covers.

## Definition of Done (Updated)
- [x] Admin: Individual and Bulk folder upload.
- [x] Admin: Remove books and view send metrics.
- [x] UI: Modern Bento Grid layout with Glassmorphism effects.
- [x] UI: Immersive full-page book details with cover-blurred backgrounds.
- [x] UI: Featured book carousel at the top of the catalog.
- [x] Search: prioritised title search and multi-author select filters.
- [x] i18n: Complete Ukrainian interface (Default) + English strings.
- [x] UX: Perfect scroll persistence when navigating between library and book pages.
- [x] Delivery: Validated email sending with book attachments.
- [x] Stats: Visible unique reader counts and share stats per book.
- [x] Feedback: User submission and storage system.

## 4. Documentation
- [Deployment Guide (DEPLOY.md)](file:///Users/tarartem/Documents/Antigravity/BookShelf/DEPLOY.md)
- [UX Design Notes (UXnotes.md)](file:///Users/tarartem/Documents/Antigravity/BookShelf/books/UI/UXnotes.md)


