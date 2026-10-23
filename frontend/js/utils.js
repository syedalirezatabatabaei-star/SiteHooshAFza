/**
 * Utility functions for هوش افزا
 */
const Utils = (() => {
    function formatPrice(amount) {
        const num = Number(amount);
        if (isNaN(num)) return '۰ تومان';
        return new Intl.NumberFormat('fa-IR').format(num) + ' تومان';
    }

    function formatDate(dateStr) {
        if (!dateStr) return '';
        return new Date(dateStr).toLocaleDateString('fa-IR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });
    }

    function formatDateTime(dateStr) {
        if (!dateStr) return '';
        return new Date(dateStr).toLocaleDateString('fa-IR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    }

    function toPersianDigits(str) {
        const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
        return String(str).replace(/\d/g, d => persianDigits[d]);
    }

    function showToast(message, type = 'info') {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    function showLoading(container) {
        container.innerHTML = '<div class="loading-overlay"><div class="spinner spinner-lg"></div></div>';
    }

    function showError(container, message) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon"><svg class="ui-icon" aria-hidden="true"><use href="/assets/images/ui-icons.svg#alert"></use></svg></div>
                <div class="empty-state-text">${message}</div>
            </div>`;
    }

    function showEmpty(container, message = 'موردی یافت نشد') {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon"><svg class="ui-icon" aria-hidden="true"><use href="/assets/images/ui-icons.svg#mail"></use></svg></div>
                <div class="empty-state-text">${message}</div>
            </div>`;
    }

    function createPagination(container, currentPage, totalPages, callback) {
        if (totalPages <= 1) { container.innerHTML = ''; return; }
        let html = '<div class="pagination">';

        if (currentPage > 1) {
            html += `<button onclick="(${callback.name || 'window._paginationCallback'})(${currentPage - 1})">← قبلی</button>`;
        }

        for (let i = 1; i <= totalPages; i++) {
            if (i === currentPage) {
                html += `<span class="active">${toPersianDigits(i)}</span>`;
            } else if (Math.abs(i - currentPage) <= 2 || i === 1 || i === totalPages) {
                html += `<button onclick="(${callback.name || 'window._paginationCallback'})(${i})">${toPersianDigits(i)}</button>`;
            } else if (Math.abs(i - currentPage) === 3) {
                html += '<span>...</span>';
            }
        }

        if (currentPage < totalPages) {
            html += `<button onclick="(${callback.name || 'window._paginationCallback'})(${currentPage + 1})">بعدی ←</button>`;
        }

        html += '</div>';
        container.innerHTML = html;
    }

    function getUrlParam(name) {
        const params = new URLSearchParams(window.location.search);
        return params.get(name);
    }

    function generateStars(rating) {
        let html = '<div class="rating">';
        for (let i = 1; i <= 5; i++) {
            html += `<span class="star ${i <= rating ? '' : 'empty'}">★</span>`;
        }
        html += '</div>';
        return html;
    }

    function getCourseTypeBadge(type) {
        if (type === 'IN_PERSON') {
            return '<span class="badge badge-primary">حضوری</span>';
        }
        return '<span class="badge badge-info">ضبط‌شده</span>';
    }

    function getStatusBadge(status) {
        const map = {
            'ACTIVE': 'badge-success',
            'INACTIVE': 'badge-warning',
            'SUSPENDED': 'badge-error',
            'PENDING': 'badge-warning',
            'SUCCESS': 'badge-success',
            'FAILED': 'badge-error',
            'PAID': 'badge-success',
            'CANCELED': 'badge-error',
            'OPEN': 'badge-info',
            'IN_PROGRESS': 'badge-warning',
            'ANSWERED': 'badge-success',
            'CLOSED': 'badge-error',
            'APPROVED': 'badge-success',
            'REJECTED': 'badge-error',
        };
        return `<span class="badge ${map[status] || 'badge-info'}">${status}</span>`;
    }

    return {
        formatPrice, formatDate, formatDateTime, toPersianDigits,
        showToast, showLoading, showError, showEmpty,
        createPagination, getUrlParam, generateStars,
        getCourseTypeBadge, getStatusBadge,
    };
})();
