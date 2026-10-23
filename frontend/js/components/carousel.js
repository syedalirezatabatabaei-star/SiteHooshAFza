/**
 * Carousel Component for هوش افزا
 * RTL-friendly image slider with prev/next buttons, dots, autoplay and responsive heights.
 *
 * Usage:
 *   <div id="heroCarousel" class="carousel" data-autoplay="true" data-interval="5000">
 *       <div class="carousel-track"> ... <figure class="carousel-slide">...</figure> ... </div>
 *       <button class="carousel-btn carousel-next" aria-label="اسلاید بعدی">‹</button>
 *       <button class="carousel-btn carousel-prev" aria-label="اسلاید قبلی">›</button>
 *       <div class="carousel-dots" role="tablist" aria-label="انتخاب اسلاید"></div>
 *   </div>
 *   Carousel.init('#heroCarousel');
 */
const Carousel = (() => {
    const CAROUSEL_ICONS = {
        next: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path d="M9 4l8 8-8 8" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        prev: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path d="M15 4l-8 8 8 8" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    };

    const instances = new Map();

    function create(root) {
        const track = root.querySelector('.carousel-track');
        const slides = Array.from(root.querySelectorAll('.carousel-slide'));
        const dotsWrap = root.querySelector('.carousel-dots');
        const prevBtn = root.querySelector('.carousel-prev');
        const nextBtn = root.querySelector('.carousel-next');

        if (!track || slides.length === 0) return null;

        const autoplay = (root.dataset.autoplay || 'true') === 'true';
        const interval = parseInt(root.dataset.interval || '5000', 10);
        const loop = (root.dataset.loop || 'true') === 'true';

        const state = { index: 0, timer: null, slides, track, root, dotsWrap, loop, autoplay, interval, busy: false };

        // Build dots
        if (dotsWrap) {
            dotsWrap.innerHTML = '';
            slides.forEach((_, i) => {
                const dot = document.createElement('button');
                dot.className = 'carousel-dot' + (i === 0 ? ' active' : '');
                dot.setAttribute('role', 'tab');
                dot.setAttribute('aria-label', `اسلاید ${i + 1}`);
                dot.addEventListener('click', () => goTo(state, i, true));
                dotsWrap.appendChild(dot);
            });
        }

        // Inject crisp SVG arrows into the placeholder buttons
        if (nextBtn && !nextBtn.querySelector('svg')) nextBtn.innerHTML = CAROUSEL_ICONS.next;
        if (prevBtn && !prevBtn.querySelector('svg')) prevBtn.innerHTML = CAROUSEL_ICONS.prev;

        // Buttons — in RTL, «بعدی» goes visually left, «قبلی» goes visually right
        if (nextBtn) nextBtn.addEventListener('click', () => next(state, true));
        if (prevBtn) prevBtn.addEventListener('click', () => prev(state, true));

        // Keyboard support
        root.setAttribute('tabindex', '0');
        root.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') { next(state, true); e.preventDefault(); }
            if (e.key === 'ArrowRight') { prev(state, true); e.preventDefault(); }
        });

        // Touch swipe support
        let startX = null;
        track.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; stopAutoplay(state); }, { passive: true });
        track.addEventListener('touchend', (e) => {
            if (startX === null) return;
            const dx = e.changedTouches[0].clientX - startX;
            if (Math.abs(dx) > 40) { dx > 0 ? next(state, true) : prev(state, true); }
            startX = null;
            startAutoplay(state);
        }, { passive: true });

        // Pause on hover
        root.addEventListener('mouseenter', () => stopAutoplay(state));
        root.addEventListener('mouseleave', () => startAutoplay(state));

        startAutoplay(state);
        update(state);
        return state;
    }

    function update(state) {
        const { track, slides, dotsWrap, index } = state;
        track.style.transform = `translateX(${index * 100}%)`; // RTL: positive X moves content right→left reveal
        slides.forEach((s, i) => s.classList.toggle('active', i === index));
        if (dotsWrap) {
            Array.from(dotsWrap.children).forEach((d, i) => {
                d.classList.toggle('active', i === index);
                d.setAttribute('aria-selected', i === index ? 'true' : 'false');
            });
        }
    }

    function goTo(state, i, user) {
        if (state.busy) return;
        const n = state.slides.length;
        state.index = ((i % n) + n) % n;
        state.busy = true;
        update(state);
        setTimeout(() => { state.busy = false; }, 350);
        if (user) restartAutoplay(state);
    }

    function next(state, user) {
        const last = state.index === state.slides.length - 1;
        if (last && !state.loop) { stopAutoplay(state); return; }
        goTo(state, state.index + 1, user);
    }

    function prev(state, user) {
        const first = state.index === 0;
        if (first && !state.loop) { stopAutoplay(state); return; }
        goTo(state, state.index - 1, user);
    }

    function startAutoplay(state) {
        if (!state.autoplay || state.timer) return;
        state.timer = setInterval(() => next(state, false), state.interval);
    }

    function stopAutoplay(state) {
        if (state.timer) { clearInterval(state.timer); state.timer = null; }
    }

    function restartAutoplay(state) {
        stopAutoplay(state);
        startAutoplay(state);
    }

    function init(selector) {
        document.querySelectorAll(selector).forEach((root) => {
            if (!instances.has(root)) instances.set(root, create(root));
        });
    }

    return { init };
})();
