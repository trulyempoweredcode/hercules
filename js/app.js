/* Hercules bespoke — interactions
   - Floating nav → solid on scroll
   - Mobile drawer toggle
   - Reveal-on-scroll (with .stagger group support)
   - Compare-bar fill on scroll-into-view
   - Megastat count-up on scroll-into-view
   - Form anti-bot timestamp
*/
(() => {
  'use strict';

  // Mark <html> with .js so CSS can opt animations in (no-JS users see static final state)
  document.documentElement.classList.add('js');

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // --- Floating nav: solid when scrolled past hero ---
  const nav = document.querySelector('.nav');
  if (nav) {
    nav.classList.add('nav--floating');
    const onScroll = () => {
      if (window.scrollY > 24) {
        nav.classList.remove('nav--floating');
        nav.classList.add('nav--solid');
      } else {
        nav.classList.add('nav--floating');
        nav.classList.remove('nav--solid');
      }
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // --- Mobile drawer ---
  const toggle = document.querySelector('.nav-toggle');
  const drawer = document.querySelector('.nav-mobile');
  if (toggle && drawer) {
    const navEl = document.querySelector('.nav');
    const setOpen = (open) => {
      toggle.setAttribute('aria-expanded', open);
      drawer.setAttribute('aria-hidden', !open);
      document.body.style.overflow = open ? 'hidden' : '';
      if (navEl) navEl.classList.toggle('menu-open', open);
    };
    toggle.addEventListener('click', () => {
      const isOpen = toggle.getAttribute('aria-expanded') === 'true';
      setOpen(!isOpen);
    });
    drawer.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setOpen(false)));
  }

  // --- Back to top button ---
  (function () {
    const btn = document.createElement('button');
    btn.className = 'back-to-top';
    btn.setAttribute('aria-label', 'Back to top');
    btn.innerHTML = '<svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>';
    btn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
    document.body.appendChild(btn);
    const onScroll = () => btn.classList.toggle('is-visible', window.scrollY > 600);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  })();

  if (!('IntersectionObserver' in window) || reduceMotion) {
    // Fallback: reveal everything immediately, fill all bars, set numerals to target
    document.querySelectorAll('.reveal, .stagger, [class*="reveal--"], [class*="stagger--"]').forEach(el => el.classList.add('in'));
    document.querySelectorAll('.compare').forEach(el => el.classList.add('compare--in-view'));
    document.querySelectorAll('.megastat__num[data-target]').forEach(el => {
      const target = el.dataset.target;
      const prefix = el.dataset.prefix || '';
      const suffix = el.dataset.suffix || '';
      el.innerHTML = prefix + target + suffix;
    });
    return;
  }

  // --- Reveal-on-scroll (works for .reveal AND .stagger + directional modifiers) ---
  const revealSelector = '.reveal, .stagger, [class*="reveal--"], [class*="stagger--"]';
  const revealIO = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('in');
        revealIO.unobserve(e.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -6% 0px' });
  document.querySelectorAll(revealSelector).forEach(el => revealIO.observe(el));

  // --- Compare bars fill ---
  const cmpIO = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('compare--in-view');
        cmpIO.unobserve(e.target);
      }
    });
  }, { threshold: 0.3 });
  document.querySelectorAll('.compare').forEach(el => cmpIO.observe(el));

  // --- Count-up megastat numerals ---
  // Markup expected:
  //   <div class="megastat__num" data-target="134" data-suffix="<sup>+ GW</sup>">134<sup>+ GW</sup></div>
  // The starting innerText is preserved so the page is readable before JS runs.
  const easeOutCubic = t => 1 - Math.pow(1 - t, 3);

  const animateNumber = (el) => {
    const target = parseFloat(el.dataset.target);
    if (Number.isNaN(target)) return;
    const start = parseFloat(el.dataset.start || '0');
    const prefix = el.dataset.prefix || '';
    const suffix = el.dataset.suffix || '';
    const decimals = (el.dataset.target.split('.')[1] || '').length;
    const duration = parseInt(el.dataset.duration || '1600', 10);
    const startTs = performance.now();

    el.classList.add('counting');

    const tick = (now) => {
      const elapsed = now - startTs;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeOutCubic(progress);
      const value = start + (target - start) * eased;
      const rendered = decimals > 0
        ? value.toFixed(decimals)
        : Math.round(value).toLocaleString('en-US');
      el.innerHTML = prefix + rendered + suffix;
      if (progress < 1) {
        requestAnimationFrame(tick);
      } else {
        el.classList.remove('counting');
        el.classList.add('counted');
      }
    };
    requestAnimationFrame(tick);
  };

  const numIO = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        animateNumber(e.target);
        numIO.unobserve(e.target);
      }
    });
  }, { threshold: 0.5 });
  document.querySelectorAll('.megastat__num[data-target]').forEach(el => numIO.observe(el));

  // --- Scroll fallback: triggers the same classes the IOs would, in case IO
  //     hasn't fired (some headless / older contexts, or content already in view) ---
  const inViewport = (el, ratio = 0.12) => {
    const r = el.getBoundingClientRect();
    if (r.height === 0) return false;
    const visible = Math.min(r.bottom, window.innerHeight) - Math.max(r.top, 0);
    return visible / r.height >= ratio;
  };
  const scrollCheck = () => {
    document.querySelectorAll('.reveal:not(.in), .stagger:not(.in), [class*="reveal--"]:not(.in), [class*="stagger--"]:not(.in)').forEach(el => {
      if (inViewport(el, 0.08)) el.classList.add('in');
    });
    document.querySelectorAll('.compare:not(.compare--in-view)').forEach(el => {
      if (inViewport(el, 0.3)) el.classList.add('compare--in-view');
    });
    document.querySelectorAll('.megastat__num[data-target]:not(.counting):not(.counted)').forEach(el => {
      if (inViewport(el, 0.5)) animateNumber(el);
    });
  };
  let scrollTimer;
  window.addEventListener('scroll', () => {
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(scrollCheck, 60);
  }, { passive: true });
  // periodic safety-net: polls every 250ms regardless of scroll events so anchor-jumps,
  // programmatic scrollIntoView, and viewport-resize-driven visibility changes still trigger
  // reveals/bar-fills even when scroll events don't fire.
  let polls = 0;
  const pollInterval = setInterval(() => {
    scrollCheck();
    polls++;
    if (polls > 40) clearInterval(pollInterval); // stop after 10 seconds
  }, 250);
  // also check immediately and on next frame (in case content is above the fold)
  scrollCheck();
  requestAnimationFrame(scrollCheck);
  setTimeout(scrollCheck, 100);
  setTimeout(scrollCheck, 600);

  // --- Hero heading + subtitle: split into words and blur-fade each in
  //     sequence. CTAs slide in from left/right after the copy resolves. ---
  (function () {
    function splitWords(el, baseDelaySec, stepSec) {
      if (!el) return 0;
      var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
      var nodes = []; var n;
      while ((n = walker.nextNode())) nodes.push(n);
      var idx = 0;
      nodes.forEach(function (tn) {
        if (!tn.textContent.trim()) return;
        var parts = tn.textContent.split(/(\s+)/);
        var frag = document.createDocumentFragment();
        parts.forEach(function (p) {
          if (!p) return;
          if (!p.trim()) { frag.appendChild(document.createTextNode(p)); return; }
          var s = document.createElement('span');
          s.className = 'word';
          s.style.animationDelay = (baseDelaySec + idx * stepSec) + 's';
          s.textContent = p;
          frag.appendChild(s);
          idx++;
        });
        tn.parentNode.replaceChild(frag, tn);
      });
      return idx; // number of words split
    }

    var heading = document.querySelector('.hero__heading');
    var sub = document.querySelector('.hero__sub');
    var ctas = document.querySelectorAll('.hero__cta');

    var headingWords = splitWords(heading, 0, 0.08);
    // Subtitle starts ~80ms after the last heading word fires
    var headingFinishMs = 80 + (headingWords > 0 ? (headingWords - 1) * 80 + 600 : 0);
    var subStartSec = Math.max(0.5, (headingFinishMs - 80) / 1000 - 0.15);
    splitWords(sub, subStartSec, 0.035);

    if (heading) setTimeout(function () { heading.classList.add('anim-in'); }, 80);
    if (sub) setTimeout(function () { sub.classList.add('anim-in'); }, 80);

    // CTAs slide in after the subtitle has mostly resolved
    if (ctas.length) {
      var subWordCount = sub ? sub.querySelectorAll('.word').length : 0;
      var subFinishMs = (subStartSec * 1000) + subWordCount * 35 + 600;
      var ctaStart = Math.max(1100, subFinishMs - 200);
      ctas.forEach(function (btn, i) {
        setTimeout(function () { btn.classList.add('anim-in'); }, ctaStart + i * 140);
      });
    }

    // Inner-page page-headers (.ph): same word-fade treatment for h1 + ph__sub
    document.querySelectorAll('.ph h1').forEach(function (h) {
      if (h === heading) return; // already handled above
      var n = splitWords(h, 0, 0.08);
      setTimeout(function () { h.classList.add('anim-in'); }, 120);
    });
    document.querySelectorAll('.ph__sub').forEach(function (s) {
      var ph = s.closest('.ph');
      var ownH1 = ph ? ph.querySelector('h1') : null;
      var hWords = ownH1 ? ownH1.querySelectorAll('.word').length : 0;
      var startSec = Math.max(0.45, (hWords > 0 ? (hWords - 1) * 0.08 + 0.45 : 0.5));
      splitWords(s, startSec, 0.035);
      setTimeout(function () { s.classList.add('anim-in'); }, 120);
    });
  })();

  // --- Hero video: simple autoplay + loop, no scrub ---
  const heroVid = document.querySelector('.hero__media video');
  if (heroVid) {
    heroVid.muted = true;
    heroVid.loop = true;
    heroVid.playsInline = true;
    const tryPlay = () => { const p = heroVid.play(); if (p && p.catch) p.catch(() => {}); };
    tryPlay();
    window.addEventListener('pointerdown', tryPlay, { once: true, passive: true });
    window.addEventListener('touchstart',  tryPlay, { once: true, passive: true });
  }

  // --- Parallax: any element with [data-parallax] translates with scroll ---
  // Range is set by data-parallax-range="N" (px). Default 200 — pronounced enough
  // to be obvious without going past the image's overflow buffer.
  const parallaxTargets = Array.from(document.querySelectorAll('[data-parallax]'));
  if (parallaxTargets.length && !reduceMotion) {
    let parRaf = null;
    const updateParallax = () => {
      parRaf = null;
      const vh = window.innerHeight;
      parallaxTargets.forEach(img => {
        const section = img.closest('.worldmap--hero, [data-parallax-section], section');
        if (!section) return;
        const rect = section.getBoundingClientRect();
        // run even when off-screen so the transform is set when it re-enters
        const range = parseFloat(img.dataset.parallaxRange) || 200;
        // 0 = section bottom just entered viewport top; 1 = section top just left viewport bottom
        const progress = (vh - rect.top) / (vh + rect.height);
        const clamped = Math.max(0, Math.min(1, progress));
        const offset = (clamped - 0.5) * range; // -range/2 → +range/2 px
        img.style.transform = `translate3d(0, ${offset.toFixed(1)}px, 0)`;
      });
    };
    const onParallaxScroll = () => { if (parRaf == null) parRaf = requestAnimationFrame(updateParallax); };
    window.addEventListener('scroll', onParallaxScroll, { passive: true });
    window.addEventListener('resize', onParallaxScroll, { passive: true });
    // continuous rAF guarantees movement even when the browser coalesces scroll events
    const parallaxTick = () => { updateParallax(); requestAnimationFrame(parallaxTick); };
    requestAnimationFrame(parallaxTick);
  }

  // --- Form: timestamp + page anti-bot ---
  const t = document.querySelector('input[name="_t"]');
  if (t) t.value = Date.now();
  const p = document.querySelector('input[name="_page"]');
  if (p) p.value = location.pathname.split('/').pop() || 'index.html';
})();
