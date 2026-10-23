/* Homepage uses the existing public API and shared course component. */
(() => {
    const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    async function load(id, endpoint, render, empty, fallback = null) {
        const container = document.getElementById(id);
        container.setAttribute('aria-live', 'polite');
        container.innerHTML = '<div class="load-state">در حال دریافت اطلاعات…</div>';
        try {
            const data = await API.get(endpoint);
            const items = Array.isArray(data) ? data : data.items;
            container.innerHTML = items?.length ? render(items) : fallback ? fallback() : `<div class="load-state">${empty}</div>`;
            container.querySelectorAll('img').forEach(img => img.addEventListener('error', () => {
                if (!img.src.endsWith('/assets/images/placeholder.jpg')) img.src = '/assets/images/placeholder.jpg';
            }, { once: true }));
        } catch {
            if (fallback) { container.innerHTML = fallback(); return; }
            container.innerHTML = '<div class="load-state">دریافت اطلاعات امکان‌پذیر نشد.<br><button type="button" class="btn btn-sm btn-outline">تلاش دوباره</button></div>';
            container.querySelector('button').addEventListener('click', () => load(id, endpoint, render, empty));
        }
    }
    document.addEventListener('DOMContentLoaded', () => {
        Header.init(); Footer.init();
        if (typeof Carousel !== 'undefined') Carousel.init('#heroCarousel');
        document.querySelector('.navbar-menu a[href="/"]')?.classList.add('active');
        const icons = ['chip', 'layers', 'eye', 'chart', 'code', 'book'];
        load('categories', '/courses/categories', items => items.map((c, i) => `
            <a href="/pages/courses.html?category=${encodeURIComponent(c.slug)}" class="category-card">
                <div class="category-icon" aria-hidden="true"><svg class="ui-icon" aria-hidden="true"><use href="/assets/images/ui-icons.svg#${icons[i % icons.length]}"></use></svg></div>
                <h3 class="category-title">${escape(c.name)}</h3>
                <p class="category-description">${escape(c.description || 'کشف دوره‌ها و شروع یادگیری')}</p><span class="category-arrow" aria-hidden="true">←</span>
            </a>`).join(''), 'هنوز دسته‌بندی‌ای منتشر نشده است.');
        load('popularCourses', '/courses?page=1&page_size=4', items => items.map(renderCourseCard).join(''), 'هنوز دوره‌ای منتشر نشده است.');
        load('instructors', '/instructors?page=1&page_size=4', items => items.map(i => `
            <article class="instructor-tile">
                ${i.profile_image && /^(https?:\/\/|\/)/.test(i.profile_image) ? `<img class="instructor-avatar" src="${escape(i.profile_image)}" alt="${escape(i.name)}" loading="lazy">` : `<span class="instructor-avatar">${escape((i.name || '').slice(0, 1))}</span>`}
                <div><h3>${escape(i.name)}</h3><p>${escape(i.specialization)}</p></div>
            </article>`).join(''), 'اطلاعات مدرسین به‌زودی منتشر می‌شود.');
    });
})();
