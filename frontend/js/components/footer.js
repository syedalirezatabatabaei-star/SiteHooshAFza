/**
 * Footer Component for هوش افزا
 */
const Footer = (() => {
    // Set the institution's verified profile URLs here when available.
    const socialProfiles = { instagram: '', linkedin: '' };
    function socialItem(network, label, icon) {
        const content = `${icon}<span>${label}</span>`;
        const url = socialProfiles[network];
        return url && /^https:\/\//.test(url)
            ? `<a href="${url.replace(/&/g, '&amp;').replace(/"/g, '&quot;')}" class="footer-social" target="_blank" rel="noopener noreferrer" aria-label="${label} هوش افزا">${content}</a>`
            : `<span class="footer-social footer-social-pending" title="آدرس صفحه هنوز اضافه نشده است">${content}</span>`;
    }
    function render() {
        return `
        <footer class="footer" role="contentinfo">
            <div class="container">
                <div class="footer-grid">
                    <div>
                        <div class="footer-brand">
                            <img src="/assets/images/logo.jpg" alt="لوگوی هوش افزا" class="footer-logo" width="52" height="52">
                            <h3 class="footer-title" style="margin-bottom:0">هوش افزا</h3>
                        </div>
                        <p class="footer-link" style="line-height:1.8;margin-top:var(--space-3)">
                            مؤسسه علمی، آموزشی و پژوهشی هوش افزا با هدف ارتقای سطح دانش و مهارت
                            دانشجویان و علاقه‌مندان به یادگیری تأسیس شده است.
                        </p>
                    </div>
                    <div>
                        <h4 class="footer-title">دسترسی سریع</h4>
                        <div class="footer-links">
                            <a href="/pages/courses.html" class="footer-link">دوره‌ها</a>
                            <a href="/pages/courses.html?type=IN_PERSON" class="footer-link">دوره‌های حضوری</a>
                            <a href="/pages/courses.html?type=RECORDED" class="footer-link">دوره‌های ضبط‌شده</a>
                            <a href="/pages/instructors.html" class="footer-link">مدرسین</a>
                        </div>
                    </div>
                    <div>
                        <h4 class="footer-title">لینک‌های مفید</h4>
                        <div class="footer-links">
                            <a href="/pages/about.html" class="footer-link">درباره ما</a>
                            <a href="/pages/blog.html" class="footer-link">وبلاگ</a>
                            <a href="/pages/faq.html" class="footer-link">سؤالات متداول</a>
                            <a href="/pages/terms.html" class="footer-link">قوانین و مقررات</a>
                            <a href="/pages/privacy.html" class="footer-link">حریم خصوصی</a>
                        </div>
                    </div>
                    <div>
                        <h4 class="footer-title">تماس با ما</h4>
                        <div class="footer-links">
                            <a href="tel:+989025100133" class="footer-link" dir="ltr"><svg class="ui-icon" aria-hidden="true"><use href="/assets/images/ui-icons.svg#phone"></use></svg> ۰۹۰۲۵۱۰۰۱۳۳</a>
                            <span class="footer-link"><svg class="ui-icon" aria-hidden="true"><use href="/assets/images/ui-icons.svg#mail"></use></svg> info@hooshafza.ir</span>
                            <span class="footer-link"><svg class="ui-icon" aria-hidden="true"><use href="/assets/images/ui-icons.svg#pin"></use></svg> اصفهان، خیابان نشاط، روبروی بانک رفاه، مؤسسه علمی آموزشی هوش افزا</span>
                        </div>
                        <div class="footer-socials" aria-label="شبکه‌های اجتماعی هوش افزا">
                            ${socialItem('instagram', 'اینستاگرام', '<svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"></rect><circle cx="12" cy="12" r="4"></circle><circle cx="17.5" cy="6.5" r=".8" fill="currentColor" stroke="none"></circle></svg>')}
                            ${socialItem('linkedin', 'لینکدین', '<svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="3"></rect><path d="M7 10v7M11 17v-7m0 3c0-4 6-4 6 0v4"></path><circle cx="7" cy="7" r=".8" fill="currentColor" stroke="none"></circle></svg>')}
                        </div>
                    </div>
                </div>
                <section class="footer-trust" aria-labelledby="footerTrustTitle">
                    <div>
                        <h4 id="footerTrustTitle" class="footer-trust-title">نماد اعتماد الکترونیکی</h4>
                        <p class="footer-trust-note">محل نمایش اینماد پس از افزودن کد رسمی</p>
                    </div>
                    <div id="enamadBadge" class="footer-enamad-slot">
                        <!-- Replace this placeholder with the official issued eNAMAD embed. -->
                        <svg class="ui-icon" aria-hidden="true"><use href="/assets/images/ui-icons.svg#shield"></use></svg>
                        <span>جایگاه اینماد</span>
                    </div>
                </section>
                <div class="footer-bottom">
                    <p>© ${new Date().getFullYear()} هوش افزا — مؤسسه علمی، آموزشی و پژوهشی. تمامی حقوق محفوظ است.</p>
                </div>
            </div>
        </footer>`;
    }

    function init() {
        const footerEl = document.getElementById('footer');
        if (footerEl) {
            footerEl.innerHTML = render();
        }
    }

    return { render, init };
})();
