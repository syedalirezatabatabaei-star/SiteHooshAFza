/**
 * Header Component for هوش افزا
 */
const Header = (() => {
    function render() {
        const user = Auth.getUser();
        const isLoggedIn = Auth.isLoggedIn();

        return `
        <nav class="navbar" role="navigation" aria-label="منوی اصلی">
            <div class="container navbar-inner">
                <!-- Hamburger stays FIRST so in RTL it sits at the far RIGHT on mobile -->
                <button class="navbar-toggle" onclick="Header.toggleMobile()" aria-label="منو">
                    ☰
                </button>
                <a href="/" class="navbar-brand" aria-label="هوش افزا — صفحه اصلی">
                    <img src="/assets/images/logo.jpg" alt="لوگوی هوش افزا" class="navbar-logo" width="40" height="40">
                    <span class="navbar-brand-text">هوش افزا</span>
                </a>

                <div class="navbar-menu">
                    <a href="/" class="navbar-link">خانه</a>
                    <a href="/pages/courses.html" class="navbar-link">دوره‌ها</a>
                    <div class="navbar-category" id="navbarCategory">
                        <a href="/pages/courses.html" class="navbar-link navbar-category-trigger" aria-haspopup="true" aria-expanded="false" id="navbarCategoryTrigger">
                            حوزه‌های آموزشی <span class="navbar-category-chevron" aria-hidden="true">▾</span>
                        </a>
                        <div class="navbar-category-menu" id="navbarCategoryMenu" role="menu" aria-label="حوزه‌های آموزشی">
                            <div class="navbar-category-loading">برای مشاهده حوزه‌ها مکث کنید…</div>
                        </div>
                    </div>
                    <a href="/pages/instructors.html" class="navbar-link">مدرسین</a>
                    <a href="/pages/blog.html" class="navbar-link">وبلاگ</a>
                    <a href="/pages/contact.html" class="navbar-link">تماس با ما</a>
                </div>

                <div class="navbar-actions">
                    ${isLoggedIn ? `
                        <a href="/pages/dashboard.html" class="btn btn-sm btn-outline">
                            ${user ? user.first_name : 'داشبورد'}
                        </a>
                        ${user && user.role === 'ADMIN' ? `
                            <a href="/pages/admin-dashboard.html" class="btn btn-sm btn-ghost">
                                مدیریت
                            </a>
                        ` : ''}
                        <button onclick="Auth.logout()" class="btn btn-sm btn-ghost">خروج</button>
                    ` : `
                        <a href="/pages/login.html" class="btn btn-sm btn-ghost">ورود</a>
                        <a href="/pages/register.html" class="btn btn-sm btn-primary">ثبت‌نام</a>
                    `}
                </div>
            </div>
        </nav>

        <div class="mobile-menu" id="mobileMenu">
            <button class="mobile-menu-close" onclick="Header.toggleMobile()" aria-label="بستن منو">✕</button>
            <div class="mobile-menu-links">
                <a href="/" class="mobile-menu-link">خانه</a>
                <a href="/pages/courses.html" class="mobile-menu-link">دوره‌ها</a>
                <div class="mobile-category-group">
                    <button type="button" class="mobile-menu-link mobile-category-trigger" id="mobileCategoryTrigger" aria-expanded="false">حوزه‌های آموزشی <span aria-hidden="true">▾</span></button>
                    <div class="mobile-category-menu" id="mobileCategoryMenu"></div>
                </div>
                <a href="/pages/instructors.html" class="mobile-menu-link">مدرسین</a>
                <a href="/pages/blog.html" class="mobile-menu-link">وبلاگ</a>
                <a href="/pages/contact.html" class="mobile-menu-link">تماس با ما</a>
                <hr>
                ${isLoggedIn ? `
                    <a href="/pages/dashboard.html" class="mobile-menu-link">داشبورد</a>
                    ${user && user.role === 'ADMIN' ? `
                        <a href="/pages/admin-dashboard.html" class="mobile-menu-link">پنل مدیریت</a>
                    ` : ''}
                    <a href="#" onclick="Auth.logout(); return false;" class="mobile-menu-link" style="color:var(--error)">خروج</a>
                ` : `
                    <a href="/pages/login.html" class="mobile-menu-link">ورود</a>
                    <a href="/pages/register.html" class="mobile-menu-link">ثبت‌نام</a>
                `}
            </div>
        </div>`;
    }

    function toggleMobile() {
        const menu = document.getElementById('mobileMenu');
        menu.classList.toggle('open');
    }

    let categoriesPromise = null;

    function loadCategories() {
        if (!categoriesPromise) {
            categoriesPromise = API.get('/courses/categories')
                .then(data => Array.isArray(data) ? data : (data.items || []))
                .catch(error => {
                    categoriesPromise = null;
                    throw error;
                });
        }
        return categoriesPromise;
    }

    function escapeHtml(value) {
        return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    }

    function categoryHref(category) {
        return '/pages/courses.html?category=' + encodeURIComponent(category.slug || '');
    }

    async function populateCategories() {
        const desktopMenu = document.getElementById('navbarCategoryMenu');
        const mobileMenu = document.getElementById('mobileCategoryMenu');
        try {
            const categories = await loadCategories();
            const markup = categories.length ? categories.map(category => {
                const label = escapeHtml(category.name);
                const href = categoryHref(category);
                return '<a role="menuitem" class="navbar-category-item" href="' + href + '">' + label + '</a>';
            }).join('') : '<span class="navbar-category-message">حوزه‌ای ثبت نشده است</span>';
            if (desktopMenu) desktopMenu.innerHTML = markup;
            if (mobileMenu) {
                mobileMenu.innerHTML = categories.length ? categories.map(category =>
                    '<a class="mobile-menu-link mobile-category-item" href="' + categoryHref(category) + '">' + escapeHtml(category.name) + '</a>'
                ).join('') : '<span class="navbar-category-message">حوزه‌ای ثبت نشده است</span>';
            }
        } catch (error) {
            const message = '<span class="navbar-category-message">دریافت حوزه‌ها ناموفق بود</span>';
            if (desktopMenu) desktopMenu.innerHTML = message;
            if (mobileMenu) mobileMenu.innerHTML = message;
        }
    }

    function initActiveLinks() {
        const path = window.location.pathname.replace(/\/+$/, '') || '/';
        const links = document.querySelectorAll('.navbar-link[href], .mobile-menu-link[href]');
        links.forEach(link => {
            const url = new URL(link.href, window.location.origin);
            const target = url.pathname.replace(/\/+$/, '') || '/';
            if (target === path && !url.search) {
                link.classList.add('active');
                link.setAttribute('aria-current', 'page');
            }
        });
        const category = new URLSearchParams(window.location.search).get('category');
        if (category) {
            document.querySelectorAll('.navbar-category-trigger').forEach(link => link.classList.add('active'));
        }
    }

    function initCategoryInteractions() {
        const wrapper = document.getElementById('navbarCategory');
        const trigger = document.getElementById('navbarCategoryTrigger');
        const menu = document.getElementById('navbarCategoryMenu');
        const mobileTrigger = document.getElementById('mobileCategoryTrigger');
        const mobileMenu = document.getElementById('mobileCategoryMenu');

        if (wrapper && trigger && menu) {
            const open = () => {
                wrapper.classList.add('is-open');
                trigger.setAttribute('aria-expanded', 'true');
                populateCategories();
            };
            const close = () => {
                wrapper.classList.remove('is-open');
                trigger.setAttribute('aria-expanded', 'false');
            };
            wrapper.addEventListener('mouseenter', open);
            wrapper.addEventListener('mouseleave', close);
            trigger.addEventListener('focus', open);
            trigger.addEventListener('click', event => {
                event.preventDefault();
                wrapper.classList.contains('is-open') ? close() : open();
            });
            wrapper.addEventListener('keydown', event => {
                if (event.key === 'Escape') { close(); trigger.focus(); }
            });
        }
        if (mobileTrigger && mobileMenu) {
            mobileTrigger.addEventListener('click', () => {
                const expanded = mobileTrigger.getAttribute('aria-expanded') === 'true';
                mobileTrigger.setAttribute('aria-expanded', String(!expanded));
                mobileMenu.classList.toggle('is-open', !expanded);
                if (!expanded) populateCategories();
            });
        }
    }

    function init() {
        const headerEl = document.getElementById('header');
        if (headerEl) {
            headerEl.innerHTML = render();
            initActiveLinks();
            initCategoryInteractions();
        }
    }

    return { render, toggleMobile, init, loadCategories };
})();
