# 🚀 Deployment Guide: BookShelf App

This guide explains how to deploy and update the BookShelf application on **Render.com** (Free Plan).

## 1. Initial Deployment

1.  **Preparation**:
    *   Ensure your `.env` variables (SMTP, etc.) are NOT in the repo.
    *   Ensure the `books/` folder contains the EPUB files you want to load.
2.  **GitHub Setup**:
    *   Push your code to a GitHub repository.
    *   **Crucial**: The `books/` folder must be tracked by Git (check `.gitignore`).
3.  **Render Setup**:
    *   Create a new **Web Service** on Render.
    *   Connect your GitHub repository.
    *   Select **Docker** as the environment.
    *   Set the following Environment Variables in the Render Dashboard:
        *   `DATABASE_URL`: `sqlite:///./data/bookshelf.db`
        *   `SMTP_HOST`: (your SMTP server)
        *   `SMTP_PORT`: (e.g., 587)
        *   `SMTP_USER`: (your email)
        *   `SMTP_PASS`: (your app password)
        *   `SENDER_EMAIL`: (your email)
4.  **Launch**:
    *   Render will build the Docker image and start the service.
    *   The books will populate in the background.

---

## 2. Persistence & Migrations (v3.1+)

As of v3.1, BookShelf supports **Persistent Disks** on Render (Starter plan and above).

1. **Persistent Disk**: 
   * Mount a disk at `/app/data` to ensure `bookshelf.db` survives redeploys.
   * Mount a disk at `/app/uploads` to preserve user-contributed books.
2. **Automated Migrations**:
   * The `Dockerfile` now runs `python3 -m backend.migrate_db` automatically on startup.
   * You no longer need to run manual SQL or scripts to update the database schema when new features (like Credits) are added.

---

## 3. Making Changes (Update Guide)

When you make changes to the code or add new books locally, follow these steps to redeploy:

### Step 1: Commit Your Changes
Add your modified files and commit them:
```bash
# To update code:
git add backend/ frontend/
git commit -m "Update code changes"
```

### Step 2: Push to GitHub
```bash
git push origin main
```

### Step 3: Monitor Redeployment
1.  Go to your **Render Dashboard**.
2.  You should see a new deployment triggered automatically.
3.  **Check Logs**: Go to the "Logs" tab. You should see `Migration completed successfully.` messages followed by the app startup.

---

## 4. Best Practices
*   **Database Management**: Use the Admin Panel to manage users and credits.
*   **Backups**: Periodically download `bookshelf.db` from the Render shell if you are not using a persistent disk.
