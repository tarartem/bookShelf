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
    
    // Carousel Elements
    const carouselTrack = document.getElementById('carousel-track');
    const carouselDots = document.getElementById('carousel-dots');
    
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
    const pageStatusCard = document.getElementById('page-status-card');
    
    // Feedback Modal
    const feedbackModal = document.getElementById('feedback-modal');
    const closeFeedbackModal = document.getElementById('close-feedback-modal');
    const fbForm = document.getElementById('feedback-form');
    
    // Nav Controls
    const searchTrigger = document.getElementById('nav-search-trigger');
    const feedbackTriggerMobile = document.getElementById('nav-feedback-trigger');
    const feedbackTriggerFloating = document.getElementById('floating-feedback-btn');
    const homeTrigger = document.getElementById('nav-home');
    
    let currentBookId = null;
    let allBooks = [];
    let carouselIndex = 0;
    
    // Multi-select Author Filter
    let activeAuthorFilters = new Set();

    // --- Localization ---

    function t(key) {
        return translations[currentLang][key] || key;
    }

    function applyLanguage() {
        if(document.getElementById('txt-app-name')) document.getElementById('txt-app-name').innerText = t('appName');
        if(document.getElementById('txt-nav-home')) document.getElementById('txt-nav-home').innerText = t('navHome');
        if(document.getElementById('txt-nav-search')) document.getElementById('txt-nav-search').innerText = t('navSearch');
        if(document.getElementById('txt-nav-feedback')) document.getElementById('txt-nav-feedback').innerText = t('navFeedback');
        if(document.getElementById('txt-loading')) document.getElementById('txt-loading').innerText = t('curatingLibrary');
        if(document.getElementById('txt-welcome-title')) document.getElementById('txt-welcome-title').innerText = t('welcomeTitle');
        if(document.getElementById('txt-welcome-subtitle')) document.getElementById('txt-welcome-subtitle').innerText = t('welcomeSubtitle');
        if(document.getElementById('txt-welcome-extra')) document.getElementById('txt-welcome-extra').innerText = t('welcomeExtra');
        if(document.getElementById('txt-footer-crafting')) document.getElementById('txt-footer-crafting').innerText = t('footerCrafting');
        if(document.getElementById('txt-footer-admin')) document.getElementById('txt-footer-admin').innerText = t('footerAdmin');
        
        if(document.getElementById('txt-reset-filters')) document.getElementById('txt-reset-filters').innerText = t('resetFilters');
        if (toggleFiltersBtn) toggleFiltersBtn.innerText = t('findByAuthor');
        
        if (searchInputDesktop) searchInputDesktop.placeholder = t('placeholderSearch');
        if (searchInputMobile) searchInputMobile.placeholder = t('placeholderSearch');

        if(backToLibraryBtn) backToLibraryBtn.innerText = t('backToLibrary');
        if(requestPageBtn) requestPageBtn.innerText = t('getThisBook');
        if(shareBookBtn) shareBookBtn.innerText = t('share');
        
        if(document.getElementById('txt-secure-delivery')) document.getElementById('txt-secure-delivery').innerText = t('secureDelivery');
        if(document.getElementById('txt-delivery-hint')) document.getElementById('txt-delivery-hint').innerText = t('deliveryHint');
        if(document.getElementById('txt-deliver-now')) document.getElementById('txt-deliver-now').innerText = t('deliverNow');
        if(cancelPageEmailBtn) cancelPageEmailBtn.innerText = t('cancel');

        if(document.getElementById('txt-feedback-title')) document.getElementById('txt-feedback-title').innerText = t('feedbackTitle');
        if(document.getElementById('txt-feedback-subtitle')) document.getElementById('txt-feedback-subtitle').innerText = t('feedbackSubtitle');
        if(document.getElementById('fb-message')) document.getElementById('fb-message').placeholder = t('feedbackPlaceholder');
        if(document.getElementById('txt-submit-feedback')) document.getElementById('txt-submit-feedback').innerText = t('submitFeedback');
    }

    // --- Core Functions ---

    const lazyObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                lazyObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    async function loadBooks(query = '') {
        try {
            const res = await fetch(`${API_URL}/books?search=${encodeURIComponent(query)}`);
            if (!res.ok) throw new Error(`Server error: ${res.status}`);
            allBooks = await res.json();

            renderBooks(allBooks);
            renderAuthorFilters(allBooks);
            if (!query) renderCarousel(allBooks); 
            checkDeepLink(); 
        } catch (e) {
            booksGrid.innerHTML = `<p style="color:var(--danger); grid-column: 1/-1; text-align: center;">${e.message}</p>`;
        }
    }

    function renderBooks(books) {
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
            card.className = 'book-card lazy-load-item';
            if (index % 7 === 0) card.classList.add('bento-featured');
            
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
            lazyObserver.observe(card);
        });
    }

    function renderAuthorFilters(books) {
        const authors = [...new Set(books.map(b => b.author).filter(Boolean))].sort();
        authorFilterContainer.innerHTML = '';
        
        authors.forEach(author => {
            const pill = document.createElement('div');
            pill.className = `author-pill ${activeAuthorFilters.has(author) ? 'active' : ''}`;
            pill.innerText = author;
            pill.onclick = () => {
                if (activeAuthorFilters.has(author)) {
                    activeAuthorFilters.delete(author);
                } else {
                    activeAuthorFilters.add(author);
                }
                updateFilterUI(books);
            };
            authorFilterContainer.appendChild(pill);
        });
        
        updateResetBtn();
    }

    function updateFilterUI(books) {
        renderAuthorFilters(books);
        renderBooks(books);
    }

    function updateResetBtn() {
        if (resetFiltersBtn) {
            if (activeAuthorFilters.size > 0) {
                resetFiltersBtn.style.display = 'block';
            } else {
                resetFiltersBtn.style.display = 'none';
            }
        }
    }

    function resetAppView() {
        activeAuthorFilters.clear();
        if (searchInputDesktop) searchInputDesktop.value = '';
        if (searchInputMobile) searchInputMobile.value = '';
        closeBookPage();
        updateFilterUI(allBooks);
        if (toggleFiltersBtn) toggleFiltersBtn.classList.remove('active');
        if (authorFilterContainer) authorFilterContainer.classList.remove('active');
        if (mobileSearchOverlay) mobileSearchOverlay.classList.remove('active');
        if (feedbackModal) feedbackModal.classList.remove('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    if (resetFiltersBtn) {
        resetFiltersBtn.onclick = () => {
            activeAuthorFilters.clear();
            updateFilterUI(allBooks);
        };
    }

    if (toggleFiltersBtn) {
        toggleFiltersBtn.onclick = () => {
            const isActive = authorFilterContainer.classList.toggle('active');
            toggleFiltersBtn.classList.toggle('active', isActive);
        };
    }

    if (headerLogo) {
        headerLogo.onclick = () => {
            resetAppView();
        }
    }

    // Search Logic
    const handleSearch = (e) => {
        const val = e.target.value.trim().toLowerCase();
        if (!val) {
            renderBooks(allBooks);
            return;
        }
        const filtered = allBooks.filter(b => {
            return b.title.toLowerCase().includes(val) || (b.author || '').toLowerCase().includes(val);
        });
        renderBooks(filtered);
    };

    if (searchInputDesktop) searchInputDesktop.addEventListener('input', handleSearch);
    if (searchInputMobile) searchInputMobile.addEventListener('input', handleSearch);

    // Mobile Search Overlay Logic
    if (searchTrigger) {
        searchTrigger.addEventListener('click', (e) => {
            e.preventDefault();
            if(mobileSearchOverlay) {
                mobileSearchOverlay.classList.add('active');
                setTimeout(() => { if(searchInputMobile) searchInputMobile.focus(); }, 400);
            }
        });
    }

    if (closeSearchOverlay) {
        closeSearchOverlay.addEventListener('click', () => {
            if(mobileSearchOverlay) mobileSearchOverlay.classList.remove('active');
        });
    }

    if (mobileSearchOverlay) {
        mobileSearchOverlay.addEventListener('click', (e) => {
            if (e.target === mobileSearchOverlay) {
                mobileSearchOverlay.classList.remove('active');
            }
        });
    }

    function renderCarousel(books) {
        if (!carouselTrack || books.length === 0) return;
        
        const shuffled = [...books].sort(() => 0.5 - Math.random());
        const featured = shuffled.slice(0, 5); 
        
        carouselTrack.innerHTML = '';
        carouselDots.innerHTML = '';

        featured.forEach((book, i) => {
            const item = document.createElement('div');
            item.className = 'carousel-item';
            const coverUrl = book.cover_filepath ? `/api/${book.cover_filepath}` : '';

            item.innerHTML = `
                <div class="carousel-info">
                    <span class="badge">${t('featuredVolume')}</span>
                    <h2>${book.title}</h2>
                    <p class="book-author">${book.author || 'Unknown Author'}</p>
                </div>
                <div class="carousel-cover-side">
                   ${coverUrl ? `<img src="${coverUrl}" alt="${book.title}">` : ''}
                </div>
            `;
            item.addEventListener('click', () => navigateToBook(book));
            carouselTrack.appendChild(item);

            const dot = document.createElement('div');
            dot.className = `dot ${i === 0 ? 'active' : ''}`;
            dot.addEventListener('click', () => setCarousel(i));
            carouselDots.appendChild(dot);
        });

        if (window.carouselTimer) clearInterval(window.carouselTimer);
        window.carouselTimer = setInterval(() => {
            carouselIndex = (carouselIndex + 1) % featured.length;
            setCarousel(carouselIndex);
        }, 5000);
    }

    function setCarousel(index) {
        if(!carouselTrack) return;
        carouselIndex = index;
        carouselTrack.style.transform = `translateX(-${index * 100}%)`;
        const dots = document.querySelectorAll('.dot');
        dots.forEach((d, i) => d.classList.toggle('active', i === index));
    }

    function navigateToBook(book) {
        window.history.pushState({ bookId: book.id }, book.title, `#book-${book.id}`);
        openBookPage(book);
    }

    function openBookPage(book) {
        currentBookId = book.id;
        pageTitle.innerText = book.title;
        pageAuthor.innerText = book.author || 'Unknown Author';
        pageDescription.innerText = book.description || (currentLang === 'uk' ? "Опис відсутній." : "No description available.");
        
        bookDetailsView.scrollTo(0, 0);
        pageStatusCard.style.display = 'none';
        emailPageContainer.style.display = 'none';
        requestPageBtn.style.display = 'block';

        if (book.cover_filepath) {
            const coverUrl = `/api/${book.cover_filepath}`;
            pageCover.src = coverUrl;
            heroBgBlur.style.backgroundImage = `url(${coverUrl})`;
        } else {
            pageCover.src = '';
            heroBgBlur.style.backgroundImage = 'none';
        }
        
        document.body.classList.add('details-active');
        bookDetailsView.style.display = 'flex';
        updateStats(book.id);
    }

    async function updateStats(bookId) {
        try {
            const res = await fetch(`${API_URL}/books/${bookId}/stats`);
            const stats = await res.json();
            const shareTxt = currentLang === 'uk' ? 'Поділилися' : 'Shared';
            const readersTxt = currentLang === 'uk' ? 'читачів' : 'readers';
            document.getElementById('page-stats').innerHTML = `
                <span>⭐ ${shareTxt} <strong>${stats.total_sends}</strong></span>
                <span style="margin-left: 1rem;">📖 <strong>${stats.unique_users}</strong> ${readersTxt}</span>
            `;
        } catch (e) { console.error(e); }
    }

    function closeBookPage() {
        if(bookDetailsView) {
            document.body.classList.remove('details-active');
            bookDetailsView.style.display = 'none';
        }
        currentBookId = null;
    }

    function checkDeepLink() {
        const hash = window.location.hash;
        if (hash.startsWith('#book-')) {
            const id = parseInt(hash.replace('#book-', ''));
            const book = allBooks.find(b => b.id === id);
            if (book) openBookPage(book);
        }
    }

    window.addEventListener('popstate', () => {
        if (window.location.hash.startsWith('#book-')) {
            checkDeepLink();
        } else {
            closeBookPage();
        }
    });

    if(backToLibraryBtn) {
        backToLibraryBtn.addEventListener('click', () => {
            window.history.pushState(null, '', window.location.pathname);
            closeBookPage();
        });
    }

    if(shareBookBtn) {
        shareBookBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(window.location.href).then(() => {
                showToast(t('linkCopied'));
            });
        });
    }

    if(requestPageBtn) {
        requestPageBtn.addEventListener('click', () => {
            requestPageBtn.style.display = 'none';
            emailPageContainer.style.display = 'block';
            if(document.getElementById('page-user-email')) document.getElementById('page-user-email').focus();
        });
    }

    if(cancelPageEmailBtn) {
        cancelPageEmailBtn.addEventListener('click', () => {
            emailPageContainer.style.display = 'none';
            requestPageBtn.style.display = 'block';
            bookDetailsView.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    function showToast(message) {
        if(!toastContainer) return;
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerText = message;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 400);
        }, 3000);
    }

    if(emailPageForm) {
        emailPageForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const emailField = document.getElementById('page-user-email');
            if(!emailField) return;
            const email = emailField.value;
            const submitBtn = emailPageForm.querySelector('button[type="submit"]');

            if(submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerText = t('deliveringVolume');
            }

            try {
                const res = await fetch(`${API_URL}/books/${currentBookId}/send`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email })
                });

                if (res.ok) {
                    emailPageContainer.style.display = 'none';
                    pageStatusCard.innerHTML = `
                        <h4>${t('successfullyDispatched')}</h4>
                        <p>${t('dispatchHint')} <strong>${email}</strong>${t('dispatchHintEnd')}</p>
                    `;
                    pageStatusCard.style.display = 'block';
                    showToast(t('bookSent'));
                } else {
                    const data = await res.json();
                    alert(data.detail || 'Error');
                    if(submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerText = t('deliverNow');
                    }
                }
            } catch (err) {
                if(submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerText = t('deliverNow');
                }
            }
        });
    }

    if(fbForm) {
        fbForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const msgField = document.getElementById('fb-message');
            if(!msgField) return;
            const message = msgField.value;
            try {
                const res = await fetch(`${API_URL}/feedback/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                if (res.ok) {
                    fbForm.reset();
                    showToast(t('feedbackSubmitted'));
                    if(feedbackModal) feedbackModal.classList.remove('active');
                }
            } catch(err) { console.error(err); }
        });
    }

    if (homeTrigger) {
        homeTrigger.onclick = (e) => {
            e.preventDefault();
            resetAppView();
        };
    }

    const openFeedback = (e) => {
        e.preventDefault();
        if(feedbackModal) feedbackModal.classList.add('active');
    };

    if (feedbackTriggerMobile) feedbackTriggerMobile.onclick = openFeedback;
    if (feedbackTriggerFloating) feedbackTriggerFloating.onclick = openFeedback;

    if(closeFeedbackModal) closeFeedbackModal.onclick = () => { if(feedbackModal) feedbackModal.classList.remove('active'); };
    
    if(feedbackModal) {
        feedbackModal.addEventListener('click', (e) => {
            if (e.target === feedbackModal) {
                feedbackModal.classList.remove('active');
            }
        });
    }

    applyLanguage(); 
    loadBooks();
});
