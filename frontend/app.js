import { translations } from './translations.js';

const API_URL = '/api';
let currentLang = localStorage.getItem('lang') || 'uk';
let currentUser = null;
let userLibrary = []; // IDs of unlocked books
let allBooks = [];
let activeAuthorFilters = new Set();
let carouselIndex = 0;

document.addEventListener('DOMContentLoaded', () => {
    console.log("DEBUG: App initializing...");
    init();
});

async function init() {
    loadLanguage();
    await loadUser();
    await loadLibrary();
    await loadBooks();
    setupEventListeners();
    handleRouting();
    console.log("DEBUG: App initialized.");
}

function loadLanguage() {
    currentLang = localStorage.getItem('lang') || 'uk';
    document.documentElement.lang = currentLang;
    applyLanguage();
}

async function loadUser() {
    const token = localStorage.getItem('token');
    if (!token) {
        console.log("DEBUG: No token found.");
        return;
    }
    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            currentUser = await response.json();
            console.log("DEBUG: User loaded:", currentUser.email);
            updateUIForUser();
        } else {
            console.warn("DEBUG: Token invalid, clearing.");
            localStorage.removeItem('token');
        }
    } catch (error) {
        console.error('DEBUG: Error loading user:', error);
    }
}

async function loadLibrary() {
    const token = localStorage.getItem('token');
    if (!token || !currentUser) return;
    try {
        const response = await fetch(`${API_URL}/books/library`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            userLibrary = await response.json();
            console.log("DEBUG: User library loaded:", userLibrary.length, "books");
        }
    } catch (error) {
        console.error('DEBUG: Error loading library:', error);
    }
}

async function loadBooks() {
    const booksGrid = document.getElementById('books-grid');
    if (booksGrid) booksGrid.innerHTML = `<div class="loading-state">${t('curatingLibrary')}</div>`;

    try {
        const response = await fetch(`${API_URL}/books/`);
        if (response.ok) {
            allBooks = await response.json();
            console.log("DEBUG: Books loaded:", allBooks.length);
            renderBooks(allBooks);
            renderFeaturedCarousel(allBooks);
            renderAuthorFilters(allBooks);
        } else {
            console.error("DEBUG: Failed to load books, status:", response.status);
        }
    } catch (error) {
        console.error('DEBUG: Error loading books:', error);
    }
}

function t(key) {
    return translations[currentLang][key] || key;
}

function applyLanguage() {
    const idsAndKeys = {
        'brand-title': 'appName',
        'txt-nav-home': 'navHome',
        'txt-nav-search': 'navSearch',
        'txt-nav-feedback': 'navFeedback',
        'txt-welcome-title': 'welcomeTitle',
        'txt-welcome-subtitle': 'welcomeSubtitle',
        'txt-welcome-extra': 'welcomeExtra',
        'txt-reset-filters': 'resetFilters',
        'txt-secure-delivery': 'secureDelivery',
        'txt-delivery-hint': 'deliveryHint',
        'txt-deliver-now': 'deliverNow',
        'txt-feedback-title': 'feedbackTitle',
        'txt-feedback-subtitle': 'feedbackSubtitle',
        'txt-submit-feedback': 'submitFeedback',
        'txt-send-to-email': 'sendToEmail',
        'txt-download-epub': 'downloadEpub',
        'back-to-library': 'backToLibrary' // Directly on the button
    };

    for (const [id, key] of Object.entries(idsAndKeys)) {
        const el = document.getElementById(id);
        if (el) el.innerText = t(key);
    }
    
    // Update placeholders
    const searchInputMobile = document.getElementById('search-input-mobile');
    if (searchInputMobile) searchInputMobile.placeholder = t('placeholderSearch');
    
    const fbPlaceholder = document.getElementById('fb-message');
    if (fbPlaceholder) fbPlaceholder.placeholder = t('feedbackPlaceholder');
}

