const API_URL = '/api';

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const epubInput = document.getElementById('epub-input');
    const selectedFilesDiv = document.getElementById('selected-files');
    const uploadBtn = document.getElementById('upload-btn');
    const uploadStatus = document.getElementById('upload-status');
    const totalBooksEl = document.getElementById('total-books-count');
    const totalSendsEl = document.getElementById('total-sends-count');
    const booksList = document.getElementById('admin-books-list');
    const feedbackList = document.getElementById('feedback-list');

    let selectedFiles = [];

    // ── Drop zone drag events ──────────────────────────────────────────────
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        addFiles([...e.dataTransfer.files]);
    });
    dropZone.addEventListener('click', () => epubInput.click());
    epubInput.addEventListener('change', () => addFiles([...epubInput.files]));

    function addFiles(files) {
        const epubs = files.filter(f => f.name.toLowerCase().endsWith('.epub'));
        if (epubs.length < files.length) {
            uploadStatus.textContent = `⚠️ ${files.length - epubs.length} non-EPUB file(s) were ignored.`;
            uploadStatus.style.color = '#f59e0b';
        }
        selectedFiles = [...selectedFiles, ...epubs];
        renderFileList();
    }

    function renderFileList() {
        selectedFilesDiv.innerHTML = '';
        if (selectedFiles.length === 0) {
            uploadBtn.style.display = 'none';
            return;
        }
        uploadBtn.style.display = 'block';
        const ul = document.createElement('ul');
        ul.className = 'file-list';
        selectedFiles.forEach((f, i) => {
            const li = document.createElement('li');
            li.className = 'file-list-item';
            li.innerHTML = `
                <span>📄 ${f.name} <small>(${(f.size / 1024 / 1024).toFixed(1)} MB)</small></span>
                <button class="btn-icon" data-idx="${i}" title="Remove">✕</button>
            `;
            ul.appendChild(li);
        });
        selectedFilesDiv.appendChild(ul);

        // Remove individual files
        selectedFilesDiv.querySelectorAll('.btn-icon').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const idx = parseInt(btn.dataset.idx);
                selectedFiles.splice(idx, 1);
                renderFileList();
            });
        });
    }

    // ── Upload ─────────────────────────────────────────────────────────────
    uploadBtn.addEventListener('click', async () => {
        if (selectedFiles.length === 0) return;

        uploadBtn.disabled = true;
        uploadStatus.textContent = `⏳ Uploading ${selectedFiles.length} file(s)…`;
        uploadStatus.style.color = '#fff';

        const formData = new FormData();
        selectedFiles.forEach(f => formData.append('epubs', f));

        try {
            const res = await fetch(`${API_URL}/admin/books`, {
                method: 'POST',
                body: formData
            });

            if (res.ok) {
                const added = await res.json();
                uploadStatus.textContent = `✅ Successfully added ${added.length} book(s)!`;
                uploadStatus.style.color = '#4ade80';
                selectedFiles = [];
                renderFileList();
                epubInput.value = '';
                loadStats();
            } else {
                const data = await res.json();
                uploadStatus.textContent = `❌ ${data.detail || 'Upload failed.'}`;
                uploadStatus.style.color = '#ef4444';
            }
        } catch (err) {
            uploadStatus.textContent = `❌ Network error: ${err.message}`;
            uploadStatus.style.color = '#ef4444';
        } finally {
            uploadBtn.disabled = false;
        }
    });

    // ── Stats & Catalog ────────────────────────────────────────────────────
    async function loadStats() {
        try {
            const res = await fetch(`${API_URL}/admin/stats`);
            const data = await res.json();

            totalBooksEl.textContent = data.total_books;
            totalSendsEl.textContent = data.total_sends;

            booksList.innerHTML = '';
            if (data.books_stats.length === 0) {
                booksList.innerHTML = '<p>No books yet.</p>';
                return;
            }
            data.books_stats.forEach(bs => {
                const item = document.createElement('div');
                item.className = 'list-item';
                item.innerHTML = `
                    <div class="list-item-info">
                        <strong>${bs.title}</strong>
                        <span class="badge">Sends: ${bs.total_sends} | Unique: ${bs.unique_users}</span>
                    </div>
                    <button class="btn-danger btn-sm" onclick="deleteBook(${bs.book_id})">Delete</button>
                `;
                booksList.appendChild(item);
            });
        } catch (e) {
            booksList.innerHTML = '<p>Failed to load stats.</p>';
        }
    }

    window.deleteBook = async function (id) {
        if (!confirm('Delete this book? This cannot be undone.')) return;
        try {
            const res = await fetch(`${API_URL}/admin/books/${id}`, { method: 'DELETE' });
            if (res.ok) loadStats();
            else alert('Failed to delete book.');
        } catch (e) {
            alert('Error: ' + e.message);
        }
    };

    // ── Feedback ───────────────────────────────────────────────────────────
    const totalFeedbackEl = document.getElementById('total-feedback-count');

    async function loadFeedback() {
        try {
            const res = await fetch(`${API_URL}/feedback/`);
            const data = await res.json();
            
            if (totalFeedbackEl) {
                totalFeedbackEl.textContent = data.length || 0;
            }

            feedbackList.innerHTML = '';
            if (data.length === 0) {
                feedbackList.innerHTML = '<p style="color:var(--text-secondary);">No feedback yet.</p>';
                return;
            }
            data.forEach(item => {
                const div = document.createElement('div');
                div.className = 'list-item feedback-item';
                div.innerHTML = `
                    <div class="feedback-text">${item.message}</div>
                    <div class="feedback-meta">
                        <span>User Feedback</span>
                        <span>${new Date(item.created_at).toLocaleString()}</span>
                    </div>
                `;
                feedbackList.appendChild(div);
            });
        } catch (e) {
            feedbackList.innerHTML = '<p style="color:var(--danger);">Failed to load feedback.</p>';
        }
    }

    // ── Init ───────────────────────────────────────────────────────────────
    loadStats();
    loadFeedback();
});
