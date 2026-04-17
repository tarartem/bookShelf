const API_URL = '/api';

document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const searchInput = document.getElementById('search-input');
    const booksGrid = document.getElementById('books-grid');
    const toastContainer = document.getElementById('toast-container');
    
    // Modals
    const emailModal = document.getElementById('email-modal');
    const closeEmailModal = document.getElementById('close-email-modal');
    const emailForm = document.getElementById('email-form');
    const feedbackModal = document.getElementById('feedback-modal');
    const closeFeedbackModal = document.getElementById('close-feedback-modal');
    const fbForm = document.getElementById('feedback-form');
    
    // Modal Content
    const modalCover = document.getElementById('modal-book-cover');
    const modalDescription = document.getElementById('modal-book-description');
    const modalTitle = document.getElementById('modal-book-title');
    const modalAuthor = document.getElementById('modal-book-author');
    const requestTriggerBtn = document.getElementById('request-trigger-btn');
    const emailFormContainer = document.getElementById('email-request-form-container');
    const actionArea = document.getElementById('action-area');
    const descriptionBox = document.getElementById('description-box');
    const cancelEmailBtn = document.getElementById('cancel-email-btn');
    const shareBookBtn = document.getElementById('share-book-btn');
    
    // Controls
    const backToTopBtn = document.getElementById('back-to-top-btn');
    const navItems = document.querySelectorAll('.nav-item');
    const searchTrigger = document.getElementById('nav-search-trigger');
    const feedbackTrigger = document.getElementById('nav-feedback-trigger');
    
    let currentBookId = null;
    let allBooks = [];

    // --- Core Functions ---

    // Fetch and bind books
    async function loadBooks(query = '') {
        try {
            const res = await fetch(`${API_URL}/books?search=${encodeURIComponent(query)}`);
            if (!res.ok) throw new Error(`Server error: ${res.status}`);
            allBooks = await res.json();

            renderBooks(allBooks);
            checkDeepLink(); // Check hash after books are loaded
        } catch (e) {
            booksGrid.innerHTML = `<p style="color:var(--danger); grid-column: 1/-1; text-align: center;">Failed to load library: ${e.message}</p>`;
        }
    }

    function renderBooks(books) {
        booksGrid.innerHTML = '';
        if (books.length === 0) {
            booksGrid.innerHTML = '<p style="color:var(--text-dim); grid-column: 1/-1; text-align: center; padding: 4rem;">The library is currently silent. Try a different search.</p>';
            return;
        }

        books.forEach((book, index) => {
            const card = document.createElement('div');
            card.className = 'book-card';
            
            // Randomly assign bento classes to first few items for visual interest
            if (index === 0) card.classList.add('bento-featured');
            
            card.innerHTML = `
                <div class="book-cover-wrapper">
                    ${book.cover_filepath
                        ? `<img src="/api/${book.cover_filepath}" alt="${book.title}" loading="lazy">`
                        : `<div style="height:100%; display:flex; align-items:center; justify-content:center; background:var(--velvet-deep); font-size:3rem;">📖</div>`}
                </div>
                <div class="book-info">
                    <h3 class="book-title">${book.title}</h3>
                    <p class="book-author">${book.author || 'Unknown Author'}</p>
                </div>
            `;
            card.addEventListener('click', () => openBookModal(book));
            booksGrid.appendChild(card);
        });
    }

    // Modal Interaction
    async function openBookModal(book) {
        currentBookId = book.id;
        modalTitle.innerText = book.title;
        modalAuthor.innerText = book.author || 'Unknown Author';
        modalDescription.innerText = book.description || "In the quiet corners of this library, a story waits to be discovered. This volume promises an journey beyond the ordinary.";
        
        // Update URL Hash without jumping
        window.history.replaceState(null, null, `#book-${book.id}`);

        // Reset state
        document.getElementById('send-status').innerText = '';
        document.getElementById('user-email').value = '';
        emailFormContainer.style.display = 'none';
        descriptionBox.style.display = 'block';
        actionArea.style.display = 'block';

        if (book.cover_filepath) {
            modalCover.src = `/api/${book.cover_filepath}`;
        }
        
        emailModal.classList.add('active');

        // Fetch Dynamic Stats
        try {
            const res = await fetch(`${API_URL}/books/${book.id}/stats`);
            const stats = await res.json();
            document.getElementById('modal-stats').innerHTML = `
                <span>⭐ Shared <strong>${stats.total_sends}</strong> times</span>
                <span style="margin-left: 1rem;">📖 <strong>${stats.unique_users}</strong> readers</span>
            `;
        } catch (e) {
            console.error(e);
        }
    }

    function closeAllModals() {
        emailModal.classList.remove('active');
        feedbackModal.classList.remove('active');
        window.history.replaceState(null, null, ' '); // Clear hash
    }

    // Deep Linking Support
    function checkDeepLink() {
        const hash = window.location.hash;
        if (hash.startsWith('#book-')) {
            const id = parseInt(hash.replace('#book-', ''));
            const book = allBooks.find(b => b.id === id);
            if (book) openBookModal(book);
        }
    }

    // Share Functionality
    shareBookBtn.addEventListener('click', () => {
        const url = `${window.location.origin}${window.location.pathname}#book-${currentBookId}`;
        navigator.clipboard.writeText(url).then(() => {
            showToast('Link copied to clipboard! ✨');
        });
    });

    // Toast Notification
    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerText = message;
        toastContainer.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 400);
        }, 3000);
    }

    // --- Event Listeners ---

    // Toggle email form inside modal
    requestTriggerBtn.addEventListener('click', () => {
        actionArea.style.display = 'none';
        descriptionBox.style.display = 'none';
        emailFormContainer.style.display = 'block';
        document.getElementById('user-email').focus();
    });

    cancelEmailBtn.addEventListener('click', () => {
        emailFormContainer.style.display = 'none';
        descriptionBox.style.display = 'block';
        actionArea.style.display = 'block';
        document.getElementById('send-status').innerText = '';
    });

    // Navigation & Controls
    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) {
            backToTopBtn.style.display = 'flex';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });

    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    searchTrigger.addEventListener('click', (e) => {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
        searchInput.focus();
    });

    feedbackTrigger.addEventListener('click', (e) => {
        e.preventDefault();
        feedbackModal.classList.add('active');
    });

    closeEmailModal.addEventListener('click', closeAllModals);
    closeFeedbackModal.addEventListener('click', closeAllModals);
    
    window.addEventListener('click', (e) => {
        if(e.target === emailModal || e.target === feedbackModal) closeAllModals();
    });

    searchInput.addEventListener('input', (e) => {
        const val = e.target.value.trim();
        renderBooks(allBooks.filter(b => 
            b.title.toLowerCase().includes(val.toLowerCase()) || 
            b.author.toLowerCase().includes(val.toLowerCase())
        ));
    });

    // Form Submissions
    emailForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('user-email').value;
        const msg = document.getElementById('send-status');

        msg.innerText = 'Delivering your book...';
        msg.style.color = 'var(--text-main)';

        try {
            const res = await fetch(`${API_URL}/books/${currentBookId}/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });

            if (res.ok) {
                msg.innerText = 'Success! Your book is on its way.';
                msg.style.color = 'var(--emerald-glow)';
                showToast('Book sent successfully! Check your inbox.');
            } else {
                const data = await res.json();
                msg.innerText = data.detail || 'Failed to deliver book.';
                msg.style.color = 'var(--danger)';
            }
        } catch (err) {
            msg.innerText = 'Network error. Please try again.';
            msg.style.color = 'var(--danger)';
        }
    });

    fbForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = document.getElementById('fb-message').value;
        const msgSpan = document.getElementById('fb-status');
        
        msgSpan.innerText = 'Sharing your thoughts...';
        msgSpan.style.color = 'var(--text-main)';

        try {
            const res = await fetch(`${API_URL}/feedback/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            if (res.ok) {
                msgSpan.innerText = 'Feedback shared. Thank you for your contribution!';
                msgSpan.style.color = 'var(--emerald-glow)';
                fbForm.reset();
                showToast('Feedback submitted! ✨');
                setTimeout(closeAllModals, 2000);
            }
        } catch(err) {
            msgSpan.innerText = 'Error sharing feedback.';
            msgSpan.style.color = 'var(--danger)';
        }
    });

    // Init
    loadBooks();
});
