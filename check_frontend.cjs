/* Check public API wiring and token retry behavior without changing site data. */
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');

(async () => {
    const calls = [];
    const storage = new Map([['access_token', 'expired'], ['refresh_token', 'refresh']]);
    let fail = false;
    const context = {
        module: { exports: {} }, URLSearchParams, FormData,
        window: { location: { hostname: '127.0.0.1', port: '8080' } },
        localStorage: { getItem: key => storage.get(key), setItem: (key, value) => storage.set(key, value), removeItem: key => storage.delete(key) },
        fetch: async (url, options) => {
            calls.push({ url, method: options.method });
            if (fail && !url.endsWith('/auth/refresh')) return { status: 401, ok: false, json: async () => ({ detail: 'Rejected' }) };
            return { status: 200, ok: true, json: async () => ({ access_token: 'fresh' }) };
        }
    };
    vm.createContext(context);
    vm.runInContext(fs.readFileSync('frontend/js/api.js', 'utf8'), context);
    const api = context.module.exports;
    await api.delete('/cart/items/1');
    await api.updateProgress(1, { lesson_id: 1 });
    await api.replyToTicket(1, 'Test');
    await api.getReviews(1);
    await api.markAllNotificationsRead();
    await api.changePassword({});
    const spec = await (await fetch('http://127.0.0.1:8002/openapi.json')).json();
    for (const call of calls) {
        const path = new URL(call.url).pathname;
        assert(Object.entries(spec.paths).some(([route, methods]) => new RegExp('^' + route.replace(/\{[^}]+\}/g, '[^/]+') + '$').test(path) && methods[call.method.toLowerCase()]), `${call.method} ${path}`);
    }
    fail = true;
    calls.length = 0;
    await assert.rejects(() => api.login({ phone_number: '09129998877', password: 'wrong' }));
    assert.equal(calls.length, 1, 'Failed login must not refresh another session');
    calls.length = 0;
    await assert.rejects(() => api.get('/auth/me'));
    assert.equal(calls.length, 3, 'Expired session must refresh once and retry once');
    for (const file of fs.readdirSync('frontend/pages')) {
        if (!file.endsWith('.html')) continue;
        const html = fs.readFileSync('frontend/pages/' + file, 'utf8');
        if (html.includes('Header.init')) {
            assert(html.indexOf('/js/api.js') >= 0 && html.indexOf('/js/auth.js') >= 0, file + ' missing header dependencies');
            assert(html.indexOf('/js/api.js') < html.indexOf('/js/components/header.js'), file + ' wrong script order');
        }
    }
    console.log('PASS: frontend methods match live OpenAPI; login errors and refresh retries; all page header dependencies.');
})().catch(error => { console.error(error); process.exitCode = 1; });
