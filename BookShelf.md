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
5.  **Credit Economy**: A "give-to-get" model where book requests cost 1 credit, incentivizing users to contribute back to the library.
6.  **Incentive Systems**: Automatic rewards for community behavior, including +5 credits for approved book uploads and +10 for opting into email notifications.
7.  **Secure Delivery**: Users receive EPUBs securely to their validated inboxes after a credit deduction. 
8.  **Admin Moderation**: A powerful dashboard allows administrators to review contributions, adjust user credit balances manually, and manage the platform's growth.
9.  **Account Management**: Secure user accounts with JWT sessions, email verification, customizable profiles showing credit balance/history, and password recovery.
10. **Localization**: The interface is fully bilingual (UA/EN) across all modules including the admin panel and profile settings.
11. **Mobile First Architecture**: Intuitive touch-targets, scroll persistence, modal dialogs, and native-feeling interactions engineered for smartphones first.

## Tech Stack
-   **Backend**: Python (FastAPI) + PostgreSQL (SQLAlchemy + psycopg2)
-   **Frontend**: Vanilla JS (ES6 Modules) + Native CSS Custom Properties (zero-bloat/no frameworks).
-   **Database**: Neon PostgreSQL (cloud-hosted, persistent, free tier — survives server restarts).
-   **Storage**: Uploaded EPUBs and covers stored on Render's Docker filesystem; database data is fully cloud-persistent via Neon.

## Features & Modules (Updated)
- [x] **User Accounts**: Registration, Login, and secure JWT verification tracking.
- [x] **Contributions**: Users can upload EPUBs which are hashed to prevent duplicates.
- [x] **Moderation Workflow**: Submissions remain "Pending" until an admin approves or rejects them.
- [x] **Account Safety**: Implemented password resets and cascading account deletion tools.
- [x] **Credit Economy**: Implemented a robust 1-credit-per-download system with transaction logging.
- [x] **Incentives**: Built logic for one-time notification bonuses and approval-based rewards.
- [x] **Admin Ecosystem**: Insights into book metrics, manual user credit adjustments, and historical logs.
- [x] **UI Polish**: Replacing all native browser pop-ups with stylized, contextual "Green Velvet" modals.
- [x] **Delivery Pipeline**: Robust background tasks for SMTP email delivery for book requesting and account recovery.

## 4. Documentation
- [Deployment Guide (DEPLOY.md)](DEPLOY.md)
- [User Implementation (UserAccount_Implementation_EN.md)](UserAccount_Implementation_EN.md)
- [Changelog (CHANGELOG.md)](CHANGELOG.md)
