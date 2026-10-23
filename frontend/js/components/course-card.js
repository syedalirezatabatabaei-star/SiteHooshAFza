/**
 * Course Card Component
 */
function renderCourseCard(course) {
    return `
    <article class="card course-card">
        <a href="/pages/course-detail.html?slug=${course.slug}" class="card-image-wrapper">
            <img
                src="${course.thumbnail || '/assets/images/placeholder.jpg'}"
                alt="${course.title}"
                class="card-image"
                loading="lazy"
            >
            <span class="course-type-badge badge ${course.course_type === 'IN_PERSON' ? 'badge-primary' : 'badge-info'}">
                ${course.course_type === 'IN_PERSON' ? 'حضوری' : 'ضبط‌شده'}
            </span>
        </a>
        <div class="card-body">
            <a href="/pages/course-detail.html?slug=${course.slug}">
                <h3 class="card-title">${course.title}</h3>
            </a>
            <p class="card-text">${course.short_description || ''}</p>
            <div class="flex items-center gap-2 mb-2">
                ${Utils.generateStars(Math.round(course.average_rating || 0))}
                <span class="text-sm text-muted">(${course.review_count || 0})</span>
            </div>
            <div class="flex items-center gap-2 text-sm text-muted">
                ${course.instructor ? `<span><svg class="ui-icon" aria-hidden="true"><use href="/assets/images/ui-icons.svg#users"></use></svg> ${course.instructor.name}</span>` : ''}
                ${course.category ? `<span><svg class="ui-icon" aria-hidden="true"><use href="/assets/images/ui-icons.svg#folder"></use></svg> ${course.category.name}</span>` : ''}
            </div>
        </div>
        <div class="card-footer">
            <span class="price">${Utils.formatPrice(course.price)}</span>
            <a href="/pages/course-detail.html?slug=${course.slug}" class="btn btn-sm btn-primary">
                مشاهده دوره
            </a>
        </div>
    </article>`;
}
