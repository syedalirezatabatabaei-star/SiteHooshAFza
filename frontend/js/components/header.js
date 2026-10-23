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
                    <div class="navbar-category" id="navbarCategory">
                        <a href="/pages/courses.html" class="navbar-link navbar-category-trigger" aria-haspopup="true" aria-expanded="false" id="navbarCategoryTrigger">
                            حوزه‌های آموزشی <span class="navbar-category-chevron" aria-hidden="true">▾</span>
                        </a>
                        <div class="navbar-category-menu" id="navbarCategoryMenu" role="menu" aria-label="حوزه‌های آموزشی">
                            <div class="navbar-category-loading">برای مشاهده حوزه‌ها مکث کنید…</div>
                        </div>
                    </div>
                    <a href="/pages/courses.html" class="navbar-link navbar-courses-link">دوره‌ها</a>
                    <a href="/pages/instructors.html" class="navbar-link">مدرسین</a>
                    <a href="/pages/blog.html" class="navbar-link">وبلاگ</a>
                    <div class="navbar-dropdown" id="navbarAboutDropdown">
                        <a href="/pages/about.html" class="navbar-link navbar-dropdown-trigger" aria-haspopup="true" aria-expanded="false">درباره ما <span class="navbar-category-chevron" aria-hidden="true">▾</span></a>
                        <div class="navbar-dropdown-menu" role="menu" aria-label="درباره ما">
                            <a role="menuitem" class="navbar-dropdown-item" href="/pages/about.html">درباره ما</a>
                            <a role="menuitem" class="navbar-dropdown-item" href="/pages/gallery.html">گالری</a>
                        </div>
                    </div>
                    <div class="navbar-dropdown" id="navbarCareersDropdown">
                        <a href="/pages/careers.html" class="navbar-link navbar-dropdown-trigger" aria-haspopup="true" aria-expanded="false">فرصت شغلی <span class="navbar-category-chevron" aria-hidden="true">▾</span></a>
                        <div class="navbar-dropdown-menu" role="menu" aria-label="فرصت شغلی">
                            <a role="menuitem" class="navbar-dropdown-item" href="/pages/collaborate-institute.html">همکاری با مؤسسه</a>
                            <a role="menuitem" class="navbar-dropdown-item" href="/pages/subsidiary-companies.html">همکاری با شرکت‌های زیرمجموعه</a>
                            <a role="menuitem" class="navbar-dropdown-item" href="/pages/job-opportunities.html">فرصت‌های شغلی</a>
                        </div>
                    </div>
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
                <div class="mobile-category-group">
                    <button type="button" class="mobile-menu-link mobile-category-trigger" id="mobileCategoryTrigger" aria-expanded="false">حوزه‌های آموزشی <span aria-hidden="true">▾</span></button>
                    <div class="mobile-category-menu" id="mobileCategoryMenu"></div>
                </div>
                <a href="/pages/courses.html" class="mobile-menu-link mobile-courses-link">دوره‌ها</a>
                <a href="/pages/instructors.html" class="mobile-menu-link">مدرسین</a>
                <a href="/pages/blog.html" class="mobile-menu-link">وبلاگ</a>
                <div class="mobile-nav-group">
                    <button type="button" class="mobile-menu-link mobile-nav-group-trigger" aria-expanded="false" aria-controls="mobileAboutLinks">درباره ما <span aria-hidden="true">▾</span></button>
                    <div class="mobile-nav-submenu" id="mobileAboutLinks">
                        <a class="mobile-menu-link" href="/pages/about.html">درباره ما</a>
                        <a class="mobile-menu-link" href="/pages/gallery.html">گالری</a>
                    </div>
                </div>
                <div class="mobile-nav-group">
                    <button type="button" class="mobile-menu-link mobile-nav-group-trigger" aria-expanded="false" aria-controls="mobileCareerLinks">فرصت شغلی <span aria-hidden="true">▾</span></button>
                    <div class="mobile-nav-submenu" id="mobileCareerLinks">
                        <a class="mobile-menu-link" href="/pages/collaborate-institute.html">همکاری با مؤسسه</a>
                        <a class="mobile-menu-link" href="/pages/subsidiary-companies.html">همکاری با شرکت‌های زیرمجموعه</a>
                        <a class="mobile-menu-link" href="/pages/job-opportunities.html">فرصت‌های شغلی</a>
                    </div>
                </div>
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
        const path = window.location.pathname.replace(/\\/+$/, '') || '/';
        const category = new URLSearchParams(window.location.search).get('category');
        const links = document.querySelectorAll('.navbar-link[href], .mobile-menu-link[href]');
        links.forEach(link => {
            const url = new URL(link.href, window.location.origin);
            const target = url.pathname.replace(/\\/+$/, '') || '/';
            if (target !== path || url.search) return;
            // Course and category triggers share a destination; never mark both active.
            if (category && (link.classList.contains('navbar-courses-link') || link.classList.contains('mobile-courses-link'))) return;
            if (!category && (link.classList.contains('navbar-category-trigger') || link.classList.contains('mobile-category-trigger'))) return;
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        });
        if (category) {
            document.querySelectorAll('.navbar-category-trigger').forEach(link => {
                link.classList.add('active');
                link.setAttribute('aria-current', 'page');
            });
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

    function initMobileNavGroups() {
        document.querySelectorAll('#header .mobile-nav-group-trigger').forEach(trigger => {
            trigger.addEventListener('click', () => {
                const expanded = trigger.getAttribute('aria-expanded') === 'true';
                trigger.setAttribute('aria-expanded', String(!expanded));
                const submenu = document.getElementById(trigger.getAttribute('aria-controls'));
                if (submenu) submenu.classList.toggle('is-open', !expanded);
            });
        });
    }

    function init() {
        const headerEl = document.getElementById('header');
        if (headerEl) {
            headerEl.innerHTML = render();
            initActiveLinks();
            initCategoryInteractions();
            initMobileNavGroups();
        }
    }

    return { render, toggleMobile, init, loadCategories };
})();
