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

    function init() {
        const headerEl = document.getElementById('header');
        if (headerEl) {
            headerEl.innerHTML = render();
        }
    }

    return { render, toggleMobile, init };
})();
