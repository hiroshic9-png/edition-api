/* ═══════════════════════════════════════════════════════════
   EDITION — Application Core
   SPA Router + Page Rendering + Animations
   ═══════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  let categoriesData = [];
  let assetsData = [];
  const app = document.getElementById('app');

  /* ── Data ── */
  async function loadCategories() {
    try {
      const resp = await fetch('./data/categories.json');
      const data = await resp.json();
      categoriesData = data.categories;
    } catch (e) {
      console.error('Failed to load categories:', e);
    }
  }

  async function loadAssets() {
    try {
      const resp = await fetch('./data/assets.json');
      const data = await resp.json();
      assetsData = data.assets;
    } catch (e) {
      console.error('Failed to load assets:', e);
    }
  }

  function getAssetsForCategory(slug) {
    return assetsData.filter(a => a.category === slug);
  }

  /* ── Router ── */
  function getRoute() {
    const path = window.location.pathname.replace(/\/$/, '') || '/';
    if (path === '/' || path === '/index.html') return { page: 'home' };
    if (path === '/discover') return { page: 'discover' };
    const match = path.match(/^\/discover\/(.+)$/);
    if (match) return { page: 'category', slug: match[1] };
    return { page: 'home' };
  }

  async function navigate(path, pushState = true) {
    if (pushState) window.history.pushState({}, '', path);
    app.classList.add('transitioning');
    await new Promise(r => setTimeout(r, 250));
    const route = getRoute();
    renderPage(route);
    app.classList.remove('transitioning');
    window.scrollTo({ top: 0 });
    setTimeout(initRevealAnimations, 100);
  }

  window.addEventListener('popstate', () => navigate(window.location.pathname, false));

  document.addEventListener('click', (e) => {
    const link = e.target.closest('a[data-link]');
    if (link) {
      e.preventDefault();
      navigate(link.getAttribute('href'));
    }
  });

  /* ── Render ── */
  function renderPage(route) {
    switch (route.page) {
      case 'home': renderHome(); break;
      case 'discover': renderDiscover(); break;
      case 'category': renderCategory(route.slug); break;
      default: renderHome();
    }
    updateActiveNav(route);
  }

  function updateActiveNav(route) {
    document.querySelectorAll('.header__link').forEach(l => {
      l.classList.remove('header__link--active');
    });
  }

  /* ── Home Page ── */
  function renderHome() {
    const featured = categoriesData.slice(0, 6);
    const editorial1 = categoriesData.find(c => c.slug === 'swords');
    const editorial2 = categoriesData.find(c => c.slug === 'ceramics');

    app.innerHTML = `
      ${renderHeader()}

      <section class="hero" id="hero">
        <div class="hero__bg">
          <img src="https://images.metmuseum.org/CRDImages/as/original/DP130155.jpg"
               alt="Under the Wave off Kanagawa by Katsushika Hokusai"
               loading="eager" />
        </div>
        <div class="hero__content">
          <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1.5rem;">EDITION</p>
          <h1 class="hero__title reveal reveal--delay-1">The Art of<br>Japan, Curated</h1>
          <p class="hero__subtitle reveal reveal--delay-2">
            Twelve centuries of mastery — swords, ceramics, ukiyo-e, and beyond.
            Intelligence for collectors, connoisseurs, and the endlessly curious.
          </p>
          <div class="hero__scroll-hint reveal reveal--delay-3">
            <span class="hero__scroll-line"></span>
            <span>Explore</span>
          </div>
        </div>
      </section>

      <section class="section section--large">
        <div class="container" style="text-align:center; margin-bottom: var(--space-lg);">
          <p class="text-label reveal" style="margin-bottom: 1rem;">Collection</p>
          <h2 class="reveal reveal--delay-1" style="font-family: var(--font-serif); font-weight: 300;">
            Twelve Worlds to Discover
          </h2>
        </div>
        <div class="categories-grid">
          ${featured.map((cat, i) => renderCategoryCard(cat, i)).join('')}
        </div>
        <div style="text-align: center; margin-top: var(--space-lg);">
          <a href="/discover" data-link class="editorial__link reveal">
            View All Categories
            <span class="editorial__link-arrow">→</span>
          </a>
        </div>
      </section>

      <div class="divider divider--gold"></div>

      ${editorial1 ? `
      <section class="section section--large">
        <div class="container">
          <div class="editorial reveal">
            <div class="editorial__image">
              <img src="${editorial1.hero_image}"
                   alt="${editorial1.image_alt}"
                   loading="lazy" />
            </div>
            <div class="editorial__text">
              <p class="editorial__eyebrow">Featured</p>
              <h2 class="editorial__heading">${editorial1.title_en}</h2>
              <p class="editorial__body">${editorial1.article.intro}</p>
              <a href="/discover/${editorial1.slug}" data-link class="editorial__link">
                Explore ${editorial1.title_en}
                <span class="editorial__link-arrow">→</span>
              </a>
            </div>
          </div>
        </div>
      </section>
      ` : ''}

      ${editorial2 ? `
      <section class="section">
        <div class="container">
          <div class="editorial editorial--reverse reveal">
            <div class="editorial__image">
              <img src="${editorial2.hero_image}"
                   alt="${editorial2.image_alt}"
                   loading="lazy" />
            </div>
            <div class="editorial__text">
              <p class="editorial__eyebrow">Featured</p>
              <h2 class="editorial__heading">${editorial2.title_en}</h2>
              <p class="editorial__body">${editorial2.article.intro}</p>
              <a href="/discover/${editorial2.slug}" data-link class="editorial__link">
                Explore ${editorial2.title_en}
                <span class="editorial__link-arrow">→</span>
              </a>
            </div>
          </div>
        </div>
      </section>
      ` : ''}

      <div class="divider"></div>

      <section class="section section--large">
        <div class="container">
          <div class="mission reveal">
            <p class="text-label" style="color: var(--gold); margin-bottom: 1.5rem;">Our Mission</p>
            <h2 class="mission__heading">
              To illuminate the depth, beauty, and enduring value of Japanese cultural heritage
              — through rigorous curation, data-driven intelligence, and unwavering respect for tradition.
            </h2>
            <p class="mission__body">
              EDITION bridges the world of Japanese art and the global collector.
              We combine deep cultural knowledge with pattern recognition technology
              to provide authentication support, fair-value analysis, and market intelligence
              across twelve categories of Japanese cultural assets.
            </p>
          </div>
        </div>
      </section>

      ${renderFooter()}
    `;
  }

  function renderCategoryCard(cat, index) {
    return `
      <a href="/discover/${cat.slug}" data-link class="category-card reveal reveal--delay-${(index % 3) + 1}">
        <div class="category-card__image">
          <img src="${cat.image}" alt="${cat.image_alt}" loading="lazy" />
        </div>
        <div class="category-card__overlay"></div>
        <div class="category-card__content">
          <h3 class="category-card__title">${cat.title_en}</h3>
          <p class="category-card__subtitle">${cat.title_jp}</p>
          <p class="category-card__count">Explore →</p>
        </div>
      </a>
    `;
  }

  /* ── Discover Page ── */
  function renderDiscover() {
    app.innerHTML = `
      ${renderHeader()}

      <div class="page-header">
        <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1rem;">Collection</p>
        <h1 class="page-header__title reveal reveal--delay-1">Discover</h1>
        <p class="page-header__desc reveal reveal--delay-2">
          Twelve categories spanning over a millennium of Japanese artistic mastery.
        </p>
      </div>

      <div class="categories-grid" style="max-width: var(--max-w); margin: 0 auto;">
        ${categoriesData.map((cat, i) => renderCategoryCard(cat, i)).join('')}
      </div>

      <div style="height: var(--space-xl);"></div>

      ${renderFooter()}
    `;
  }

  /* ── Category Detail Page ── */
  function renderCategory(slug) {
    const cat = categoriesData.find(c => c.slug === slug);
    if (!cat) { renderHome(); return; }

    const related = categoriesData.filter(c => c.slug !== slug).slice(0, 4);
    const catAssets = getAssetsForCategory(slug);

    app.innerHTML = `
      ${renderHeader()}

      <div class="cat-hero">
        <div class="cat-hero__bg">
          <img src="${cat.hero_image}" alt="${cat.image_alt}" loading="eager" />
        </div>
        <div class="cat-hero__content">
          <p class="cat-hero__eyebrow reveal">EDITION Collection</p>
          <h1 class="cat-hero__title reveal reveal--delay-1">${cat.title_en}</h1>
          <p class="cat-hero__subtitle reveal reveal--delay-2">${cat.title_jp}</p>
        </div>
      </div>

      <article class="cat-article">
        <p class="reveal" style="font-size: 1.125rem; line-height: 2; color: var(--text-secondary); margin-bottom: var(--space-lg);">
          ${cat.article.intro}
        </p>

        ${cat.article.sections.map(sec => `
          <h2 class="reveal">${sec.title}</h2>
          ${sec.body.split('\n\n').map(para => `
            <p class="reveal">${para}</p>
          `).join('')}
        `).join('')}
      </article>

      ${catAssets.length > 0 ? `
      <section class="section" style="max-width: var(--max-w); margin: 0 auto; padding: var(--space-lg) var(--gutter);">
        <div style="text-align: center; margin-bottom: var(--space-lg);">
          <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1rem;">Curated Selection</p>
          <h2 class="reveal reveal--delay-1" style="font-family: var(--font-serif); font-weight: 300;">Notable Works</h2>
        </div>
        <div class="asset-grid">
          ${catAssets.map((asset, i) => `
            <div class="asset-card reveal reveal--delay-${(i % 3) + 1}" data-asset-id="${asset.id}">
              <div class="asset-card__image">
                <img src="${asset.image}" alt="${asset.image_alt}" loading="lazy" />
              </div>
              <div class="asset-card__info">
                <h3 class="asset-card__title">${asset.title_en}</h3>
                <p class="asset-card__meta">${asset.period}</p>
              </div>
            </div>
          `).join('')}
        </div>
      </section>
      ` : ''}

      <section class="related" style="max-width: var(--max-w); margin: 0 auto; padding: var(--space-lg) var(--gutter);">
        <p class="text-label reveal" style="text-align: center; margin-bottom: var(--space-md);">Continue Exploring</p>
        <div class="related__grid">
          ${related.map(r => `
            <a href="/discover/${r.slug}" data-link class="related__card reveal">
              <img src="${r.image}" alt="${r.image_alt}" loading="lazy" />
              <div class="related__card-overlay">
                <span class="related__card-name">${r.title_en}</span>
              </div>
            </a>
          `).join('')}
        </div>
      </section>

      ${renderFooter()}
    `;
  }

  /* ── Shared Components ── */
  function renderHeader() {
    const theme = document.documentElement.getAttribute('data-theme') || 'light';
    const icon = theme === 'dark' ? '○' : '●';
    return `
      <header class="header" id="site-header">
        <a href="/" data-link class="header__logo">Edition</a>
        <nav class="header__nav">
          <a href="/discover" data-link class="header__link">Collection</a>
          <a href="https://api.edition.sh/docs" target="_blank" class="header__link">API</a>
          <button class="header__theme-toggle" id="theme-toggle" aria-label="Toggle theme">
            <span style="font-size: 14px;">${icon}</span>
          </button>
        </nav>
      </header>
    `;
  }

  function renderFooter() {
    return `
      <footer class="footer">
        <div class="footer__inner">
          <span class="footer__brand">Edition</span>
          <div class="footer__links">
            <a href="/discover" data-link class="footer__link">Collection</a>
            <a href="https://api.edition.sh/docs" target="_blank" class="footer__link">API</a>
            <a href="https://github.com/hiroshic9-png/edition-api" target="_blank" class="footer__link">GitHub</a>
          </div>
        </div>
        <p class="footer__copy">
          © ${new Date().getFullYear()} EDITION — Japanese Cultural Assets Intelligence
        </p>
      </footer>
    `;
  }

  /* ── Scroll Reveal ── */
  function initRevealAnimations() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('reveal--visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.reveal:not(.reveal--visible)').forEach(el => {
      observer.observe(el);
    });
  }

  /* ── Header Scroll ── */
  function initHeaderScroll() {
    let ticking = false;
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          const header = document.getElementById('site-header');
          if (header) {
            const scrolled = window.scrollY > 80;
            header.classList.toggle('header--scrolled', scrolled);
            // Check if hero exists (home or category page)
            const hero = document.querySelector('.hero, .cat-hero');
            if (hero) {
              const heroBottom = hero.offsetTop + hero.offsetHeight;
              header.classList.toggle('header--over-hero', window.scrollY < heroBottom - 100);
            }
          }
          ticking = false;
        });
        ticking = true;
      }
    });
    // Initial state
    setTimeout(() => {
      const header = document.getElementById('site-header');
      const hero = document.querySelector('.hero, .cat-hero');
      if (header && hero) header.classList.add('header--over-hero');
    }, 50);
  }

  /* ── Theme ── */
  function initTheme() {
    const saved = localStorage.getItem('edition-theme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);

    document.addEventListener('click', (e) => {
      if (e.target.closest('#theme-toggle')) {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('edition-theme', next);
        const btn = document.getElementById('theme-toggle');
        if (btn) btn.querySelector('span').textContent = next === 'dark' ? '○' : '●';
      }
    });
  }

  /* ── Asset Detail Panel ── */
  function initAssetPanel() {
    document.addEventListener('click', (e) => {
      const card = e.target.closest('.asset-card');
      if (card) {
        const id = card.dataset.assetId;
        const asset = assetsData.find(a => a.id === id);
        if (asset) openAssetPanel(asset);
      }
      if (e.target.closest('.panel__close') || e.target.classList.contains('panel-backdrop')) {
        closeAssetPanel();
      }
    });
  }

  function openAssetPanel(asset) {
    const existing = document.querySelector('.panel-backdrop');
    if (existing) existing.remove();

    const panel = document.createElement('div');
    panel.className = 'panel-backdrop';
    panel.innerHTML = `
      <div class="panel">
        <button class="panel__close" aria-label="Close">×</button>
        <div class="panel__image">
          <img src="${asset.image}" alt="${asset.image_alt}" />
        </div>
        <div class="panel__content">
          <p class="text-label" style="color: var(--gold); margin-bottom: 0.75rem;">${asset.era}</p>
          <h2 class="panel__title">${asset.title_en}</h2>
          <p class="panel__title-jp">${asset.title_jp}</p>
          <div class="panel__meta">
            <div class="panel__meta-row"><span>Period</span><span>${asset.period}</span></div>
            <div class="panel__meta-row"><span>Medium</span><span>${asset.medium}</span></div>
            <div class="panel__meta-row"><span>Dimensions</span><span>${asset.dimensions}</span></div>
            <div class="panel__meta-row"><span>Origin</span><span>${asset.origin}</span></div>
          </div>
          <p class="panel__desc">${asset.description}</p>
          <p class="panel__sig">${asset.significance}</p>
          <div class="panel__source">
            <a href="${asset.source_url}" target="_blank" rel="noopener">
              View at ${asset.source} →
            </a>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(panel);
    requestAnimationFrame(() => panel.classList.add('panel-backdrop--open'));
    document.body.style.overflow = 'hidden';
  }

  function closeAssetPanel() {
    const backdrop = document.querySelector('.panel-backdrop');
    if (backdrop) {
      backdrop.classList.remove('panel-backdrop--open');
      setTimeout(() => backdrop.remove(), 400);
      document.body.style.overflow = '';
    }
  }

  /* ── Init ── */
  async function init() {
    await Promise.all([loadCategories(), loadAssets()]);
    initTheme();
    initHeaderScroll();
    initAssetPanel();
    const route = getRoute();
    renderPage(route);
    setTimeout(initRevealAnimations, 200);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
