const API_URL = '/api';

document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const appContainer = document.querySelector('.app-container');
    const searchInput = document.getElementById('search-input');
    const booksGrid = document.getElementById('books-grid');
    const toastContainer = document.getElementById('toast-container');
    
    // Page View Elements
    const bookDetailsView = document.getElementById('book-details-view');
    const backToLibraryBtn = document.getElementById('back-to-library');
    const shareBookBtn = document.getElementById('share-book-page-btn');
    
    const pageCover = document.getElementById('page-book-cover');
    const pageTitle = document.getElementById('page-book-title');
    const pageAuthor = document.getElementById('page-book-author');
    const pageDescription = document.getElementById('page-book-description');
    const heroBgBlur = document.getElementById('hero-bg-blur');
    
    const requestPageBtn = document.getElementById('page-request-trigger-btn');
    const emailPageContainer = document.getElementById('page-email-container');
    const emailPageForm = document.getElementById('page-email-form');
    const cancelPageEmailBtn = document.getElementById('page-cancel-email-btn');
    
    // Feedback Modal (Still a modal as it's a utility)
    const feedbackModal = document.getElementById('feedback-modal');
    const closeFeedbackModal = document.getElementById('close-feedback-modal');
    const fbForm = document.getElementById('feedback-form');
    
    // Controls
    const backToTopBtn = document.getElementById('back-to-top-btn');
    const searchTrigger = document.getElementById('nav-search-trigger');
    const feedbackTrigger = document.getElementById('nav-feedback-trigger');
    
    let currentBookId = null;
    let allBooks = [];

    // --- Core Functions ---

    async function loadBooks(query = '') {
        try {
            const res = await fetch(`${API_URL}/books?search=${encodeURIComponent(query)}`);
            if (!res.ok) throw new Error(`Server error: ${res.status}`);
            allBooks = await res.json();

            renderBooks(allBooks);
            checkDeepLink(); 
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
            card.addEventListener('click', () => navigateToBook(book));
            booksGrid.appendChild(card);
        });
    }

    // Navigation Logic
    function navigateToBook(book) {
        window.history.pushState({ bookId: book.id }, book.title, `#book-${book.id}`);
        openBookPage(book);
    }

    function openBookPage(book) {
        currentBookId = book.id;
        pageTitle.innerText = book.title;
        pageAuthor.innerText = book.author || 'Unknown Author';
        pageDescription.innerText = book.description || "In the quiet corners of this library, a story waits to be discovered. This volume promises a journey beyond the ordinary.";
        
        // Reset state
        document.getElementById('page-send-status').innerText = '';
        document.getElementById('page-user-email').value = '';
        emailPageContainer.style.display = 'none';
        requestPageBtn.parentElement.style.display = 'block';

        if (book.cover_filepath) {
            const coverUrl = `/api/${book.cover_filepath}`;
            pageCover.src = coverUrl;
            heroBgBlur.style.backgroundImage = `url(${coverUrl})`;
        } else {
            pageCover.src = '';
            heroBgBlur.style.backgroundImage = 'none';
        }
        
        // Switch Views
        document.body.classList.add('details-active');
        bookDetailsView.style.display = 'flex';
        window.scrollTo(0, 0);

        // Fetch Stats
        updateStats(book.id);
    }

    async function updateStats(bookId) {
        try {
            const res = await fetch(`${API_URL}/books/${bookId}/stats`);
            const stats = await res.json();
            document.getElementById('page-stats').innerHTML = `
                <span>⭐ Shared <strong>${stats.total_sends}</strong> times</span>
                <span style="margin-left: 1rem;">📖 <strong>${stats.unique_users}</strong> readers</span>
            `;
        } catch (e) { console.error(e); }
    }

    function closeBookPage() {
        document.body.classList.remove('details-active');
        bookDetailsView.style.display = 'none';
        currentBookId = null;
    }

    // Deep Linking & History
    function checkDeepLink() {
        const hash = window.location.hash;
        if (hash.startsWith('#book-')) {
            const id = parseInt(hash.replace('#book-', ''));
            const book = allBooks.find(b => b.id === id);
            if (book) openBookPage(book);
        }
    }

    window.addEventListener('popstate', (event) => {
        if (window.location.hash.startsWith('#book-')) {
            checkDeepLink();
        } else {
            closeBookPage();
        }
    });

    // --- Interactive Events ---

    backToLibraryBtn.addEventListener('click', () => {
        window.history.pushState(null, '', window.location.pathname);
        closeBookPage();
    });

    shareBookBtn.addEventListener('click', () => {
        const url = window.location.href;
        navigator.clipboard.writeText(url).then(() => {
            showToast('Link to this page copied! ✨');
        });
    });

    requestPageBtn.addEventListener('click', () => {
        requestPageBtn.parentElement.style.display = 'none';
        emailPageContainer.style.display = 'block';
        document.getElementById('page-user-email').focus();
    });

    cancelPageEmailBtn.addEventListener('click', () => {
        emailPageContainer.style.display = 'none';
        requestPageBtn.parentElement.style.display = 'block';
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

    // Search & Misc
    searchInput.addEventListener('input', (e) => {
        const val = e.target.value.trim();
        renderBooks(allBooks.filter(b => 
            b.title.toLowerCase().includes(val.toLowerCase()) || 
            b.author.toLowerCase().includes(val.toLowerCase())
        ));
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

    closeFeedbackModal.addEventListener('click', () => feedbackModal.classList.remove('active'));
    
    window.addEventListener('click', (e) => {
        if(e.target === feedbackModal) feedbackModal.classList.remove('active');
    });

    // Forms
    emailPageForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('page-user-email').value;
        const msg = document.getElementById('page-send-status');

        msg.innerText = 'Delivering your volume...';
        try {
            const res = await fetch(`${API_URL}/books/${currentBookId}/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });

            if (res.ok) {
                msg.innerText = 'Success! Your book is on its way.';
                msg.style.color = 'var(--emerald-glow)';
                showToast('Volume sent successfully! ✨');
            } else {
                const data = await res.json();
                msg.innerText = data.detail || 'Failed to deliver.';
                msg.style.color = 'var(--danger)';
            }
        } catch (err) {
            msg.innerText = 'Network error.';
        }
    });

    fbForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = document.getElementById('fb-message').value;
        const msgSpan = document.getElementById('fb-status');
        msgSpan.innerText = 'Submitting...';
        try {
            const res = await fetch(`${API_URL}/feedback/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            if (res.ok) {
                msgSpan.innerText = 'Thank you! Your feedback has been shared.';
                fbForm.reset();
                showToast('Feedback submitted! ✨');
                setTimeout(() => feedbackModal.classList.remove('active'), 2000);
            }
        } catch(err) { msgSpan.innerText = 'Error submitting feedback.'; }
    });

    loadBooks();
});
