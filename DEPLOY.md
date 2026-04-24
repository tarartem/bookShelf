# 🚀 Deployment Guide: BookShelf App

This guide explains how to deploy and update the BookShelf application on **Render.com** (Free Plan) with **Neon PostgreSQL**.

## 1. Initial Deployment

1.  **Preparation**:
    *   Ensure your `.env` variables are NOT in the repository.
    *   **Get a Neon Database**: Create a free project at [neon.tech](https://neon.tech) and copy the connection string.
2.  **GitHub Setup**:
    *   Push your code to a GitHub repository.
3.  **Render Setup**:
    *   Create a new **Web Service** on Render.
    *   Connect your GitHub repository.
    *   Select **Docker** as the environment.
    *   Set the following Environment Variables in the Render Dashboard:
        *   `DATABASE_URL`: (your Neon connection string starting with `postgresql://`)
        *   `SECRET_KEY`: (a long random string for JWT security)
        *   `SMTP_HOST`: `smtp.gmail.com`
        *   `SMTP_PORT`: `587`
        *   `SMTP_USER`: (your email)
        *   `SMTP_PASS`: (your app password)
        *   `FROM_EMAIL`: (your email)
        *   `BASE_URL`: `https://your-app-name.onrender.com`
        *   `ADMIN_SECRET`: (your chosen admin password)
4.  **Launch**:
    *   Render will build the Docker image and start the service.
    *   The app will automatically run migrations on the Neon database.

---

## 2. Persistence & Cloud Database (v3.2+)

As of v3.2, BookShelf uses **Neon PostgreSQL** for permanent data storage.

1. **Persistent Data**: 
   * **Database**: User accounts, credits, logs, and metadata are stored in the cloud (Neon) and **survive server restarts/redeploys**.
   * **Files**: On the Render **Free Plan**, uploaded files (EPUBs and covers) are stored in the temporary Docker filesystem and **will be lost** when the server restarts or code is updated. 
   * *Note: To persist uploaded files, upgrade to a Render paid plan and attach a "Persistent Disk" to `/app/uploads`.*
2. **Automated Migrations**:
   * The `Dockerfile` runs `python3 -m backend.migrate_db` automatically on every startup.
   * Schema updates (like adding new columns) are handled gracefully and safely.

---

## 3. Making Changes (Update Guide)

When you make changes to the code locally, follow these steps to redeploy:

### Step 1: Commit Your Changes
```bash
git add .
git commit -m "Update feature X"
```

### Step 2: Push to GitHub
```bash
git push origin main
```

### Step 3: Monitor Redeployment
1.  Go to your **Render Dashboard**.
2.  A new deployment will trigger automatically.
3.  **Check Logs**: Go to the "Logs" tab. You should see `Migration completed successfully.` followed by `Uvicorn running`.

---

## 4. Best Practices
*   **Database Management**: Use the Admin Panel to manage users and credits.
*   **Security**: Never share your `DATABASE_URL` or `ADMIN_SECRET`.
*   **Local Dev**: Locally, the app defaults to `sqlite:///./bookshelf.db` if no `DATABASE_URL` is set, allowing for easy offline development.
