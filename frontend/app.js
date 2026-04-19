import { translations } from './translations.js';

const API_URL = '/api';
let currentLang = 'uk'; 

document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const searchInputDesktop = document.getElementById('search-input-desktop');
    const searchInputMobile = document.getElementById('search-input-mobile');
    const booksGrid = document.getElementById('books-grid');
    const toastContainer = document.getElementById('toast-container');
    const authorFilterContainer = document.getElementById('author-filter-container');
    const resetFiltersBtn = document.getElementById('reset-filters-btn');
    const toggleFiltersBtn = document.getElementById('toggle-author-filters-btn');
    const headerLogo = document.getElementById('header-logo');
    
    const mobileSearchOverlay = document.getElementById('mobile-search-overlay');
    const closeSearchOverlay = document.getElementById('close-search-overlay');
    
    // Feedback Modal
    const feedbackModal = document.getElementById('feedback-modal');
    const closeFeedbackModal = document.getElementById('close-feedback-modal');
    const fbForm = document.getElementById('feedback-form');
    
    // Page View Elements
    const bookDetailsView = document.getElementById('book-details-view');
    const backToLibraryBtn = document.getElementById('back-to-library');
    const shareBookBtn = document.getElementById('share-book-page-btn');
    
    // Nav Controls
    const searchTrigger = document.getElementById('nav-search-trigger');
    const feedbackTriggerMobile = document.getElementById('nav-feedback-trigger');
    const feedbackTriggerFloating = document.getElementById('floating-feedback-btn');
    const homeTrigger = document.getElementById('nav-home');
    
    let allBooks = [];
    let activeAuthorFilters = new Set();
    let currentBookId = null;

    // --- Localization ---
    function t(key) { return translations[currentLang][key] || key; }

    function applyLanguage() {
        const ids = [
            'txt-app-name', 'txt-nav-home', 'txt-nav-search', 'txt-nav-feedback',
            'txt-loading', 'txt-welcome-title', 'txt-welcome-subtitle', 'txt-welcome-extra',
            'txt-footer-crafting', 'txt-footer-admin', 'txt-reset-filters',
            'txt-feedback-title', 'txt-feedback-subtitle', 'txt-submit-feedback'
        ];
        ids.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerText = t(id.replace('txt-', '').replace(/-([a-z])/g, (g) => g[1].toUpperCase()));
        });

        // Special mappings for non-standard txt IDs
        if(document.getElementById('txt-reset-filters')) document.getElementById('txt-reset-filters').innerText = t('resetFilters');
        if(toggleFiltersBtn) toggleFiltersBtn.innerText = t('findByAuthor');
        if(searchInputDesktop) searchInputDesktop.placeholder = t('placeholderSearch');
        if(searchInputMobile) searchInputMobile.placeholder = t('placeholderSearch');
        if(document.getElementById('fb-message')) document.getElementById('fb-message').placeholder = t('feedbackPlaceholder');
    }

    // --- Core Data Logic ---
    async function loadBooks(query = '') {
        try {
            const res = await fetch(`${API_URL}/books?search=${encodeURIComponent(query)}`);
            if (!res.ok) throw new Error(`Server error: ${res.status}`);
            allBooks = await res.json();
            renderBooks(allBooks);
            renderAuthorFilters(allBooks);
            renderCarousel(allBooks);
            checkDeepLink();
        } catch (e) {
            if(booksGrid) booksGrid.innerHTML = `<p style="color:var(--danger); grid-column: 1/-1; text-align: center;">${e.message}</p>`;
        }
    }

    function renderBooks(books) {
        if(!booksGrid) return;
        booksGrid.innerHTML = '';
        const filtered = activeAuthorFilters.size > 0 
            ? books.filter(b => activeAuthorFilters.has(b.author))
            : books;

        if (filtered.length === 0) {
            booksGrid.innerHTML = `<p style="color:var(--text-dim); grid-column: 1/-1; text-align: center; padding: 4rem;">${t('noResults')}</p>`;
            return;
        }

        filtered.forEach((book, index) => {
            const card = document.createElement('div');
            card.className = 'book-card';
            card.innerHTML = `
                <div class="book-cover-wrapper">
                    ${book.cover_filepath ? `<img src="/api/${book.cover_filepath}" alt="${book.title}" loading="lazy">` : `<div style="height:100%; display:flex; align-items:center; justify-content:center; background:#000;">📖</div>`}
                </div>
                <h3 class="book-title">${book.title}</h3>
                <p class="book-author">${book.author || 'Unknown'}</p>
            `;
            card.onclick = () => openBookPage(book);
            booksGrid.appendChild(card);
        });
    }

    function renderAuthorFilters(books) {
        if(!authorFilterContainer) return;
        const authors = [...new Set(books.map(b => b.author).filter(Boolean))].sort();
        authorFilterContainer.innerHTML = '';
        authors.forEach(author => {
            const pill = document.createElement('div');
            pill.className = `author-pill ${activeAuthorFilters.has(author) ? 'active' : ''}`;
            pill.innerText = author;
            pill.onclick = () => {
                if (activeAuthorFilters.has(author)) activeAuthorFilters.delete(author);
                else activeAuthorFilters.add(author);
                renderAuthorFilters(books);
                renderBooks(books);
                if(resetFiltersBtn) resetFiltersBtn.style.display = activeAuthorFilters.size > 0 ? 'block' : 'none';
            };
            authorFilterContainer.appendChild(pill);
        });
    }

    // --- Search Handling ---
    const handleSearch = (e) => {
        const val = e.target.value.trim().toLowerCase();
        const filtered = allBooks.filter(b => b.title.toLowerCase().includes(val) || (b.author || '').toLowerCase().includes(val));
        renderBooks(filtered);
    };

    if (searchInputDesktop) searchInputDesktop.addEventListener('input', handleSearch);
    if (searchInputMobile) searchInputMobile.addEventListener('input', handleSearch);

    if (searchTrigger) {
        searchTrigger.onclick = (e) => {
            e.preventDefault();
            if(mobileSearchOverlay) {
                mobileSearchOverlay.classList.add('active');
                setTimeout(() => { if(searchInputMobile) searchInputMobile.focus(); }, 300);
            }
        };
    }

    if(closeSearchOverlay) closeSearchOverlay.onclick = () => mobileSearchOverlay.classList.remove('active');
    if(mobileSearchOverlay) mobileSearchOverlay.onclick = (e) => { if(e.target === mobileSearchOverlay) mobileSearchOverlay.classList.remove('active'); };

    // --- Navigation & Clicks ---
    function resetAppView() {
        activeAuthorFilters.clear();
        if(searchInputDesktop) searchInputDesktop.value = '';
        if(searchInputMobile) searchInputMobile.value = '';
        if(mobileSearchOverlay) mobileSearchOverlay.classList.remove('active');
        if(feedbackModal) feedbackModal.classList.remove('active');
        if(resetFiltersBtn) resetFiltersBtn.style.display = 'none';
        closeBookPage();
        renderBooks(allBooks);
        renderAuthorFilters(allBooks);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    if(headerLogo) headerLogo.onclick = resetAppView;
    if(homeTrigger) homeTrigger.onclick = (e) => { e.preventDefault(); resetAppView(); };
    if(resetFiltersBtn) resetFiltersBtn.onclick = () => { activeAuthorFilters.clear(); resetFiltersBtn.style.display = 'none'; renderAuthorFilters(allBooks); renderBooks(allBooks); };

    const toggleFB = (e) => { e.preventDefault(); if(feedbackModal) feedbackModal.classList.add('active'); };
    if(feedbackTriggerMobile) feedbackTriggerMobile.onclick = toggleFB;
    if(feedbackTriggerFloating) feedbackTriggerFloating.onclick = toggleFB;
    if(closeFeedbackModal) closeFeedbackModal.onclick = () => feedbackModal.classList.remove('active');
    if(feedbackModal) feedbackModal.onclick = (e) => { if(e.target === feedbackModal) feedbackModal.classList.remove('active'); };

    // --- Book Details ---
    function openBookPage(book) {
        currentBookId = book.id;
        document.getElementById('page-book-title').innerText = book.title;
        document.getElementById('page-book-author').innerText = book.author || 'Unknown';
        document.getElementById('page-book-description').innerText = book.description || 'No description.';
        if(book.cover_filepath) document.getElementById('page-book-cover').src = `/api/${book.cover_filepath}`;
        
        bookDetailsView.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    function closeBookPage() {
        if(bookDetailsView) bookDetailsView.style.display = 'none';
        document.body.style.overflow = 'auto';
        currentBookId = null;
    }

    if(backToLibraryBtn) backToLibraryBtn.onclick = closeBookPage;

    // --- Feedback ---
    if(fbForm) {
        fbForm.onsubmit = async (e) => {
            e.preventDefault();
            const message = document.getElementById('fb-message').value;
            try {
                const res = await fetch(`${API_URL}/feedback/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                if(res.ok) { showToast(t('feedbackSubmitted')); fbForm.reset(); feedbackModal.classList.remove('active'); }
            } catch(e) {}
        };
    }

    function showToast(msg) {
        if(!toastContainer) return;
        const t = document.createElement('div');
        t.innerText = msg; t.className = 'toast';
        toastContainer.appendChild(t);
        setTimeout(() => t.remove(), 3000);
    }

    // Carousel Dummy
    function renderCarousel() {
        const track = document.getElementById('carousel-track');
        if(track) track.innerHTML = '<div class="carousel-item" style="justify-content:center;"><h2>Explore our curated collection</h2></div>';
    }

    function checkDeepLink() {
        const hash = window.location.hash;
        if (hash.startsWith('#book-')) {
            const id = parseInt(hash.replace('#book-', ''));
            const book = allBooks.find(b => b.id === id);
            if (book) openBookPage(book);
        }
    }

    applyLanguage();
    loadBooks();
});
