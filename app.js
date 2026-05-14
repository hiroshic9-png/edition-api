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

      <div class="divider divider--gold"></div>

      <section class="section section--large" style="background: var(--bg-alt);">
        <div class="container">
          <div class="auth-promo reveal">
            <div class="auth-promo__text">
              <p class="text-label" style="color: var(--gold); margin-bottom: 1rem;">Authentication Intelligence</p>
              <h2 style="font-family: var(--font-serif); font-weight: 300; margin-bottom: 1.5rem;">
                Trust, Verified
              </h2>
              <p style="color: var(--text-secondary); line-height: 1.9; margin-bottom: 1.5rem;">
                EDITION employs a four-layer authentication framework combining traditional
                connoisseurship with AI-driven pattern recognition. Our proprietary system
                analyzes brushstrokes, hamon patterns, glaze compositions, and provenance
                chains to support expert authentication decisions.
              </p>
              <a href="/authenticate" data-link class="editorial__link">
                Explore Our Methodology
                <span class="editorial__link-arrow">\u2192</span>
              </a>
            </div>
            <div class="auth-promo__metrics reveal reveal--delay-1">
              <div class="auth-promo__metric">
                <span class="auth-promo__metric-value">4</span>
                <span class="auth-promo__metric-label">Verification Layers</span>
              </div>
              <div class="auth-promo__metric">
                <span class="auth-promo__metric-value">12</span>
                <span class="auth-promo__metric-label">Asset Categories</span>
              </div>
              <div class="auth-promo__metric">
                <span class="auth-promo__metric-value">24/7</span>
                <span class="auth-promo__metric-label">AI Learning Active</span>
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
              <p class="text-label" style="color: var(--gold); margin-bottom: 1rem;">Market Intelligence</p>
              <h2 style="font-family: var(--font-serif); font-weight: 300; font-size: 1.8rem; margin-bottom: 1.5rem;">
                Price Intelligence
              </h2>
              <p style="color: var(--text-secondary); line-height: 1.9; margin-bottom: 1.5rem;">
                The world's first comprehensive price database for Japanese art and antiques.
                Track auction results across 8 categories, from swords to contemporary art.
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
              ">Explore Market Data →</a>
            </div>
            <div class="reveal reveal--delay-1" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
              <div class="auth-promo__metric">
                <span class="auth-promo__metric-value">12</span>
                <span class="auth-promo__metric-label">Auction Records</span>
              </div>
              <div class="auth-promo__metric">
                <span class="auth-promo__metric-value">5</span>
                <span class="auth-promo__metric-label">Auction Houses</span>
              </div>
              <div class="auth-promo__metric">
                <span class="auth-promo__metric-value">$1.6M</span>
                <span class="auth-promo__metric-label">Tracked Value</span>
              </div>
              <div class="auth-promo__metric">
                <span class="auth-promo__metric-value">3</span>
                <span class="auth-promo__metric-label">Currencies</span>
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
        <div class="discover-search reveal reveal--delay-3">
          <input type="text" id="category-search" class="discover-search__input"
                 placeholder="Search categories\u2026" autocomplete="off" />
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
              <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1rem;">Market Intelligence</p>
              <h2 class="reveal reveal--delay-1" style="font-family: var(--font-serif); font-weight: 300;">Market Snapshot</h2>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1.5rem; max-width: 700px; margin: 0 auto 2rem;">
              <div class="auth-promo__metric reveal">
                <span class="auth-promo__metric-value">${catSummary.total_lots}</span>
                <span class="auth-promo__metric-label">Records</span>
              </div>
              <div class="auth-promo__metric reveal">
                <span class="auth-promo__metric-value">${fmtUSD(catSummary.avg_usd)}</span>
                <span class="auth-promo__metric-label">Avg Price</span>
              </div>
              <div class="auth-promo__metric reveal">
                <span class="auth-promo__metric-value">${fmtUSD(catSummary.max_usd)}</span>
                <span class="auth-promo__metric-label">Highest</span>
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
              <a href="/prices" data-link style="color: var(--gold); font-size: 0.85rem; text-decoration: none; letter-spacing: 0.08em; text-transform: uppercase;">View Full Market Data →</a>
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

      ${priceSection}

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

  /* ── Authenticate Page ── */
  /* ── Price Intelligence Page ── */
  async function renderPrices() {
    let priceData;
    try {
      const res = await fetch('/data/price_intelligence.json');
      priceData = await res.json();
    } catch (e) {
      app.innerHTML = `${renderHeader()}<div style="padding: 6rem 2rem; text-align: center;"><p>Price data loading...</p></div>${renderFooter()}`;
      return;
    }

    const { stats, categories, highlights, results } = priceData;

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

    app.innerHTML = `
      ${renderHeader()}

      <!-- Hero -->
      <section class="section" style="padding: 8rem 2rem 3rem; text-align: center;">
        <p class="text-label" style="color: var(--gold); margin-bottom: 1rem;">Phase 2 — Market Intelligence</p>
        <h1 style="font-family: var(--font-serif); font-weight: 300; font-size: clamp(2rem, 4vw, 3.2rem); margin-bottom: 1.5rem;">
          Price Intelligence
        </h1>
        <p style="color: var(--text-secondary); max-width: 600px; margin: 0 auto; line-height: 1.8;">
          Curated auction results and market data across Japanese cultural asset categories.
          Building the world's first comprehensive price database for Japanese art and antiques.
        </p>
      </section>

      <!-- Market Overview Stats -->
      <section class="section" style="padding: 2rem;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; max-width: 1000px; margin: 0 auto;">
          <div class="auth-promo__metric reveal" style="padding: 1.5rem;">
            <span class="auth-promo__metric-value">${stats.total_records}</span>
            <span class="auth-promo__metric-label">Auction Records</span>
          </div>
          <div class="auth-promo__metric reveal" style="padding: 1.5rem;">
            <span class="auth-promo__metric-value">${stats.categories_covered}</span>
            <span class="auth-promo__metric-label">Categories</span>
          </div>
          <div class="auth-promo__metric reveal" style="padding: 1.5rem;">
            <span class="auth-promo__metric-value">${stats.auction_houses}</span>
            <span class="auth-promo__metric-label">Auction Houses</span>
          </div>
          <div class="auth-promo__metric reveal" style="padding: 1.5rem;">
            <span class="auth-promo__metric-value" style="font-size: clamp(1.2rem, 2.5vw, 1.8rem);">${formatUSD(stats.total_market_value)}</span>
            <span class="auth-promo__metric-label">Total Tracked Value</span>
          </div>
        </div>
      </section>

      <!-- Category Price Overview -->
      <section class="section" style="padding: 3rem 2rem;">
        <div style="max-width: 1000px; margin: 0 auto;">
          <p class="text-label" style="color: var(--gold); margin-bottom: 1rem;">Category Analysis</p>
          <h2 style="font-family: var(--font-serif); font-weight: 300; margin-bottom: 2rem;">Market by Category</h2>
          
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
                    ${cat.total_lots} lot${cat.total_lots > 1 ? 's' : ''} tracked
                  </span>
                </div>
                <div style="text-align: right;">
                  <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em;">Avg</div>
                  <div style="font-family: var(--font-serif); color: var(--gold); font-size: 1.1rem;">${formatUSD(cat.avg_usd)}</div>
                </div>
                <div style="text-align: right;">
                  <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em;">High</div>
                  <div style="font-family: var(--font-serif); font-size: 1.1rem;">${formatUSD(cat.max_usd)}</div>
                </div>
                <div style="text-align: right;">
                  <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em;">Period</div>
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
          <p class="text-label" style="color: var(--gold); margin-bottom: 1rem;">Highlights</p>
          <h2 style="font-family: var(--font-serif); font-weight: 300; margin-bottom: 2rem;">Notable Sales</h2>
          
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
                    <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em;">Hammer</div>
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

      <!-- Results by Category -->
      <section class="section" style="padding: 3rem 2rem;">
        <div style="max-width: 1100px; margin: 0 auto;">
          <p class="text-label" style="color: var(--gold); margin-bottom: 1rem;">Database</p>
          <h2 style="font-family: var(--font-serif); font-weight: 300; margin-bottom: 0.5rem;">Auction Records</h2>
          <p style="color: var(--text-secondary); margin-bottom: 2.5rem; font-size: 0.9rem;">${stats.total_records} results across ${stats.categories_covered} categories</p>
          
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
                        <th style="text-align: left; padding: 0.8rem 1.2rem; font-weight: 500; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.08em; color: var(--text-secondary);">Item</th>
                        <th style="text-align: left; padding: 0.8rem 1rem; font-weight: 500; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.08em; color: var(--text-secondary);">House</th>
                        <th style="text-align: left; padding: 0.8rem 1rem; font-weight: 500; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.08em; color: var(--text-secondary);">Date</th>
                        <th style="text-align: right; padding: 0.8rem 1rem; font-weight: 500; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.08em; color: var(--text-secondary);">Hammer</th>
                        <th style="text-align: right; padding: 0.8rem 1.2rem; font-weight: 500; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.08em; color: var(--text-secondary);">USD</th>
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
            Data sourced from public auction records. Prices shown are hammer prices before buyer's premium unless noted.
            <br>Last updated: ${priceData.meta.generated_at?.slice(0,10) || '—'}
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
            <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1.5rem; letter-spacing: 0.25em;">Authentication Intelligence</p>
            <h1 class="auth-hero__title reveal reveal--delay-1">The Science<br>of Certainty</h1>
            <p class="auth-hero__desc reveal reveal--delay-2">
              Four layers of verification — from the connoisseur's trained eye to AI-driven pattern recognition.
              EDITION builds trust through rigorous, transparent methodology.
            </p>
          </div>
        </section>

        <section class="auth-philosophy">
          <div class="container">
            <div class="auth-philosophy__grid">
              <div class="auth-philosophy__text reveal">
                <p class="text-label" style="color: var(--gold); margin-bottom: 1rem;">Our Approach</p>
                <h2 style="font-family: var(--font-serif); font-weight: 300; margin-bottom: 1.5rem;">Human Expertise,<br>Augmented by Technology</h2>
                <p style="color: var(--text-secondary); line-height: 1.9; margin-bottom: 1.5rem;">
                  In the tradition of the world's leading scientific research departments and provenance methodologies,
                  EDITION employs a multi-layered authentication framework. AI is never the sole arbiter —
                  it is a powerful lens that reveals what the human eye alone cannot see.
                </p>
                <p style="color: var(--text-secondary); line-height: 1.9;">
                  Every assessment is transparent. Every methodology is documented.
                  Every conclusion is defensible.
                </p>
              </div>
              <div class="auth-philosophy__visual reveal reveal--delay-1">
                <div class="auth-stat">
                  <span class="auth-stat__number">4</span>
                  <span class="auth-stat__label">Verification Layers</span>
                </div>
                <div class="auth-stat">
                  <span class="auth-stat__number">12</span>
                  <span class="auth-stat__label">Asset Categories</span>
                </div>
                <div class="auth-stat">
                  <span class="auth-stat__number">7+</span>
                  <span class="auth-stat__label">Scientific Methods</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div class="divider divider--gold"></div>

        <section class="auth-layers">
          <div class="container">
            <div style="text-align: center; margin-bottom: var(--space-xl);">
              <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1rem;">Framework</p>
              <h2 class="reveal reveal--delay-1" style="font-family: var(--font-serif); font-weight: 300;">
                Four-Layer Authentication Architecture
              </h2>
            </div>

            <div class="auth-layers__stack">
              <div class="auth-layer reveal" data-layer="4">
                <div class="auth-layer__marker">
                  <span class="auth-layer__number">IV</span>
                  <span class="auth-layer__line"></span>
                </div>
                <div class="auth-layer__content">
                  <h3 class="auth-layer__title">Market Intelligence</h3>
                  <p class="auth-layer__subtitle">Anomaly Detection & Pattern Analysis</p>
                  <p class="auth-layer__desc">
                    Statistical analysis of listing patterns across global auction houses.
                    Detection of duplicate listings, price anomalies, and provenance gaps
                    that may indicate fraudulent activity.
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
                  <h3 class="auth-layer__title">AI Forensics</h3>
                  <p class="auth-layer__subtitle">Pattern Recognition & Deep Analysis</p>
                  <p class="auth-layer__desc">
                    Convolutional neural networks trained on authenticated works analyze
                    stylistic fingerprints invisible to the human eye — brushstroke patterns,
                    hamon classifications in swords, glaze composition signatures in ceramics.
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
                  <h3 class="auth-layer__title">Scientific Verification</h3>
                  <p class="auth-layer__subtitle">Material & Compositional Analysis</p>
                  <p class="auth-layer__desc">
                    Following the standards established by the world's leading auction house laboratories,
                    we employ non-destructive scientific testing to verify material authenticity.
                    Period-inconsistent materials are identified with certainty.
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
                  <h3 class="auth-layer__title">Connoisseurship & Provenance</h3>
                  <p class="auth-layer__subtitle">Expert Evaluation & Historical Documentation</p>
                  <p class="auth-layer__desc">
                    The foundation of all authentication. Trained specialists evaluate works
                    through direct examination — assessing form, technique, patina, and the
                    subtle markers that distinguish a master's hand. Provenance is traced through
                    historical records, exhibition catalogues, and institutional archives.
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
              <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1rem;">Defense</p>
              <h2 class="reveal reveal--delay-1" style="font-family: var(--font-serif); font-weight: 300;">
                Evolving Threat Landscape
              </h2>
              <p class="reveal reveal--delay-2" style="color: var(--text-secondary); max-width: 640px; margin: 1.5rem auto 0; line-height: 1.8;">
                As generative AI enables increasingly sophisticated forgeries,
                EDITION maintains continuous intelligence on emerging threats.
              </p>
            </div>

            <div class="auth-threats__grid">
              <div class="auth-threat-card reveal">
                <div class="auth-threat-card__level">Critical</div>
                <h3 class="auth-threat-card__title">Provenance Fabrication</h3>
                <p class="auth-threat-card__desc">
                  LLM-generated sales records, certificates, and ownership histories
                  that bypass traditional document verification.
                </p>
                <p class="auth-threat-card__defense">Defense: Blockchain-anchored provenance chain + document metadata forensics</p>
              </div>

              <div class="auth-threat-card reveal reveal--delay-1">
                <div class="auth-threat-card__level">High</div>
                <h3 class="auth-threat-card__title">AI Style Mimicry</h3>
                <p class="auth-threat-card__desc">
                  GANs and diffusion models trained to replicate specific artistic styles,
                  guiding physical reproduction of paintings and prints.
                </p>
                <p class="auth-threat-card__defense">Defense: Multi-modal analysis — frequency domain + material verification</p>
              </div>

              <div class="auth-threat-card reveal reveal--delay-2">
                <div class="auth-threat-card__level">Emerging</div>
                <h3 class="auth-threat-card__title">Precision Replication</h3>
                <p class="auth-threat-card__desc">
                  CT-scan data combined with AI-optimized CNC/robotics
                  to produce structurally accurate physical reproductions.
                </p>
                <p class="auth-threat-card__defense">Defense: Molecular-level patina analysis + nanoscale aging verification</p>
              </div>
            </div>
          </div>
        </section>

        <section class="auth-cta">
          <div class="container" style="text-align: center;">
            <p class="text-label reveal" style="color: var(--gold); margin-bottom: 1rem;">Coming Soon</p>
            <h2 class="reveal reveal--delay-1" style="font-family: var(--font-serif); font-weight: 300; margin-bottom: 1.5rem;">
              EDITION Certified
            </h2>
            <p class="reveal reveal--delay-2" style="color: var(--text-secondary); max-width: 560px; margin: 0 auto; line-height: 1.8;">
              A new standard in Japanese cultural asset authentication.
              Transparent methodology. Immutable records. Absolute confidence.
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
    return `
      <header class="header" id="site-header">
        <a href="/" data-link class="header__logo">Edition</a>
        <nav class="header__nav">
          <a href="/discover" data-link class="header__link">Collection</a>
          <a href="/authenticate" data-link class="header__link">Authenticate</a>
          <a href="/prices" data-link class="header__link">Prices</a>
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
            <a href="/authenticate" data-link class="footer__link">Authenticate</a>
            <a href="/prices" data-link class="footer__link">Prices</a>
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
