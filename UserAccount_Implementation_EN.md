# User Account System Implementation Plan (BookShelf)

This document outlines a step-by-step plan for implementing personal user accounts with content upload capabilities.

## 📋 Task Checklist

### Iteration 1: Database [✅]
- [x] Create `User` model (`email`, `hashed_password`, `is_verified`, `created_at`). (Defined in models.py)
- [x] Add `owner_id` field to `Book` model (Many-to-One relationship). (Defined in models.py)
- [x] Add `file_hash` field to `Book` model for duplicate checking. (Defined in models.py)
- [x] Perform database migration. (Completed via migrate_db.py)

### Iteration 2: Registration and Verification [✅]
- [x] Create API endpoint for Signup. (Implemented in routers/auth.py)
- [x] Implement Email delivery service with verification tokens. (Implemented in email_service.py)
- [x] Create page/endpoint to handle verification links (`/verify/{token}`). (Endpoint in auth.py)

### Iteration 3: Login and Security [✅]
- [x] Implement API endpoint for Login (JWT issuance). (Implemented in auth.py)
- [ ] Implement "Forgot Password" functionality (Email with temporary tokens).
- [x] Create endpoint for account deletion. (Implemented in auth.py)

### Iteration 4: Profile Interface [ ]
- [ ] Create `profile.html` page (Mobile First).
- [ ] Implement display of user status and basic profile data.
- [ ] Add redirection logic (if not logged in -> redirect to Login).

### Iteration 5: Upload Logic [✅]
- [x] Create API for user EPUB uploads. (Implemented in routers/books.py)
- [x] Integrate `epub_service` for automatic metadata extraction. (Integrated in upload endpoint)
- [x] Implement duplicate check (via file hash). (Implemented in upload endpoint)

### Iteration 6: Upload Visualization [✅]
- [x] Create upload form with metadata editing (Title/Author). (Implemented in profile.html)
- [x] Create "My Books" list in profile. (Implemented in profile.html)
- [x] Add status badges (Pending, Approved). (Implemented in status badges)

### Final Refinement & Polishing [✅]
- [x] Implement "Forgot Password" functionality. (Implemented in auth router)
- [x] Create Reset Password page UI. (Implemented in reset-password.html)
- [x] Final UI/UX polish across the app. (Polished profile and transition flows)
- [x] Conduct final verification and testing. (Verified via end-to-end scripts)

---

## 🛠️ Technical Details
- **Auth**: JWT (JSON Web Tokens).
- **Password Hashing**: Bcrypt.
- **Duplicates**: MD5 hash for files.
- **Frontend**: Vanilla JS (API interaction via `fetch`).

## ⚠️ Important Notes
- **Data Policy**: Do not delete books from the DB upon user request (as per project requirements).
- **Design**: Adhere to the "Green Velvet" aesthetics for all new interfaces.
- **Compatibility**: Ensure existing admin panel features remain stable.
