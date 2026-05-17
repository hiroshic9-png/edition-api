/* ═══════════════════════════════════════════════════════════
   EDITION — Application Core
   SPA Router + Page Rendering + Animations
   ═══════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  let categoriesData = [];
  let assetsData = [];
  let _marketData = null;
  const app = document.getElementById('app');

  /* ── i18n System ── */
  let _locale = localStorage.getItem('edition-lang') || 'en';
  let _strings = {};
  let _i18nLoaded = false;

  async function loadI18n(lang) {
    try {
      const resp = await fetch(`./i18n/${lang}.json`);
      _strings = await resp.json();
      _locale = lang;
      _i18nLoaded = true;
      localStorage.setItem('edition-lang', lang);
      document.documentElement.lang = lang;
    } catch (e) {
      console.error(`Failed to load i18n/${lang}.json:`, e);
      if (lang !== 'en') await loadI18n('en'); // fallback
    }
  }

  function t(key) {
    const parts = key.split('.');
    let val = _strings;
    for (const p of parts) {
      if (val && typeof val === 'object' && p in val) val = val[p];
      else return key; // fallback: return key itself
    }
    return typeof val === 'string' ? val : key;
  }

  function toggleLang() {
    const next = _locale === 'en' ? 'ja' : 'en';
    loadI18n(next).then(() => {
      const route = getRoute();
      renderPage(route);
      setTimeout(initRevealAnimations, 100);
    });
  }

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

  async function loadMarketData() {
    try {
      const resp = await fetch('./data/market_intelligence.json');
      _marketData = await resp.json();
    } catch (e) {
      console.warn('Market data not available:', e);
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
    if (path === '/authenticate') return { page: 'authenticate' };
    if (path === '/prices') return { page: 'prices' };
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
      case 'authenticate': renderAuthenticate(); break;
      case 'prices': renderPrices(); break;
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
          <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1.5rem;">${t('hero.label')}</p>
          <h1 class="hero__title reveal reveal--delay-1">${t('hero.title_line1')}<br>${t('hero.title_line2')}</h1>
          <p class="hero__subtitle reveal reveal--delay-2">
            ${t('hero.subtitle')}
          </p>
          <div class="hero__scroll-hint reveal reveal--delay-3">
            <span class="hero__scroll-line"></span>
            <span>${t('hero.scroll')}</span>
          </div>
        </div>
      </section>

      <section class="section section--large">
        <div class="container" style="text-align:center; margin-bottom: var(--space-lg);">
          <p class="text-label reveal" style="margin-bottom: 1rem;">${t('home.collection_label')}</p>
          <h2 class="reveal reveal--delay-1" style="font-family: var(--font-serif); font-weight: 300;">
            ${t('home.collection_title')}
          </h2>
        </div>
        <div class="categories-grid">
          ${featured.map((cat, i) => renderCategoryCard(cat, i)).join('')}
        </div>
        <div style="text-align: center; margin-top: var(--space-lg);">
          <a href="/discover" data-link class="editorial__link reveal">
            ${t('home.view_all')}
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
              <p class="editorial__eyebrow">${t('home.featured')}</p>
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
              <p class="editorial__eyebrow">${t('home.featured')}</p>
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
            <p class="text-label" style="color: var(--gold); margin-bottom: 1.5rem;">${t('home.mission_label')}</p>
            <h2 class="mission__heading">
              ${t('home.mission_heading')}
            </h2>
            <p class="mission__body">
              ${t('home.mission_body')}
            </p>
          </div>
        </div>
      </section>

      <div class="divider divider--gold"></div>

      <section class="section section--large" style="background: var(--bg-alt);">
        <div class="container">
          <div class="auth-promo reveal">
            <div class="auth-promo__text">
              <p class="text-label" style="color: var(--gold); margin-bottom: 1rem;">${t('home.auth_label')}</p>
              <h2 style="font-family: var(--font-serif); font-weight: 300; margin-bottom: 1.5rem;">
                ${t('home.auth_title')}
              </h2>
              <p style="color: var(--text-secondary); line-height: 1.9; margin-bottom: 1.5rem;">
                ${t('home.auth_desc')}
              </p>
              <a href="/authenticate" data-link class="editorial__link">
                ${t('home.auth_explore')}
                <span class="editorial__link-arrow">\u2192</span>
              </a>
            </div>
            <div class="auth-promo__metrics reveal reveal--delay-1">
              <div class="auth-promo__metric">
                <span class="auth-promo__metric-value">4</span>
                <span class="auth-promo__metric-label">${t('home.auth_layers')}</span>
              </div>
              <div class="auth-promo__metric">
                <span class="auth-promo__metric-value">12</span>
                <span class="auth-promo__metric-label">${t('home.auth_categories')}</span>
              </div>
              <div class="auth-promo__metric">
                <span class="auth-promo__metric-value">24/7</span>
                <span class="auth-promo__metric-label">${t('home.auth_learning')}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Price Intelligence Promo -->
      <section class="section" style="padding: 5rem 2rem; background: var(--surface);">
        <div class="container" style="max-width: 1000px;">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center;">
            <div class="reveal">
              <p class="text-label" style="color: var(--gold); margin-bottom: 1rem;">${t('home.market_label')}</p>
              <h2 style="font-family: var(--font-serif); font-weight: 300; font-size: 1.8rem; margin-bottom: 1.5rem;">
                ${t('home.market_title')}
              </h2>
              <p style="color: var(--text-secondary); line-height: 1.9; margin-bottom: 1.5rem;">
                ${t('home.market_desc')}
              </p>
              <a href="/prices" data-link style="
                display: inline-block;
                padding: 0.75rem 2rem;
                border: 1px solid var(--gold);
                color: var(--gold);
                text-transform: uppercase;
                letter-spacing: 0.15em;
                font-size: 0.8rem;
                text-decoration: none;
                transition: all 0.3s ease;
              ">${t('home.market_cta')}</a>
            </div>
            <div class="reveal reveal--delay-1" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
              <div class="auth-promo__metric">
                <span class="auth-promo__metric-value">${_marketData ? Number(_marketData.stats.total_records).toLocaleString() : '23,121'}</span>
                <span class="auth-promo__metric-label">${t('home.market_records')}</span>
              </div>
              <div class="auth-promo__metric">
                <span class="auth-promo__metric-value">${_marketData ? _marketData.stats.auction_houses : '3'}</span>
                <span class="auth-promo__metric-label">${t('home.market_houses')}</span>
              </div>
              <div class="auth-promo__metric">
                <span class="auth-promo__metric-value">${_marketData ? '¥' + (Number(_marketData.stats.total_market_value) / 1e8).toFixed(0) + '億' : '¥463億'}</span>
                <span class="auth-promo__metric-label">${t('home.market_value')}</span>
              </div>
              <div class="auth-promo__metric">
                <span class="auth-promo__metric-value">${_marketData ? Number(_marketData.stats.total_artists).toLocaleString() : '3,509'}</span>
                <span class="auth-promo__metric-label">${t('home.market_artists')}</span>
              </div>
            </div>
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
          <p class="category-card__count">${t('home.explore')} →</p>
        </div>
      </a>
    `;
  }

  /* ── Discover Page ── */
  function renderDiscover() {
    app.innerHTML = `
      ${renderHeader()}

      <div class="page-header">
        <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1rem;">${t('discover.label')}</p>
        <h1 class="page-header__title reveal reveal--delay-1">${t('discover.title')}</h1>
        <p class="page-header__desc reveal reveal--delay-2">
          ${t('discover.desc')}
        </p>
        <div class="discover-search reveal reveal--delay-3">
          <input type="text" id="category-search" class="discover-search__input"
                 placeholder="${t('discover.search_placeholder')}" autocomplete="off" />
        </div>
      </div>

      <div class="categories-grid" id="categories-grid" style="max-width: var(--max-w); margin: 0 auto;">
        ${categoriesData.map((cat, i) => renderCategoryCard(cat, i)).join('')}
      </div>

      <div style="height: var(--space-xl);"></div>

      ${renderFooter()}
    `;

    // Search filter
    const searchInput = document.getElementById('category-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        document.querySelectorAll('.category-card').forEach(card => {
          const text = card.textContent.toLowerCase();
          card.style.display = text.includes(query) ? '' : 'none';
        });
      });
    }
  }

  /* ── Category Detail Page ── */
  async function renderCategory(slug) {
    const cat = categoriesData.find(c => c.slug === slug);
    if (!cat) { renderHome(); return; }

    const related = categoriesData.filter(c => c.slug !== slug).slice(0, 4);
    const catAssets = getAssetsForCategory(slug);

    // Fetch price data for this category
    let priceSection = '';
    try {
      const res = await fetch('/data/price_intelligence.json');
      const pd = await res.json();
      const catPrices = pd.results.filter(r => r.asset_category === slug);
      const catSummary = pd.categories.find(c => c.asset_category === slug);

      if (catPrices.length > 0 && catSummary) {
        const fmtUSD = (n) => n ? '$' + Number(n).toLocaleString() : '—';
        const fmtPrice = (n, cur) => {
          if (!n) return '—';
          if (cur === 'JPY') return '¥' + Number(n).toLocaleString();
          if (cur === 'GBP') return '£' + Number(n).toLocaleString();
          return '$' + Number(n).toLocaleString();
        };
        const recent = catPrices.slice(0, 3);

        priceSection = `
          <section class="section" style="max-width: var(--max-w); margin: 0 auto; padding: var(--space-lg) var(--gutter);">
            <div style="text-align: center; margin-bottom: var(--space-md);">
              <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1rem;">${t('category.market_label')}</p>
              <h2 class="reveal reveal--delay-1" style="font-family: var(--font-serif); font-weight: 300;">${t('category.market_title')}</h2>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1.5rem; max-width: 700px; margin: 0 auto 2rem;">
              <div class="auth-promo__metric reveal">
                <span class="auth-promo__metric-value">${catSummary.total_lots}</span>
                <span class="auth-promo__metric-label">${t('category.records')}</span>
              </div>
              <div class="auth-promo__metric reveal">
                <span class="auth-promo__metric-value">${fmtUSD(catSummary.avg_usd)}</span>
                <span class="auth-promo__metric-label">${t('category.avg_price')}</span>
              </div>
              <div class="auth-promo__metric reveal">
                <span class="auth-promo__metric-value">${fmtUSD(catSummary.max_usd)}</span>
                <span class="auth-promo__metric-label">${t('category.highest')}</span>
              </div>
            </div>
            <div style="display: grid; gap: 0.75rem; max-width: 700px; margin: 0 auto;">
              ${recent.map(r => `
                <div class="reveal" style="
                  display: grid; grid-template-columns: 1fr auto;
                  gap: 1rem; align-items: center;
                  padding: 1rem 1.5rem;
                  background: var(--surface);
                  border: 1px solid var(--border);
                  border-radius: 8px;
                ">
                  <div>
                    <div style="font-weight: 500; font-size: 0.9rem;">${r.title.length > 40 ? r.title.slice(0,40)+'…' : r.title}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">${r.auction_house} — ${r.auction_date}</div>
                  </div>
                  <div style="text-align: right;">
                    <div style="font-family: var(--font-serif); color: var(--gold);">${fmtPrice(r.hammer_price, r.currency)}</div>
                    <div style="font-size: 0.7rem; color: var(--text-secondary);">≈ ${fmtUSD(r.usd_equivalent)}</div>
                  </div>
                </div>
              `).join('')}
            </div>
            <div style="text-align: center; margin-top: 1.5rem;">
              <a href="/prices" data-link style="color: var(--gold); font-size: 0.85rem; text-decoration: none; letter-spacing: 0.08em; text-transform: uppercase;">${t('category.view_full')}</a>
            </div>
          </section>
        `;
      }
    } catch(e) { /* price data optional */ }

    app.innerHTML = `
      ${renderHeader()}

      <div class="cat-hero">
        <div class="cat-hero__bg">
          <img src="${cat.hero_image}" alt="${cat.image_alt}" loading="eager" />
        </div>
        <div class="cat-hero__content">
          <p class="cat-hero__eyebrow reveal">${t('category.eyebrow')}</p>
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

      ${priceSection}

      ${catAssets.length > 0 ? `
      <section class="section" style="max-width: var(--max-w); margin: 0 auto; padding: var(--space-lg) var(--gutter);">
        <div style="text-align: center; margin-bottom: var(--space-lg);">
          <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1rem;">${t('category.curated_label')}</p>
          <h2 class="reveal reveal--delay-1" style="font-family: var(--font-serif); font-weight: 300;">${t('category.curated_title')}</h2>
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
        <p class="text-label reveal" style="text-align: center; margin-bottom: var(--space-md);">${t('category.continue')}</p>
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

  /* ── Authenticate Page ── */
  /* ── Price Intelligence Page ── */
  async function renderPrices() {
    let priceData, marketData;
    try {
      const [priceRes, marketRes] = await Promise.all([
        fetch('/data/price_intelligence.json'),
        fetch('/data/market_intelligence.json').catch(() => null)
      ]);
      priceData = await priceRes.json();
      if (marketRes && marketRes.ok) marketData = await marketRes.json();
    } catch (e) {
      app.innerHTML = `${renderHeader()}<div style="padding: 6rem 2rem; text-align: center;"><p>Price data loading...</p></div>${renderFooter()}`;
      return;
    }

    // Merge: use market data for overview stats if available, fall back to price_intelligence
    const stats = marketData ? marketData.stats : priceData.stats;
    const { categories, highlights, results } = priceData;
    const topVolume = marketData ? marketData.top_artists_by_volume : [];
    const topValue = marketData ? marketData.top_artists_by_value : [];
    const houses = marketData ? marketData.auction_houses : [];


    const categoryNames = {
      swords: 'Swords & Armor', ceramics: 'Ceramics & Tea', ukiyoe: 'Ukiyo-e & Prints',
      painting: 'Painting & Calligraphy', lacquerware: 'Lacquerware & Maki-e',
      netsuke: 'Netsuke & Miniatures', textiles: 'Textiles & Kimono',
      metalwork: 'Metalwork & Ornaments', bonsai: 'Bonsai & Suiseki',
      sculpture: 'Sculpture & Buddhist Art', architecture: 'Architecture & Furnishing',
      contemporary: 'Contemporary Art'
    };

    function formatCurrency(amount, currency) {
      if (!amount) return '—';
      if (currency === 'JPY') return '¥' + Number(amount).toLocaleString();
      if (currency === 'GBP') return '£' + Number(amount).toLocaleString();
      return '$' + Number(amount).toLocaleString();
    }

    function formatUSD(amount) {
      if (!amount) return '—';
      return '$' + Number(amount).toLocaleString();
    }

    function formatJPY(amount) {
      if (!amount) return '—';
      const n = Number(amount);
      if (n >= 1e8) return '¥' + (n / 1e8).toFixed(1) + '億';
      if (n >= 1e4) return '¥' + (n / 1e4).toFixed(0) + '万';
      return '¥' + n.toLocaleString();
    }

    function formatJPYFull(amount) {
      if (!amount) return '—';
      return '¥' + Number(amount).toLocaleString();
    }

    app.innerHTML = `
      ${renderHeader()}

      <!-- Hero -->
      <section class="section" style="padding: 8rem 2rem 3rem; text-align: center;">
        <p class="text-label" style="color: var(--gold); margin-bottom: 1rem;">${t('prices.phase_label')}</p>
        <h1 style="font-family: var(--font-serif); font-weight: 300; font-size: clamp(2rem, 4vw, 3.2rem); margin-bottom: 1.5rem;">
          ${t('prices.title')}
        </h1>
        <p style="color: var(--text-secondary); max-width: 600px; margin: 0 auto; line-height: 1.8;">
          ${t('prices.desc')}
        </p>
      </section>

      <!-- Market Overview Stats -->
      <section class="section" style="padding: 2rem;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; max-width: 1000px; margin: 0 auto;">
          <div class="auth-promo__metric reveal" style="padding: 1.5rem;">
            <span class="auth-promo__metric-value">${stats.total_records}</span>
            <span class="auth-promo__metric-label">${t('prices.records')}</span>
          </div>
          <div class="auth-promo__metric reveal" style="padding: 1.5rem;">
            <span class="auth-promo__metric-value">${stats.categories_covered}</span>
            <span class="auth-promo__metric-label">${t('prices.categories_covered')}</span>
          </div>
          <div class="auth-promo__metric reveal" style="padding: 1.5rem;">
            <span class="auth-promo__metric-value">${stats.auction_houses}</span>
            <span class="auth-promo__metric-label">${t('prices.houses')}</span>
          </div>
          <div class="auth-promo__metric reveal" style="padding: 1.5rem;">
            <span class="auth-promo__metric-value" style="font-size: clamp(1.2rem, 2.5vw, 1.8rem);">${stats.total_market_value > 1e6 ? formatJPY(stats.total_market_value) : formatUSD(stats.total_market_value)}</span>
            <span class="auth-promo__metric-label">${t('prices.total_value')}</span>
          </div>
        </div>
      </section>

      <!-- Category Price Overview -->
      <section class="section" style="padding: 3rem 2rem;">
        <div style="max-width: 1000px; margin: 0 auto;">
          <p class="text-label" style="color: var(--gold); margin-bottom: 1rem;">${t('prices.analysis_label')}</p>
          <h2 style="font-family: var(--font-serif); font-weight: 300; margin-bottom: 2rem;">${t('prices.analysis_title')}</h2>
          
          <div style="display: grid; gap: 1rem;">
            ${categories.map(cat => `
              <div class="reveal" style="
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 1.5rem 2rem;
                display: grid;
                grid-template-columns: 1fr auto auto auto;
                gap: 2rem;
                align-items: center;
              ">
                <div>
                  <h3 style="font-family: var(--font-serif); font-weight: 400; font-size: 1.1rem; margin-bottom: 0.3rem;">
                    ${categoryNames[cat.asset_category] || cat.asset_category}
                  </h3>
                  <span style="color: var(--text-secondary); font-size: 0.85rem;">
                    ${cat.total_lots} ${cat.total_lots > 1 ? t('prices.lots_tracked') : t('prices.lot_tracked')}
                  </span>
                </div>
                <div style="text-align: right;">
                  <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em;">${t('prices.avg')}</div>
                  <div style="font-family: var(--font-serif); color: var(--gold); font-size: 1.1rem;">${formatUSD(cat.avg_usd)}</div>
                </div>
                <div style="text-align: right;">
                  <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em;">${t('prices.high')}</div>
                  <div style="font-family: var(--font-serif); font-size: 1.1rem;">${formatUSD(cat.max_usd)}</div>
                </div>
                <div style="text-align: right;">
                  <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em;">${t('prices.period')}</div>
                  <div style="font-size: 0.85rem; color: var(--text-secondary);">${cat.earliest?.slice(0,7) || '—'} → ${cat.latest?.slice(0,7) || '—'}</div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      </section>

      <!-- Notable Sales -->
      <section class="section" style="padding: 3rem 2rem; background: var(--surface);">
        <div style="max-width: 1000px; margin: 0 auto;">
          <p class="text-label" style="color: var(--gold); margin-bottom: 1rem;">${t('prices.highlights_label')}</p>
          <h2 style="font-family: var(--font-serif); font-weight: 300; margin-bottom: 2rem;">${t('prices.highlights_title')}</h2>
          
          <div style="display: grid; gap: 1.5rem;">
            ${highlights.map((h, i) => `
              <div class="reveal" style="
                background: var(--bg);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 2rem;
                position: relative;
                overflow: hidden;
              ">
                <div style="
                  position: absolute; top: 0; left: 0; bottom: 0; width: 4px;
                  background: linear-gradient(to bottom, var(--gold), transparent);
                "></div>
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
                  <div style="flex: 1; min-width: 250px;">
                    <span style="
                      font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;
                      color: var(--gold); background: var(--surface); padding: 0.2rem 0.6rem;
                      border-radius: 4px; margin-bottom: 0.5rem; display: inline-block;
                    ">${categoryNames[h.asset_category] || h.asset_category}</span>
                    <h3 style="font-family: var(--font-serif); font-weight: 400; font-size: 1.15rem; margin: 0.5rem 0;">
                      ${h.title}
                    </h3>
                    ${h.title_jp ? `<p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">${h.title_jp}</p>` : ''}
                    ${h.artist ? `<p style="font-size: 0.85rem; color: var(--text-secondary);">${h.artist}${h.artist_jp ? ' (' + h.artist_jp + ')' : ''}</p>` : ''}
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.5rem;">
                      ${h.auction_house} — ${h.auction_date}
                    </p>
                    ${h.certification ? `<p style="font-size: 0.8rem; color: var(--gold); margin-top: 0.3rem;">🏆 ${h.certification}</p>` : ''}
                  </div>
                  <div style="text-align: right;">
                    <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em;">${t('prices.hammer')}</div>
                    <div style="font-family: var(--font-serif); font-size: 1.4rem; color: var(--gold);">
                      ${formatCurrency(h.hammer_price, h.currency)}
                    </div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.3rem;">
                      ≈ ${formatUSD(h.usd_equivalent)} USD
                    </div>
                    ${h.premium_price ? `<div style="font-size: 0.75rem; color: var(--text-secondary);">w/ premium: ${formatCurrency(h.premium_price, h.currency)}</div>` : ''}
                  </div>
                </div>
                ${h.notes ? `<p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 1rem; font-style: italic; border-top: 1px solid var(--border); padding-top: 1rem;">${h.notes}</p>` : ''}
              </div>
            `).join('')}
          </div>
        </div>
      </section>

      ${topVolume.length > 0 ? `
      <!-- Top Artists -->
      <section class="section" style="padding: 3rem 2rem;">
        <div style="max-width: 1000px; margin: 0 auto;">
          <p class="text-label" style="color: var(--gold); margin-bottom: 1rem;">${t('prices.artist_label')}</p>
          <h2 style="font-family: var(--font-serif); font-weight: 300; margin-bottom: 2rem;">${t('prices.artist_title')}</h2>
          <div style="display: grid; gap: 0.5rem;">
            ${topVolume.slice(0, 10).map((a, i) => `
              <div class="reveal" style="
                display: grid; grid-template-columns: 2rem 1fr auto auto;
                gap: 1.5rem; align-items: center;
                padding: 1rem 1.5rem;
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 8px;
              ">
                <span style="font-family: var(--font-serif); color: var(--gold); font-size: 1.1rem; text-align: center;">${i + 1}</span>
                <div>
                  <div style="font-weight: 500; font-size: 0.95rem;">${a.artist}</div>
                  <div style="font-size: 0.75rem; color: var(--text-secondary);">${a.lot_count} ${t('prices.artist_lots')}</div>
                </div>
                <div style="text-align: right;">
                  <div style="font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em;">${t('prices.artist_avg')}</div>
                  <div style="font-family: var(--font-serif); color: var(--gold);">${formatJPYFull(a.avg_price_jpy)}</div>
                </div>
                <div style="text-align: right;">
                  <div style="font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em;">${t('prices.artist_median')}</div>
                  <div style="font-family: var(--font-serif);">${formatJPYFull(a.median_price_jpy)}</div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      </section>
      ` : ''}

      <!-- Results by Category -->
      <section class="section" style="padding: 3rem 2rem;">
        <div style="max-width: 1100px; margin: 0 auto;">
          <p class="text-label" style="color: var(--gold); margin-bottom: 1rem;">${t('prices.database_label')}</p>
          <h2 style="font-family: var(--font-serif); font-weight: 300; margin-bottom: 0.5rem;">${t('prices.database_title')}</h2>
          <p style="color: var(--text-secondary); margin-bottom: 2.5rem; font-size: 0.9rem;">${stats.total_records} ${t('prices.results_across')} ${stats.categories_covered} ${t('prices.categories_suffix')}</p>
          
          ${Object.keys(categoryNames).map(catKey => {
            const catResults = results.filter(r => r.asset_category === catKey);
            if (catResults.length === 0) return '';
            return `
              <details class="reveal" style="margin-bottom: 1rem; border: 1px solid var(--border); border-radius: 12px; overflow: hidden;" open>
                <summary style="
                  padding: 1.2rem 1.5rem;
                  background: var(--surface);
                  cursor: pointer;
                  display: flex;
                  justify-content: space-between;
                  align-items: center;
                  list-style: none;
                  font-family: var(--font-serif);
                  font-size: 1.1rem;
                ">
                  <span>${categoryNames[catKey]}</span>
                  <span style="font-size: 0.8rem; color: var(--text-secondary); font-family: var(--font-sans);">${catResults.length} records</span>
                </summary>
                <div style="overflow-x: auto;">
                  <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                      <tr style="border-bottom: 1px solid var(--border);">
                        <th style="text-align: left; padding: 0.8rem 1.2rem; font-weight: 500; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.08em; color: var(--text-secondary);">${t('prices.item')}</th>
                        <th style="text-align: left; padding: 0.8rem 1rem; font-weight: 500; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.08em; color: var(--text-secondary);">${t('prices.house')}</th>
                        <th style="text-align: left; padding: 0.8rem 1rem; font-weight: 500; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.08em; color: var(--text-secondary);">${t('prices.date')}</th>
                        <th style="text-align: right; padding: 0.8rem 1rem; font-weight: 500; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.08em; color: var(--text-secondary);">${t('prices.hammer')}</th>
                        <th style="text-align: right; padding: 0.8rem 1.2rem; font-weight: 500; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.08em; color: var(--text-secondary);">${t('prices.usd')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${catResults.map((r, i) => `
                        <tr style="border-bottom: 1px solid var(--border); ${i % 2 !== 0 ? 'background: var(--surface);' : ''}">
                          <td style="padding: 0.8rem 1.2rem;">
                            <div style="font-weight: 500; font-size: 0.95rem;">${r.title.length > 42 ? r.title.slice(0,42) + '…' : r.title}</div>
                            ${r.artist ? `<div style="font-size: 0.8rem; color: var(--text-secondary);">${r.artist}</div>` : ''}
                          </td>
                          <td style="padding: 0.8rem 1rem; color: var(--text-secondary); font-size: 0.9rem;">${r.auction_house}</td>
                          <td style="padding: 0.8rem 1rem; color: var(--text-secondary); font-size: 0.9rem; white-space: nowrap;">${r.auction_date}</td>
                          <td style="padding: 0.8rem 1rem; text-align: right; font-family: var(--font-serif); font-size: 1rem; white-space: nowrap;">${formatCurrency(r.hammer_price, r.currency)}</td>
                          <td style="padding: 0.8rem 1.2rem; text-align: right; color: var(--gold); font-family: var(--font-serif); font-size: 1rem; font-weight: 500; white-space: nowrap;">${formatUSD(r.usd_equivalent)}</td>
                        </tr>
                      `).join('')}
                    </tbody>
                  </table>
                </div>
              </details>
            `;
          }).join('')}
          
          <p style="text-align: center; color: var(--text-secondary); font-size: 0.8rem; margin-top: 2rem;">
            ${t('prices.data_note')}
            <br>${t('prices.last_updated')}: ${priceData.meta.generated_at?.slice(0,10) || '—'}
          </p>
        </div>
      </section>

      ${renderFooter()}
    `;
  }

  function renderAuthenticate() {

    app.innerHTML = `
      ${renderHeader()}

      <div class="auth-page">
        <section class="auth-hero">
          <div class="auth-hero__content">
            <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1.5rem; letter-spacing: 0.25em;">${t('authenticate.label')}</p>
            <h1 class="auth-hero__title reveal reveal--delay-1">${t('authenticate.title_line1')}<br>${t('authenticate.title_line2')}</h1>
            <p class="auth-hero__desc reveal reveal--delay-2">
              ${t('authenticate.desc')}
            </p>
          </div>
        </section>

        <section class="auth-philosophy">
          <div class="container">
            <div class="auth-philosophy__grid">
              <div class="auth-philosophy__text reveal">
                <p class="text-label" style="color: var(--gold); margin-bottom: 1rem;">${t('authenticate.approach_label')}</p>
                <h2 style="font-family: var(--font-serif); font-weight: 300; margin-bottom: 1.5rem;">${t('authenticate.approach_title_line1')}<br>${t('authenticate.approach_title_line2')}</h2>
                <p style="color: var(--text-secondary); line-height: 1.9; margin-bottom: 1.5rem;">
                  ${t('authenticate.approach_desc1')}
                </p>
                <p style="color: var(--text-secondary); line-height: 1.9;">
                  ${t('authenticate.approach_desc2')}
                </p>
              </div>
              <div class="auth-philosophy__visual reveal reveal--delay-1">
                <div class="auth-stat">
                  <span class="auth-stat__number">4</span>
                  <span class="auth-stat__label">${t('authenticate.layers')}</span>
                </div>
                <div class="auth-stat">
                  <span class="auth-stat__number">12</span>
                  <span class="auth-stat__label">${t('authenticate.categories')}</span>
                </div>
                <div class="auth-stat">
                  <span class="auth-stat__number">7+</span>
                  <span class="auth-stat__label">${t('authenticate.methods')}</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div class="divider divider--gold"></div>

        <section class="auth-layers">
          <div class="container">
            <div style="text-align: center; margin-bottom: var(--space-xl);">
              <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1rem;">${t('authenticate.framework_label')}</p>
              <h2 class="reveal reveal--delay-1" style="font-family: var(--font-serif); font-weight: 300;">
                ${t('authenticate.framework_title')}
              </h2>
            </div>

            <div class="auth-layers__stack">
              <div class="auth-layer reveal" data-layer="4">
                <div class="auth-layer__marker">
                  <span class="auth-layer__number">IV</span>
                  <span class="auth-layer__line"></span>
                </div>
                <div class="auth-layer__content">
                  <h3 class="auth-layer__title">${t('authenticate.layer4_title')}</h3>
                  <p class="auth-layer__subtitle">${t('authenticate.layer4_subtitle')}</p>
                  <p class="auth-layer__desc">
                    ${t('authenticate.layer4_desc')}
                  </p>
                  <div class="auth-layer__tags">
                    <span>Price Anomaly Detection</span>
                    <span>Duplicate Listing Analysis</span>
                    <span>Provenance Network Mapping</span>
                  </div>
                </div>
              </div>

              <div class="auth-layer reveal" data-layer="3">
                <div class="auth-layer__marker">
                  <span class="auth-layer__number">III</span>
                  <span class="auth-layer__line"></span>
                </div>
                <div class="auth-layer__content">
                  <h3 class="auth-layer__title">${t('authenticate.layer3_title')}</h3>
                  <p class="auth-layer__subtitle">${t('authenticate.layer3_subtitle')}</p>
                  <p class="auth-layer__desc">
                    ${t('authenticate.layer3_desc')}
                  </p>
                  <div class="auth-layer__tags">
                    <span>CNN Brushstroke Analysis</span>
                    <span>Hamon Pattern Classification</span>
                    <span>Glaze Spectral Matching</span>
                    <span>3D Surface Topology</span>
                  </div>
                </div>
              </div>

              <div class="auth-layer reveal" data-layer="2">
                <div class="auth-layer__marker">
                  <span class="auth-layer__number">II</span>
                  <span class="auth-layer__line"></span>
                </div>
                <div class="auth-layer__content">
                  <h3 class="auth-layer__title">${t('authenticate.layer2_title')}</h3>
                  <p class="auth-layer__subtitle">${t('authenticate.layer2_subtitle')}</p>
                  <p class="auth-layer__desc">
                    ${t('authenticate.layer2_desc')}
                  </p>
                  <div class="auth-layer__methods">
                    <div class="auth-method">
                      <span class="auth-method__name">XRF</span>
                      <span class="auth-method__desc">X-Ray Fluorescence — Elemental composition of pigments, metals, and glazes</span>
                    </div>
                    <div class="auth-method">
                      <span class="auth-method__name">FTIR</span>
                      <span class="auth-method__desc">Fourier Transform Infrared — Organic binders, resins, and lacquer analysis</span>
                    </div>
                    <div class="auth-method">
                      <span class="auth-method__name">Raman</span>
                      <span class="auth-method__desc">Raman Spectroscopy — Molecular-level pigment and mineral identification</span>
                    </div>
                    <div class="auth-method">
                      <span class="auth-method__name">IRR</span>
                      <span class="auth-method__desc">Infrared Reflectography — Underdrawings, pentimenti, and hidden alterations</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="auth-layer reveal" data-layer="1">
                <div class="auth-layer__marker">
                  <span class="auth-layer__number">I</span>
                  <span class="auth-layer__line"></span>
                </div>
                <div class="auth-layer__content">
                  <h3 class="auth-layer__title">${t('authenticate.layer1_title')}</h3>
                  <p class="auth-layer__subtitle">${t('authenticate.layer1_subtitle')}</p>
                  <p class="auth-layer__desc">
                    ${t('authenticate.layer1_desc')}
                  </p>
                  <div class="auth-layer__tags">
                    <span>NBTHK Certification</span>
                    <span>Catalogue Raisonné</span>
                    <span>Kiln Site Database</span>
                    <span>Hakogaki Analysis</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div class="divider divider--gold"></div>

        <section class="auth-threats">
          <div class="container">
            <div style="text-align: center; margin-bottom: var(--space-xl);">
              <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1rem;">${t('authenticate.defense_label')}</p>
              <h2 class="reveal reveal--delay-1" style="font-family: var(--font-serif); font-weight: 300;">
                ${t('authenticate.defense_title')}
              </h2>
              <p class="reveal reveal--delay-2" style="color: var(--text-secondary); max-width: 640px; margin: 1.5rem auto 0; line-height: 1.8;">
                ${t('authenticate.defense_desc')}
              </p>
            </div>

            <div class="auth-threats__grid">
              <div class="auth-threat-card reveal">
                <div class="auth-threat-card__level">${t('authenticate.threat1_level')}</div>
                <h3 class="auth-threat-card__title">${t('authenticate.threat1_title')}</h3>
                <p class="auth-threat-card__desc">
                  ${t('authenticate.threat1_desc')}
                </p>
                <p class="auth-threat-card__defense">${t('authenticate.threat1_defense')}</p>
              </div>

              <div class="auth-threat-card reveal reveal--delay-1">
                <div class="auth-threat-card__level">${t('authenticate.threat2_level')}</div>
                <h3 class="auth-threat-card__title">${t('authenticate.threat2_title')}</h3>
                <p class="auth-threat-card__desc">
                  ${t('authenticate.threat2_desc')}
                </p>
                <p class="auth-threat-card__defense">${t('authenticate.threat2_defense')}</p>
              </div>

              <div class="auth-threat-card reveal reveal--delay-2">
                <div class="auth-threat-card__level">${t('authenticate.threat3_level')}</div>
                <h3 class="auth-threat-card__title">${t('authenticate.threat3_title')}</h3>
                <p class="auth-threat-card__desc">
                  ${t('authenticate.threat3_desc')}
                </p>
                <p class="auth-threat-card__defense">${t('authenticate.threat3_defense')}</p>
              </div>
            </div>
          </div>
        </section>

        <section class="auth-cta">
          <div class="container" style="text-align: center;">
            <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1rem;">${t('authenticate.cta_label')}</p>
            <h2 class="reveal reveal--delay-1" style="font-family: var(--font-serif); font-weight: 300; margin-bottom: 1.5rem;">
              ${t('authenticate.cta_title')}
            </h2>
            <p class="reveal reveal--delay-2" style="color: var(--text-secondary); max-width: 560px; margin: 0 auto; line-height: 1.8;">
              ${t('authenticate.cta_desc')}
            </p>
          </div>
        </section>
      </div>

      ${renderFooter()}
    `;
  }

  /* ── Shared Components ── */
  function renderHeader() {
    const theme = document.documentElement.getAttribute('data-theme') || 'light';
    const icon = theme === 'dark' ? '○' : '●';
    const langLabel = _locale === 'en' ? 'JP' : 'EN';
    return `
      <header class="header" id="site-header">
        <a href="/" data-link class="header__logo">Edition</a>
        <nav class="header__nav">
          <a href="/discover" data-link class="header__link">${t('nav.collection')}</a>
          <a href="/authenticate" data-link class="header__link">${t('nav.authenticate')}</a>
          <a href="/prices" data-link class="header__link">${t('nav.prices')}</a>
          <button class="header__lang-toggle" id="lang-toggle" aria-label="Toggle language"
            style="background:none;border:1px solid var(--border);color:var(--text-secondary);padding:0.25rem 0.6rem;border-radius:4px;font-size:0.7rem;letter-spacing:0.1em;cursor:pointer;transition:all 0.3s ease;font-family:var(--font-sans);">${langLabel}</button>
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
            <a href="/discover" data-link class="footer__link">${t('nav.collection')}</a>
            <a href="/authenticate" data-link class="footer__link">${t('nav.authenticate')}</a>
            <a href="/prices" data-link class="footer__link">${t('nav.prices')}</a>
          </div>
        </div>
        <p class="footer__copy">
          © ${new Date().getFullYear()} EDITION — ${t('footer.copy')}
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
      if (e.target.closest('#lang-toggle')) {
        toggleLang();
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
            <div class="panel__meta-row"><span>${t('panel.period')}</span><span>${asset.period}</span></div>
            <div class="panel__meta-row"><span>${t('panel.medium')}</span><span>${asset.medium}</span></div>
            <div class="panel__meta-row"><span>${t('panel.dimensions')}</span><span>${asset.dimensions}</span></div>
            <div class="panel__meta-row"><span>${t('panel.origin')}</span><span>${asset.origin}</span></div>
          </div>
          <p class="panel__desc">${asset.description}</p>
          <p class="panel__sig">${asset.significance}</p>
          <div class="panel__source">
            <a href="${asset.source_url}" target="_blank" rel="noopener">
              ${t('panel.view_at')} ${asset.source} →
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
    await Promise.all([loadCategories(), loadAssets(), loadI18n(_locale), loadMarketData()]);
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
