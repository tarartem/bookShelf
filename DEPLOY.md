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

## 2. Making Changes (Update Guide)

When you make changes to the code or add new books locally, follow these steps to redeploy:

### Step 1: Commit Your Changes
Add your modified files and commit them:
```bash
# To update code:
git add backend/ frontend/
git commit -m "Update code changes"

# To add new books:
git add books/
git commit -m "Add new books to collection"
```

### Step 2: Push to GitHub
```bash
git push origin main
```

### Step 3: Monitor Redeployment
1.  Go to your **Render Dashboard**.
2.  You should see a new deployment triggered automatically.
3.  **Check Logs**: Go to the "Logs" tab. You should see `DEBUG` messages showing the startup task indexing your books.
4.  **Persistence**: On the Free plan, Render wipes the ephemeral storage. However, our **Startup Background Task** will automatically reload all books from the `books/` folder into the database as soon as the app starts.

---

## 3. Best Practices
*   **Book Management**: To "remove" a book permanently from the free plan, delete it from your local `books/` folder, commit, and push.
*   **Large Collections**: If you have many books, the first few minutes after a redeploy may show an incomplete list while the background task finishes indexing.
