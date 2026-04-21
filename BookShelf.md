# BookShelf App

## 1. Project Overview
BookShelf is a community-driven web application where readers can discover, share, and forward available books in EPUB format to their email addresses. Built with a **Mobile First** philosophy, the app provides a premium, native-like experience on smartphones while maintaining a sleek, adaptive layout for desktop browsers. It serves as a central hub where people can effortlessly contribute their own books to the library and take from the collective collection.

## Persona
I am a product owner and developer who wants to construct an elegant, reliable, and user-centric platform that democratizes book sharing using modern design principles.

## Objective
1.  **Immersive Browsing**: Users browse books in a modern, "Bento Box" and "Glassmorphism" styled interface utilizing an OLED Black and Green Velvet theme.
2.  **Community Driven**: Registered users can upload their own EPUBs to contribute to the global library.
3.  **Dedicated Content Context**: Each book has its own dedicated full-page view with immersive, cover-blurred backgrounds and detailed metadata.
4.  **Discovery & Filtering**: Features include a "Featured Carousel", dynamic random shuffling, and multi-select interactive pills for advanced author filtering.
5.  **Secure Delivery**: Users receive EPUBs securely to their validated inboxes. 
6.  **Admin Moderation**: A powerful dashboard allows administrators to review community contributions, download pending books, and approve or reject submissions while maintaining an audit trail.
7.  **Account Management**: Secure user accounts with JWT sessions, email verification, customizable profiles, password recovery, and full upload history.
8.  **Localization**: The interface is fully bilingual, defaulting to **Ukrainian (UA)** with seamless English (EN) fallbacks.
9.  **Mobile First Architecture**: Intuitive touch-targets, scroll persistence, modal dialogs, and native-feeling interactions engineered for smartphones first.

## Tech Stack
-   **Backend**: Python (FastAPI) + SQLite (SQLAlchemy)
-   **Frontend**: Vanilla JS (ES6 Modules) + Native CSS Custom Properties (zero-bloat/no frameworks).
-   **Storage**: Persistent local disk storage structured for dockerized Render deployment.

## Features & Modules (Updated)
- [x] **User Accounts**: Registration, Login, and secure JWT verification tracking.
- [x] **Contributions**: Users can upload EPUBs which are hashed to prevent duplicates.
- [x] **Moderation Workflow**: Submissions remain "Pending" until an admin approves or rejects them.
- [x] **Account Safety**: Implemented password resets and cascading account deletion tools.
- [x] **Admin Ecosystem**: Insights into book metrics, unique user shares, and historical contribution logs.
- [x] **UI Polish**: Replacing all native browser pop-ups with stylized, contextual "Green Velvet" modals.
- [x] **Delivery Pipeline**: robust background tasks for SMTP email delivery for book requesting and account recovery.

## 4. Documentation
- [Deployment Guide (DEPLOY.md)](DEPLOY.md)
- [User Implementation (UserAccount_Implementation_EN.md)](UserAccount_Implementation_EN.md)
- [Changelog (CHANGELOG.md)](CHANGELOG.md)
