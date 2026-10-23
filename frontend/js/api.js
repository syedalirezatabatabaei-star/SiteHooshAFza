/**
 * API Client Module for هوش افزا
 * Handles all HTTP requests to the FastAPI backend
 */
const API = (() => {
    // Production: same-origin via Nginx proxy (/api → FastAPI).
    // Local dev fallback: direct port 8002 when served outside Docker.
    const isLocal = ['127.0.0.1', 'localhost'].includes(window.location.hostname) && window.location.port === '8080';
    const BASE_URL = isLocal
        ? 'http://127.0.0.1:8002/api/v1'
        : '/api/v1';

    function getToken() {
        return localStorage.getItem('access_token');
    }

    function setToken(token) {
        localStorage.setItem('access_token', token);
    }

    function setRefreshToken(token) {
        localStorage.setItem('refresh_token', token);
    }

    function clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    function getAuthHeaders() {
        const token = getToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    function request(method, endpoint, data = null, useAuth = true, retried = false) {
        const url = `${BASE_URL}${endpoint}`;
        const headers = useAuth ? getAuthHeaders() : {};

        if (data) {
            headers['Content-Type'] = 'application/json';
        }

        const options = {
            method,
            headers,
        };

        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            options.body = JSON.stringify(data);
        }

        return fetch(url, options)
            .then(response => {
                if (response.status === 401 && useAuth && !retried) {
                    // Try to refresh token
                    return refreshToken().then(refreshSuccess => {
                        if (refreshSuccess) {
                            return request(method, endpoint, data, useAuth, true);
                        }
                        throw new Error('احراز هویت لازم است. لطفاً وارد شوید.');
                    });
                }
                if (response.status === 403) {
                    throw new Error('دسترسی غیرمجاز');
                }
                if (!response.ok) {
                    return response.json().catch(() => ({})).then(err => {
                        const detail = Array.isArray(err.detail)
                            ? err.detail.map(item => item.msg || 'اطلاعات ورودی نامعتبر است').join('؛ ')
                            : err.detail;
                        throw new Error(detail || `خطا: ${response.status}`);
                    });
                }
                if (response.status === 204) {
                    return null;
                }
                return response.json();
            });
    }

    async function refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            clearTokens();
            return false;
        }

        try {
            const response = await fetch(`${BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken }),
            });

            if (response.ok) {
                const data = await response.json();
                setToken(data.access_token);
                if (data.refresh_token) {
                    setRefreshToken(data.refresh_token);
                }
                return true;
            }
            return false;
        } catch (error) {
            clearTokens();
            return false;
        }
    }

    // Cached current user (localStorage-backed)
    const USER_KEY = 'current_user';

    function getUser() {
        try {
            const raw = localStorage.getItem(USER_KEY);
            return raw ? JSON.parse(raw) : null;
        } catch (e) {
            return null;
        }
    }

    function setUser(user) {
        if (user) {
            localStorage.setItem(USER_KEY, JSON.stringify(user));
        } else {
            localStorage.removeItem(USER_KEY);
        }
    }

    // Generic HTTP helpers used by page scripts
    const get = (endpoint) => request('GET', endpoint);
    const post = (endpoint, data) => request('POST', endpoint, data);
    const put = (endpoint, data) => request('PUT', endpoint, data);
    const patch = (endpoint, data) => request('PATCH', endpoint, data);
    const del = (endpoint) => request('DELETE', endpoint);

    // Public API methods
    return {
        // Auth
        register: (data) => request('POST', '/auth/register', data, false),
        login: (data) => request('POST', '/auth/login', data, false),
        me: () => request('GET', '/auth/me'),
        refresh: (refreshToken) => request('POST', '/auth/refresh', { refresh_token: refreshToken }, false),
        getToken,
        setToken,
        setRefreshToken,
        clearTokens,
        getUser,
        setUser,

        // Generic helpers
        get,
        post,
        put,
        patch,
        del,
        delete: del,

        // Courses
        getCourses: (params = {}) => {
            const query = new URLSearchParams(params).toString();
            return request('GET', `/courses${query ? '?' + query : ''}`);
        },
        getCourse: (slug) => request('GET', `/courses/${slug}`),
        getCategories: () => request('GET', '/courses/categories'),
        getFeaturedCourses: () => request('GET', '/courses/featured'),
        getInstructor: (slug) => request('GET', `/instructors/${slug}`),
        getInstructors: () => request('GET', '/instructors'),

        // Blog
        getArticles: (params = {}) => {
            const query = new URLSearchParams(params).toString();
            return request('GET', `/articles${query ? '?' + query : ''}`);
        },
        getArticle: (slug) => request('GET', `/articles/${slug}`),

        // Search
        search: (q, params = {}) => {
            const query = new URLSearchParams({ q, ...params }).toString();
            return request('GET', `/search?${query}`);
        },

        // Cart
        getCart: () => request('GET', '/cart'),
        addToCart: (courseId) => request('POST', '/cart/items', { course_id: courseId }),
        removeFromCart: (itemId) => request('DELETE', `/cart/items/${itemId}`),
        applyCoupon: (code) => request('POST', '/cart/coupon', { code }),

        // Orders
        createOrder: () => request('POST', '/orders/checkout'),
        getOrders: () => request('GET', '/orders'),
        getOrder: (id) => request('GET', `/orders/${id}`),

        // Payments
        initiatePayment: (orderId) => request('POST', '/payments/initiate', { order_id: orderId }),
        verifyPayment: (token) => request('GET', `/payments/callback?Authority=${encodeURIComponent(token)}&Status=OK`),

        // Enrollments
        getEnrollments: () => request('GET', '/enrollments'),
        getEnrollment: (id) => request('GET', `/enrollments/${id}`),
        getEnrollmentProgress: (enrollmentId) => request('GET', `/enrollments/${enrollmentId}`),
        updateProgress: (enrollmentId, data) => request('PUT', `/enrollments/${enrollmentId}/progress`, data),

        // Exams
        getExams: () => request('GET', '/exams'),
        getExam: (id) => request('GET', `/exams/${id}`),
        startExam: (id) => request('POST', `/exams/${id}/start`),
        submitExam: (id, answers) => request('POST', `/exams/${id}/submit`, { answers }),
        getExamAttempts: (examId) => request('GET', `/exams/${examId}/attempts`),
        getAttemptResult: (attemptId) => request('GET', `/exams/attempts/${attemptId}`),

        // Certificates
        getCertificates: () => request('GET', '/certificates'),
        verifyCertificate: (code) => request('GET', `/certificates/verify/${code}`),

        // Notifications
        getNotifications: () => request('GET', '/notifications'),
        markNotificationRead: (id) => request('PUT', `/notifications/${id}/read`),
        markAllNotificationsRead: () => request('PUT', '/notifications/read-all'),

        // Tickets
        getTickets: () => request('GET', '/tickets'),
        createTicket: (data) => request('POST', '/tickets', data),
        getTicket: (id) => request('GET', `/tickets/${id}`),
        replyToTicket: (id, message) => request('POST', `/tickets/${id}/reply`, { message }),

        // Reviews
        getReviews: (courseId) => request('GET', `/reviews/course/${courseId}`),
        createReview: (data) => request('POST', '/reviews', data),

        // Users
        updateProfile: (data) => request('PUT', '/users/me', data),
        changePassword: (data) => request('POST', '/auth/change-password', data),

        // Admin
        getDashboardStats: () => request('GET', '/admin/dashboard/stats'),
        getAdminUsers: (params = {}) => {
            const query = new URLSearchParams(params).toString();
            return request('GET', `/admin/users${query ? '?' + query : ''}`);
        },
        getAdminCourses: () => request('GET', '/admin/courses'),
        getAdminOrders: (params = {}) => {
            const query = new URLSearchParams(params).toString();
            return request('GET', `/admin/orders${query ? '?' + query : ''}`);
        },
        getAdminPayments: (params = {}) => {
            const query = new URLSearchParams(params).toString();
            return request('GET', `/admin/payments${query ? '?' + query : ''}`);
        },

        // Files
        uploadFile: (file, endpoint) => {
            const formData = new FormData();
            formData.append('file', file);
            return fetch(`${BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: formData,
            }).then(response => {
                if (!response.ok) {
                    throw new Error('آپلود فایل ناموفق بود');
                }
                return response.json();
            });
        },
    };
})();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
}
