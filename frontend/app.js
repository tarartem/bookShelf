const API_URL = '/api';

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const booksGrid = document.getElementById('books-grid');
    
    const emailModal = document.getElementById('email-modal');
    const closeEmailModal = document.getElementById('close-email-modal');
    const emailForm = document.getElementById('email-form');
    
    const feedbackModal = document.getElementById('feedback-modal');
    const openFeedbackBtn = document.getElementById('open-feedback-btn');
    const closeFeedbackModal = document.getElementById('close-feedback-modal');
    const fbForm = document.getElementById('feedback-form');
    
    // New Modal Elements
    const modalCover = document.getElementById('modal-book-cover');
    const modalDescription = document.getElementById('modal-book-description');
    const requestTriggerBtn = document.getElementById('request-trigger-btn');
    const emailFormContainer = document.getElementById('email-request-form-container');
    const actionArea = document.getElementById('action-area');
    
    let currentBookId = null;

    // Fetch and bind books
    async function loadBooks(query = '') {
        booksGrid.innerHTML = '<div class="loading">Loading books…</div>';
        try {
            const res = await fetch(`${API_URL}/books?search=${encodeURIComponent(query)}`);
            if (!res.ok) throw new Error(`Server error: ${res.status}`);
            const books = await res.json();

            booksGrid.innerHTML = '';
            if (books.length === 0) {
                booksGrid.innerHTML = '<p style="color:var(--text-secondary);grid-column:1/-1;text-align:center;">No books found. Ask the admin to add some!</p>';
                return;
            }

            books.forEach(book => {
                const card = document.createElement('div');
                card.className = 'book-card';
                card.innerHTML = `
                    <div class="book-cover">
                        ${book.cover_filepath
                            ? `<img src="/api/${book.cover_filepath}" alt="${book.title}" loading="lazy">`
                            : `<span style="font-size:3rem;">📖</span>`}
                    </div>
                    <div class="book-info">
                        <h3 class="book-title">${book.title}</h3>
                        <p class="book-author">${book.author || 'Unknown'}</p>
                    </div>
                `;
                card.addEventListener('click', () => openBookModal(book));
                booksGrid.appendChild(card);
            });
        } catch (e) {
            booksGrid.innerHTML = `<p style="color:var(--danger)">Failed to load books: ${e.message}</p>`;
        }
    }

    // Open Book Email Modal
    async function openBookModal(book) {
        currentBookId = book.id;
        document.getElementById('modal-book-title').innerText = book.title;
        document.getElementById('modal-book-author').innerText = book.author || 'Unknown';
        modalDescription.innerText = book.description || "A captivating tale that will keep you on the edge of your seat. This book is currently in high demand from our library members!";
        
        // Reset modal state
        document.getElementById('send-status').innerText = '';
        document.getElementById('user-email').value = '';
        emailFormContainer.style.display = 'none';
        actionArea.style.display = 'block';

        if (book.cover_filepath) {
            modalCover.src = `/api/${book.cover_filepath}`;
            modalCover.style.display = 'block';
        } else {
            modalCover.style.display = 'none';
        }
        
        emailModal.classList.add('active');

        // Fetch Stats
        try {
            const res = await fetch(`${API_URL}/books/${book.id}/stats`);
            const stats = await res.json();
            document.getElementById('modal-stats').innerHTML = `
                <span>📧 Sent <strong>${stats.total_sends}</strong> times</span>
                <span>👥 <strong>${stats.unique_users}</strong> readers</span>
            `;
        } catch (e) {
            console.error(e);
        }
    }

    // Toggle email form inside modal
    requestTriggerBtn.addEventListener('click', () => {
        actionArea.style.display = 'none';
        emailFormContainer.style.display = 'block';
        document.getElementById('user-email').focus();
    });

    // Modal Close logic for Email
    closeEmailModal.addEventListener('click', () => emailModal.classList.remove('active'));
    
    // Feedback Modal logic
    openFeedbackBtn.addEventListener('click', () => {
        document.getElementById('fb-status').innerText = '';
        document.getElementById('fb-message').value = '';
        feedbackModal.classList.add('active');
    });
    closeFeedbackModal.addEventListener('click', () => feedbackModal.classList.remove('active'));

    // Global Modal Click-out Event
    window.addEventListener('click', (e) => {
        if(e.target === emailModal) emailModal.classList.remove('active');
        if(e.target === feedbackModal) feedbackModal.classList.remove('active');
    });

    // Handle Search
    searchInput.addEventListener('input', (e) => {
        const val = e.target.value.trim();
        loadBooks(val);
    });

    // Handle form submit for email
    emailForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('user-email').value;
        const msg = document.getElementById('send-status');

        msg.innerText = 'Sending...';
        msg.style.color = '#fff';

        try {
            const res = await fetch(`${API_URL}/books/${currentBookId}/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });

            const data = await res.json();
            if (res.ok) {
                msg.innerText = 'Success! Check your inbox.';
                msg.style.color = '#4ade80';
            } else {
                msg.innerText = data.detail || 'Failed to request book.';
                msg.style.color = 'var(--danger)';
            }
        } catch (err) {
            msg.innerText = 'Network error.';
            msg.style.color = 'var(--danger)';
        }
    });

    // Handle feedback
    fbForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = document.getElementById('fb-message').value;
        const msgSpan = document.getElementById('fb-status');
        
        msgSpan.innerText = 'Submitting...';
        msgSpan.style.color = '#fff';

        try {
            const res = await fetch(`${API_URL}/feedback/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            if (res.ok) {
                msgSpan.innerText = 'Feedback submitted successfully! Thank you.';
                msgSpan.style.color = '#4ade80';
                fbForm.reset();
                setTimeout(() => feedbackModal.classList.remove('active'), 2500);
            }
        } catch(err) {
            msgSpan.innerText = 'Error submitting feedback.';
            msgSpan.style.color = 'var(--danger)';
        }
    });

    // Init
    loadBooks();
});
