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
    const contributionsList = document.getElementById('contributions-list');
    const historyList = document.getElementById('history-list');
    const contributionsBadge = document.getElementById('contributions-badge');

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
        loadContributions();
        loadHistory();
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
            booksList.innerHTML = '<p style="text-align:center; color:var(--text-dim); padding:2rem;">Бібліотека ще порожня.</p>';
            return;
        }

        books.forEach(b => {
            const div = document.createElement('div');
            div.className = 'admin-card-item';
            div.innerHTML = `
                <div style="flex:1;">
                    <h4 style="margin:0;">${b.title}</h4>
                    <p style="font-size:0.8rem; color:var(--text-dim); margin:0.25rem 0 0;">Відправлень: <strong>${b.total_sends}</strong> | Читачів: <strong>${b.unique_users}</strong></p>
                </div>
                <button class="btn-secondary" style="border-color:var(--danger); color:var(--danger); font-size:0.7rem; padding:0.5rem 1rem;" onclick="deleteBook(${b.book_id})">Видалити</button>
            `;
            booksList.appendChild(div);
        });
    }

    window.deleteBook = async function(id) {
        const confirmed = await showConfirm(
            "Видалити книгу?",
            "Ви впевнені, що хочете видалити цю книгу? Цю дію неможливо скасувати.",
            "Видалити",
            true
        );
        if (!confirmed) return;
        try {
            const res = await fetch(`${API_URL}/admin/books/${id}`, { 
                method: 'DELETE',
                headers: getHeaders()
            });
            if (res.ok) {
                loadStats();
            } else {
                alert('Помилка видалення.');
            }
        } catch (e) { console.error(e); }
    };

    // --- Upload ---

    uploadBtn.onclick = async () => {
        if (!epubInput.files.length) return;
        
        uploadBtn.disabled = true;
        uploadStatus.textContent = 'Завантаження...';
        
        const formData = new FormData();
        [...epubInput.files].forEach(file => formData.append('epubs', file));

        try {
            const res = await fetch(`${API_URL}/admin/books`, {
                method: 'POST',
                headers: getHeaders(),
                body: formData
            });

            if (res.ok) {
                uploadStatus.textContent = 'Успішно завантажено!';
                uploadStatus.style.color = '#4ade80';
                epubInput.value = '';
                setTimeout(() => uploadStatus.textContent = '', 3000);
                loadStats();
            } else {
                const err = await res.json();
                uploadStatus.textContent = err.detail || 'Помилка завантаження.';
                uploadStatus.style.color = 'var(--danger)';
            }
        } catch (e) {
            uploadStatus.textContent = 'Помилка мережі.';
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
                feedbackList.innerHTML = '<p style="text-align:center; color:var(--text-dim); padding:2rem;">Відгуків ще немає.</p>';
                return;
            }

            data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).forEach(item => {
                const card = document.createElement('div');
                card.className = 'feedback-bubble new';
                const dateStr = new Date(item.created_at).toLocaleString();
                card.innerHTML = `
                    <p style="margin-bottom:0.75rem; line-height:1.5;">${item.message}</p>
                    <div style="font-size:0.75rem; color:var(--text-dim); display:flex; justify-content:space-between;">
                        <span>Отримано ${dateStr}</span>
                        <span style="color:var(--emerald-glow);">Новий</span>
                    </div>
                `;
                feedbackList.appendChild(card);
            });
        } catch (e) {
            console.error(e);
        }
    }

    // --- Contributions ---

    async function loadContributions() {
        try {
            const res = await fetch(`${API_URL}/admin/contributions`, { headers: getHeaders() });
            const data = await res.json();

            if (contributionsBadge) {
                contributionsBadge.textContent = data.length;
                contributionsBadge.style.display = data.length > 0 ? 'inline' : 'none';
            }

            contributionsList.innerHTML = '';
            if (!data || data.length === 0) {
                contributionsList.innerHTML = '<p style="text-align:center; color:var(--text-muted); padding:3rem;">Немає внесків для перевірки.</p>';
                return;
            }

            data.forEach(book => {
                const div = document.createElement('div');
                div.className = 'admin-card-item';
                div.innerHTML = `
                    <div style="width: 60px; height: 80px; border-radius: 8px; overflow:hidden; background: #222;">
                        <img src="/api/${book.cover_filepath}" style="width:100%; height:100%; object-fit:cover;">
                    </div>
                    <div style="flex:1;">
                        <h4 style="margin:0;">${book.title}</h4>
                        <p style="font-size:0.8rem; color:var(--text-muted); margin:0.25rem 0 0;">${book.author} | ID власника: ${book.owner_id}</p>
                    </div>
                    <div style="display:flex; gap:0.5rem;">
                        <button class="btn-secondary" style="padding:0.5rem 1rem; font-size:0.75rem; border-radius:8px;" onclick="downloadBook(${book.id})">Переглянути EPUB</button>
                        <button class="btn-primary" style="padding:0.5rem 1rem; font-size:0.75rem; border-radius:8px;" onclick="approveContribution(${book.id})">Схвалити</button>
                        <button class="btn-secondary" style="border-color:var(--danger); color:var(--danger); padding:0.5rem 1rem; font-size:0.75rem; border-radius:8px;" onclick="rejectContribution(event, ${book.id})">Відхилити</button>
                    </div>
                `;
                contributionsList.appendChild(div);
            });
        } catch (e) { console.error(e); }
    }

    window.downloadBook = async function(id) {
        const res = await fetch(`${API_URL}/books/download/${id}`, { headers: getHeaders() });
        if (res.ok) {
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `review_book_${id}.epub`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } else {
            alert("Не вдалося завантажити книгу для перегляду.");
        }
    };

    async function loadHistory() {
        try {
            const res = await fetch(`${API_URL}/admin/history`, { headers: getHeaders() });
            const userBooks = await res.json();

            historyList.innerHTML = '';
            if (!userBooks || userBooks.length === 0) {
                historyList.innerHTML = '<p style="text-align:center; color:var(--text-muted); padding:3rem;">Внесків від користувачів ще немає.</p>';
                return;
            }

            userBooks.reverse().forEach(book => {
                const div = document.createElement('div');
                div.className = 'admin-card-item';
                const statusColor = book.status === 'approved' ? 'var(--emerald-glow)' : 'var(--danger)';
                div.innerHTML = `
                    <div style="flex:1;">
                        <h4 style="margin:0;">${book.title}</h4>
                        <p style="font-size:0.8rem; color:var(--text-muted); margin:0.25rem 0 0;">
                            Завантажено користувачем #${book.owner_id} | Статус: <span style="color:${statusColor}; text-transform:capitalize;">${book.status}</span>
                        </p>
                    </div>
                    <button class="btn-secondary" style="padding:0.5rem 1rem; font-size:0.75rem; border-radius:8px;" onclick="downloadBook(${book.id})">Завантажити</button>
                `;
                historyList.appendChild(div);
            });
        } catch (e) { console.error(e); }
    }

    window.approveContribution = async function(id) {
        try {
            const res = await fetch(`${API_URL}/admin/contributions/${id}/approve`, { 
                method: 'POST', 
                headers: getHeaders() 
            });
            if (res.ok) {
                loadContributions();
                loadStats();
            }
        } catch (e) { console.error(e); }
    };

    window.rejectContribution = async function(event, id) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        const confirmed = await showConfirm(
            "Відхилити внесок?",
            "Це позначить книгу як відхилену і приховає її з бібліотеки. Ви все ще зможете бачити її в Історії.",
            "Відхилити",
            true
        );
        if (!confirmed) return;
        
        try {
            const res = await fetch(`${API_URL}/admin/contributions/${id}/reject`, { 
                method: 'POST', 
                headers: getHeaders() 
            });
            if (res.ok) {
                loadContributions();
                loadHistory();
            }
        } catch (e) { console.error(e); }
    };

    async function showConfirm(title, text, confirmText = "Підтвердити", isDanger = false) {
        return new Promise((resolve) => {
            const modal = document.getElementById('confirm-modal');
            const titleEl = document.getElementById('modal-title');
            const textEl = document.getElementById('modal-text');
            const confirmBtn = document.getElementById('modal-confirm');
            const cancelBtn = document.getElementById('modal-cancel');

            titleEl.textContent = title;
            textEl.textContent = text;
            confirmBtn.textContent = confirmText;
            confirmBtn.style.background = isDanger ? 'var(--danger)' : 'var(--emerald-primary)';
            confirmBtn.style.color = isDanger ? 'white' : 'black';

            modal.style.display = 'flex';

            const close = (res) => {
                modal.style.display = 'none';
                confirmBtn.onclick = null;
                cancelBtn.onclick = null;
                resolve(res);
            };

            confirmBtn.onclick = () => close(true);
            cancelBtn.onclick = () => close(false);
        });
    }

    // Start
    checkAuth();
});
