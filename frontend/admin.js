const API_URL = '/api';

document.addEventListener('DOMContentLoaded', () => {
    const totalBooksEl = document.getElementById('total-books-count');
    const totalSendsEl = document.getElementById('total-sends-count');
    const totalFeedbackEl = document.getElementById('total-feedback-count');
    
    const epubInput = document.getElementById('epub-input');
    const uploadBtn = document.getElementById('upload-btn');
    const uploadStatus = document.getElementById('upload-status');
    const booksList = document.getElementById('admin-books-list');
    const feedbackList = document.getElementById('feedback-list');

    // Get Auth from localStorage (stored by login.html)
    let authHeader = localStorage.getItem('admin_auth');

    function getHeaders() {
        return { 'Authorization': authHeader };
    }

    async function checkAuth() {
        if (!authHeader) {
            window.location.href = '/login.html';
            return;
        }

        try {
            const res = await fetch(`${API_URL}/admin/verify`, { headers: getHeaders() });
            if (!res.ok) {
                localStorage.removeItem('admin_auth');
                window.location.href = '/login.html';
            } else {
                // Auth OK, load data
                initDashboard();
            }
        } catch (e) {
            console.error('Auth check failed', e);
        }
    }

    function initDashboard() {
        loadStats();
        loadFeedback();
    }

    // --- Stats & Library ---

    async function loadStats() {
        try {
            const res = await fetch(`${API_URL}/admin/stats`, { headers: getHeaders() });
            const data = await res.json();

            totalBooksEl.textContent = data.total_books;
            totalSendsEl.textContent = data.total_sends;

            renderLibrary(data.books_stats);
        } catch (e) {
            console.error(e);
        }
    }

    function renderLibrary(books) {
        booksList.innerHTML = '';
        if (!books || books.length === 0) {
            booksList.innerHTML = '<p style="text-align:center; color:var(--text-dim); padding:2rem;">No books in library yet.</p>';
            return;
        }

        books.forEach(b => {
            const div = document.createElement('div');
            div.className = 'admin-card-item';
            div.innerHTML = `
                <div style="flex:1;">
                    <h4 style="margin:0;">${b.title}</h4>
                    <p style="font-size:0.8rem; color:var(--text-dim); margin:0.25rem 0 0;">Sends: <strong>${b.total_sends}</strong> | Readers: <strong>${b.unique_users}</strong></p>
                </div>
                <button class="btn-secondary" style="border-color:var(--danger); color:var(--danger); font-size:0.7rem; padding:0.5rem 1rem;" onclick="deleteBook(${b.book_id})">Delete</button>
            `;
            booksList.appendChild(div);
        });
    }

    window.deleteBook = async function(id) {
        if (!confirm('Are you sure you want to delete this book? This action cannot be undone.')) return;
        try {
            const res = await fetch(`${API_URL}/admin/books/${id}`, { 
                method: 'DELETE',
                headers: getHeaders()
            });
            if (res.ok) {
                loadStats();
            } else {
                alert('Delete failed.');
            }
        } catch (e) { console.error(e); }
    };

    // --- Upload ---

    uploadBtn.onclick = async () => {
        if (!epubInput.files.length) return;
        
        uploadBtn.disabled = true;
        uploadStatus.textContent = 'Uploading...';
        
        const formData = new FormData();
        [...epubInput.files].forEach(file => formData.append('epubs', file));

        try {
            const res = await fetch(`${API_URL}/admin/books`, {
                method: 'POST',
                headers: getHeaders(),
                body: formData
            });

            if (res.ok) {
                uploadStatus.textContent = 'Successfully uploaded!';
                uploadStatus.style.color = '#4ade80';
                epubInput.value = '';
                setTimeout(() => uploadStatus.textContent = '', 3000);
                loadStats();
            } else {
                const err = await res.json();
                uploadStatus.textContent = err.detail || 'Upload failed.';
                uploadStatus.style.color = 'var(--danger)';
            }
        } catch (e) {
            uploadStatus.textContent = 'Network error.';
        } finally {
            uploadBtn.disabled = false;
        }
    };

    // --- Feedback ---

    async function loadFeedback() {
        try {
            const res = await fetch(`${API_URL}/feedback/`, { headers: getHeaders() });
            const data = await res.json();
            
            totalFeedbackEl.textContent = data.length;

            feedbackList.innerHTML = '';
            if (!data || data.length === 0) {
                feedbackList.innerHTML = '<p style="text-align:center; color:var(--text-dim); padding:2rem;">No feedback received yet.</p>';
                return;
            }

            data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).forEach(item => {
                const card = document.createElement('div');
                card.className = 'feedback-bubble new';
                const dateStr = new Date(item.created_at).toLocaleString();
                card.innerHTML = `
                    <p style="margin-bottom:0.75rem; line-height:1.5;">${item.message}</p>
                    <div style="font-size:0.75rem; color:var(--text-dim); display:flex; justify-content:space-between;">
                        <span>Received at ${dateStr}</span>
                        <span style="color:var(--emerald-glow);">New</span>
                    </div>
                `;
                feedbackList.appendChild(card);
            });
        } catch (e) {
            console.error(e);
        }
    }

    // Start
    checkAuth();
});