function updateUIForUser() {
    const profileTrigger = document.getElementById('profile-trigger');
    if (profileTrigger) {
        console.log("DEBUG: Updating profile icon UI, currentUser:", currentUser ? currentUser.email : "Guest");
        if (currentUser) {
            const initial = currentUser.email[0].toUpperCase();
            profileTrigger.innerHTML = `<div style="font-weight:700; color:var(--emerald-primary); font-size:1.1rem; width:100%; height:100%; display:flex; align-items:center; justify-content:center;">${initial}</div>`;
            profileTrigger.onclick = (e) => {
                console.log("DEBUG: Profile icon clicked (User)");
                window.location.href = '/profile.html';
            };
            profileTrigger.title = currentUser.email;
        } else {
            profileTrigger.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--emerald-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="pointer-events: none;">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                </svg>`;
            profileTrigger.onclick = (e) => {
                console.log("DEBUG: Profile icon clicked (Guest)");
                window.location.href = '/login.html';
            };
        }
    } else {
        console.warn("DEBUG: profile-trigger element not found in DOM");
    }
}

function renderBooks(books) {
    const grid = document.getElementById('books-grid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    if (books.length === 0) {
        grid.innerHTML = `<div class="no-results">${t('noResults')}</div>`;
        return;
    }

    books.forEach(book => {
        const card = document.createElement('div');
        card.className = 'book-card';
        card.innerHTML = `
            <div class="book-cover-wrapper">
                <img src="${book.cover_filepath || 'assets/default-cover.jpg'}" alt="${book.title}" loading="lazy">
            </div>
            <div class="book-info">
                <div class="book-title">${book.title}</div>
                <div class="book-author">${book.author}</div>
            </div>
        `;
        card.onclick = () => openBookDetails(book.id);
        grid.appendChild(card);
    });
}

function renderFeaturedCarousel(books) {
    const track = document.getElementById('carousel-track');
    const dots = document.getElementById('carousel-dots');
    if (!track || !dots || books.length === 0) return;

    const featured = books.slice(0, 5); // Take first 5 as featured
    track.innerHTML = '';
    dots.innerHTML = '';

    featured.forEach((book, idx) => {
        const item = document.createElement('div');
        item.className = 'carousel-item';
        item.innerHTML = `
            <div class="carousel-info">
                <span class="badge">${t('featuredVolume')}</span>
                <h2>${book.title}</h2>
                <p>${book.author}</p>
            </div>
            <div class="carousel-cover-side">
                <img src="${book.cover_filepath}" alt="">
            </div>
        `;
        item.onclick = () => openBookDetails(book.id);
        track.appendChild(item);

        const dot = document.createElement('div');
        dot.className = `dot ${idx === 0 ? 'active' : ''}`;
        dot.onclick = (e) => {
            e.stopPropagation();
            goToCarousel(idx);
        };
        dots.appendChild(dot);
    });
}

function goToCarousel(index) {
    const track = document.getElementById('carousel-track');
    const dots = document.querySelectorAll('.dot');
    if (!track) return;
    
    carouselIndex = index;
    track.style.transform = `translateX(-${index * 100}%)`;
    dots.forEach((d, i) => d.classList.toggle('active', i === index));
}

function renderAuthorFilters(books) {
    const container = document.getElementById('author-filter-container');
    if (!container) return;

    const authors = {};
    books.forEach(b => {
        authors[b.author] = (authors[b.author] || 0) + 1;
    });

    const sortedAuthors = Object.keys(authors).sort();
    container.innerHTML = '';
    
    sortedAuthors.forEach(author => {
        const pill = document.createElement('div');
        pill.className = `author-pill ${activeAuthorFilters.has(author) ? 'active' : ''}`;
        pill.innerHTML = `${author} <span class="author-count">${authors[author]}</span>`;
        pill.onclick = () => toggleAuthorFilter(author);
        container.appendChild(pill);
    });
}

function toggleAuthorFilter(author) {
    if (activeAuthorFilters.has(author)) {
        activeAuthorFilters.delete(author);
    } else {
        activeAuthorFilters.add(author);
    }
    
    const filtered = allBooks.filter(b => 
        activeAuthorFilters.size === 0 || activeAuthorFilters.has(b.author)
    );
    
    renderBooks(filtered);
    renderAuthorFilters(allBooks);
}

async function openBookDetails(bookId) {
    const book = allBooks.find(b => b.id === bookId);
    if (!book) return;

    console.log("DEBUG: Opening book details for ID:", bookId);
    document.body.classList.add('details-active');
    const view = document.getElementById('book-details-view');
    view.style.display = 'flex';
    view.scrollTop = 0;

    document.getElementById('page-book-cover').src = book.cover_filepath;
    document.getElementById('page-book-title').innerText = book.title;
    document.getElementById('page-book-author').innerText = book.author;
    document.getElementById('page-book-description').innerText = book.description || '';
    document.getElementById('hero-bg-blur').style.backgroundImage = `url(${book.cover_filepath})`;

    // Set share icon
    const shareBtn = document.getElementById('share-book-page-btn');
    if (shareBtn) {
        shareBtn.innerHTML = '🔗';
        shareBtn.onclick = () => {
            navigator.clipboard.writeText(window.location.href);
            showToast(t('linkCopied'));
        };
    }
    
    updateBookActionsUI(bookId);
    
    // Update URL without reload
    window.history.pushState({ bookId }, book.title, `?book=${bookId}`);
}

function updateBookActionsUI(bookId) {
    const isUnlocked = userLibrary.includes(bookId);
    const unlockBtn = document.getElementById('page-request-trigger-btn');
    const deliveryContainer = document.getElementById('page-delivery-container');

    if (isUnlocked) {
        if (unlockBtn) unlockBtn.style.display = 'none';
        if (deliveryContainer) deliveryContainer.style.display = 'block';
    } else {
        if (unlockBtn) {
            unlockBtn.style.display = 'flex';
            unlockBtn.style.alignItems = 'center';
            unlockBtn.style.justifyContent = 'center';
            unlockBtn.innerHTML = `<span>${t('unlockBook')} (1 ${t('credit')})</span>`;
            unlockBtn.onclick = () => handleUnlock(bookId);
        }
        if (deliveryContainer) deliveryContainer.style.display = 'none';
    }
}

async function handleUnlock(bookId) {
    const token = localStorage.getItem('token');
    if (!token) {
        showToast(t('loginToDownload'));
        setTimeout(() => window.location.href = '/login.html', 1500);
        return;
    }

    try {
        const response = await fetch(`${API_URL}/books/${bookId}/unlock`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            showToast(t('unlockSuccess'));
            userLibrary.push(bookId);
            updateBookActionsUI(bookId);
        } else {
            const error = await response.json();
            if (response.status === 402) {
                showToast(t('insufficientCredits'));
            } else {
                showToast(error.detail || 'Error');
            }
        }
    } catch (error) {
        console.error('Unlock error:', error);
    }
}

function setupEventListeners() {
    // Back button
    const backBtn = document.getElementById('back-to-library');
    if (backBtn) {
        backBtn.onclick = () => {
            document.body.classList.remove('details-active');
            document.getElementById('book-details-view').style.display = 'none';
            window.history.pushState({}, 'BookShelf', '/');
        };
    }

    // Reset Filters
    const resetBtn = document.getElementById('reset-filters-btn');
    if (resetBtn) {
        resetBtn.onclick = () => {
            activeAuthorFilters.clear();
            renderBooks(allBooks);
            renderAuthorFilters(allBooks);
        };
    }

    // Logo click to go home
    const logo = document.getElementById('header-logo');
    if (logo) {
        logo.onclick = () => {
            if (document.body.classList.contains('details-active')) {
                document.body.classList.remove('details-active');
                document.getElementById('book-details-view').style.display = 'none';
                window.history.pushState({}, 'BookShelf', '/');
            } else {
                window.location.href = '/';
            }
        };
    }

    // Search Mode
    const searchTrigger = document.getElementById('nav-search-trigger');
    if (searchTrigger) {
        searchTrigger.onclick = () => document.body.classList.add('search-active');
    }

    const cancelSearch = document.getElementById('cancel-search-btn');
    if (cancelSearch) {
        cancelSearch.onclick = () => {
            document.body.classList.remove('search-active');
            const input = document.getElementById('search-input-mobile');
            if (input) {
                input.value = '';
                renderBooks(allBooks);
            }
        };
    }

    const searchInputMobile = document.getElementById('search-input-mobile');
    if (searchInputMobile) {
        searchInputMobile.oninput = (e) => {
            const q = e.target.value.toLowerCase();
            const filtered = allBooks.filter(b => 
                b.title.toLowerCase().includes(q) || b.author.toLowerCase().includes(q)
            );
            renderBooks(filtered);
        };
    }

    // Download Logic
    const downloadBtn = document.getElementById('btn-download-epub');
    if (downloadBtn) {
        downloadBtn.onclick = async () => {
            const urlParams = new URLSearchParams(window.location.search);
            const bookId = urlParams.get('book');
            if (bookId) {
                window.location.href = `${API_URL}/books/download/${bookId}/user?token=${localStorage.getItem('token')}`;
            }
        };
    }

    // Email Form Toggle
    const toggleEmailBtn = document.getElementById('btn-toggle-email-form');
    if (toggleEmailBtn) {
        toggleEmailBtn.onclick = () => {
            const form = document.getElementById('page-email-form');
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
        };
    }

    // Email Dispatch
    const emailForm = document.getElementById('page-email-form');
    if (emailForm) {
        emailForm.onsubmit = async (e) => {
            e.preventDefault();
            const emailInput = document.getElementById('page-user-email');
            const email = emailInput ? emailInput.value : '';
            const urlParams = new URLSearchParams(window.location.search);
            const bookId = urlParams.get('book');
            const submitBtn = emailForm.querySelector('button[type="submit"]');
            
            if (!bookId) return;

            submitBtn.disabled = true;
            submitBtn.innerText = t('deliveringVolume');

            try {
                const response = await fetch(`${API_URL}/books/${bookId}/send?email=${encodeURIComponent(email)}`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                });

                if (response.ok) {
                    emailForm.style.display = 'none';
                    const statusCard = document.getElementById('page-status-card');
                    statusCard.style.display = 'block';
                    statusCard.innerHTML = `<div class="status-success">
                        <p>${t('successfullyDispatched')} ${email}</p>
                        <p>${t('checkInbox')}</p>
                    </div>`;
                    showToast(t('bookSent'));
                } else {
                    const err = await response.json();
                    alert(err.detail || 'Error');
                }
            } catch (err) {
                console.error(err);
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerText = t('deliverNow');
            }
        };
    }

    // Feedback
    const fbTrigger = document.getElementById('nav-feedback-trigger');
    if (fbTrigger) {
        fbTrigger.onclick = () => document.getElementById('feedback-modal').classList.add('active');
    }

    const closeFb = document.getElementById('close-feedback-modal');
    if (closeFb) {
        closeFb.onclick = () => document.getElementById('feedback-modal').classList.remove('active');
    }

    const fbForm = document.getElementById('feedback-form');
    if (fbForm) {
        fbForm.onsubmit = async (e) => {
            e.preventDefault();
            const message = document.getElementById('fb-message').value;
            try {
                const res = await fetch(`${API_URL}/feedback/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                if (res.ok) {
                    fbForm.reset();
                    showToast(t('feedbackSubmitted'));
                    document.getElementById('feedback-modal').classList.remove('active');
                }
            } catch (err) { console.error(err); }
        };
    }
}

function handleRouting() {
    const urlParams = new URLSearchParams(window.location.search);
    const bookId = urlParams.get('book');
    if (bookId) {
        openBookDetails(parseInt(bookId));
    }
}

function showToast(message) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerText = message;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}
