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
        const learningSearch = document.getElementById('learningPathSearch');
        learningSearch?.addEventListener('submit', event => {
            const query = document.getElementById('learningPathQuery')?.value.trim();
            if (!query) {
                event.preventDefault();
                document.getElementById('learningPathQuery')?.focus();
            }
        });
        document.querySelector('.navbar-menu a[href="/"]')?.classList.add('active');
        const iconForCategory = name => { const value = String(name || '').toLowerCase(); if (/پایتون|برنامه|کدنویس|program|python/.test(value)) return 'code'; if (/ماشین|یادگیر|هوش مصنوعی|ai|machine/.test(value)) return 'chip'; if (/بینایی|تصویر|vision/.test(value)) return 'eye'; if (/داده|تحلیل|آمار|data|analytics/.test(value)) return 'chart'; if (/عمیق|شبکه|deep|neural/.test(value)) return 'layers'; if (/دوره|آموزش|مبانی|کتاب/.test(value)) return 'book'; return 'sparkles'; };
        load('categories', '/courses/categories', items => items.map((c, i) => `
            <a href="/pages/courses.html?category=${encodeURIComponent(c.slug)}" class="category-card">
                <div class="category-icon" aria-hidden="true"><svg class="ui-icon" aria-hidden="true"><use href="/assets/images/ui-icons.svg#${iconForCategory(c.name)}"></use></svg></div>
                <h3 class="category-title">${escape(c.name)}</h3>
                <p class="category-description">${escape(c.description || 'کشف دوره‌ها و شروع یادگیری')}</p><span class="category-arrow" aria-hidden="true">←</span>
            </a>`).join(''), 'هنوز دسته‌بندی‌ای منتشر نشده است.');
        load('popularCourses', '/courses?page=1&page_size=4', items => items.map(renderCourseCard).join(''), 'هنوز دوره‌ای منتشر نشده است.');
        load('instructors', '/instructors?page=1&page_size=8', items => items.map(i => `
            <article class="instructor-tile">
                ${i.profile_image && /^(https?:\\/\\/|\\/)/.test(i.profile_image) ? `<img class="instructor-avatar" src="${escape(i.profile_image)}" alt="${escape(i.name)}" loading="lazy">` : `<span class="instructor-avatar">${escape((i.name || '').slice(0, 1))}</span>`}
                <div><h3>${escape(i.name)}</h3><p>${escape(i.specialization || 'مدرس هوش افزا')}</p></div>
            </article>`).join(''), 'اطلاعات مدرسین به‌زودی منتشر می‌شود.');
        const countItems = data => Array.isArray(data) ? data.length : (Array.isArray(data?.items) ? data.items.length : Number(data?.total ?? data?.total_count ?? data?.count ?? 0));
        const setStat = (id, value) => { const el = document.getElementById(id); if (el && Number.isFinite(Number(value))) el.textContent = new Intl.NumberFormat('fa-IR').format(Number(value)); };
        Promise.allSettled([
            API.get('/courses?page=1&page_size=1'),
            API.get('/instructors?page=1&page_size=1'),
            API.get('/courses/categories'),
            API.get('/admin/dashboard/stats')
        ]).then(results => {
            const [courses, instructors, categories, dashboard] = results;
            if (courses.status === 'fulfilled') setStat('statCourses', countItems(courses.value));
            if (instructors.status === 'fulfilled') setStat('statInstructors', countItems(instructors.value));
            if (categories.status === 'fulfilled') setStat('statCategories', countItems(categories.value));
            if (dashboard.status === 'fulfilled') {
                const stats = dashboard.value?.data || dashboard.value;
                const students = stats?.total_students ?? stats?.students_count ?? stats?.total_users ?? stats?.users_count;
                if (students != null) setStat('statStudents', students);
            }
        });
    });
})();
