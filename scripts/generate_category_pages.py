#!/usr/bin/env python3
"""
Generate individual category article pages for edition.sh
Reads data/categories.json and produces /categories/{slug}/index.html for each category.
"""
import json
import os
import html as html_mod

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_json(path):
    with open(os.path.join(REPO_ROOT, path)) as f:
        return json.load(f)


def fmt_jpy(n):
    if not n:
        return "¥0"
    if n >= 100_000_000:
        return f"¥{n / 100_000_000:.1f}億"
    if n >= 10_000:
        return f"¥{n / 10_000:.0f}万"
    return f"¥{n:,}"


def esc(text):
    return html_mod.escape(text) if text else ""


def generate_page(cat, all_categories):
    slug = cat["slug"]
    title_en = cat["title_en"]
    title_jp = cat["title_jp"]
    desc = cat.get("description", "")
    hero = cat.get("hero_image", "")
    image = cat.get("image", hero)
    image_alt = cat.get("image_alt", f"{title_en} — {title_jp}")
    image_credit = cat.get("image_credit", "")
    article = cat.get("article", {})
    intro = article.get("intro", "")
    sections = article.get("sections", [])

    # Build sections HTML
    sections_html = ""
    for i, sec in enumerate(sections):
        body = sec.get("body", "")
        if not body:
            continue
        # Convert line breaks to paragraphs
        paragraphs = [f"<p>{esc(p.strip())}</p>" for p in body.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [f"<p>{esc(body)}</p>"]
        sections_html += f"""
    <h2>{esc(sec['title'])}</h2>
    {''.join(paragraphs)}
"""

    # Related categories (exclude self)
    related = [c for c in all_categories if c["id"] != cat["id"]][:6]
    related_html = ""
    for r in related:
        r_hero = r.get("hero_image", "")
        related_html += f"""
      <a href="/categories/{r['slug']}" class="related-card">
        <div class="related-img" style="background-image:url('{r_hero}')"></div>
        <div class="related-info">
          <div class="related-title">{esc(r['title_jp'])}</div>
          <div class="related-en">{esc(r['title_en'])}</div>
        </div>
      </a>"""

    # Schema.org JSON-LD
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": f"{title_en} — {title_jp} | EDITION",
        "description": desc[:160],
        "url": f"https://edition.sh/categories/{slug}",
        "image": hero,
        "publisher": {"@type": "Organization", "name": "EDITION", "url": "https://edition.sh"},
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "EDITION", "item": "https://edition.sh"},
                {"@type": "ListItem", "position": 2, "name": "Categories", "item": "https://edition.sh/categories"},
                {"@type": "ListItem", "position": 3, "name": title_en, "item": f"https://edition.sh/categories/{slug}"},
            ],
        },
    }

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title_en)} — {esc(title_jp)} | EDITION Japanese Art Intelligence</title>
  <meta name="description" content="{esc(desc[:160])}">
  <meta name="robots" content="index, follow">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{esc(title_en)} — {esc(title_jp)} | EDITION">
  <meta property="og:description" content="{esc(desc[:160])}">
  <meta property="og:url" content="https://edition.sh/categories/{slug}">
  <meta property="og:image" content="{hero}">
  <meta property="og:site_name" content="EDITION">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="https://edition.sh/categories/{slug}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Inter:wght@300;400;500;600&family=Noto+Serif+JP:wght@300;400;500&family=Noto+Sans+JP:wght@300;400;500&display=swap" rel="stylesheet">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>◆</text></svg>">

  <script type="application/ld+json">
  {json.dumps(schema, ensure_ascii=False, indent=2)}
  </script>

  <style>
    *{{margin:0;padding:0;box-sizing:border-box}}
    :root{{
      --bg:#0C0C0C;--surface:rgba(255,255,255,0.03);--surface-2:rgba(255,255,255,0.05);
      --border:rgba(255,255,255,0.08);--border-gold:rgba(184,134,11,0.25);
      --text:#e0e0e0;--text-dim:rgba(255,255,255,0.4);--text-sec:rgba(255,255,255,0.55);
      --gold:#b8860b;--gold-dim:rgba(184,134,11,0.3);
      --font-serif:'Cormorant Garamond','Noto Serif JP',serif;
      --font-sans:'Inter','Noto Sans JP',sans-serif;
    }}
    body{{background:var(--bg);color:var(--text);font-family:var(--font-sans);line-height:1.8;-webkit-font-smoothing:antialiased}}
    a{{color:var(--gold);text-decoration:none;transition:opacity 0.2s}}
    a:hover{{opacity:0.8}}

    /* Header */
    .header{{position:fixed;top:0;left:0;right:0;z-index:100;padding:1.2rem 2rem;display:flex;align-items:center;justify-content:space-between;background:rgba(12,12,12,0.85);backdrop-filter:blur(20px);border-bottom:1px solid var(--border)}}
    .header__logo{{font-family:var(--font-serif);font-size:1.4rem;font-weight:300;color:#fff;text-decoration:none;letter-spacing:0.05em}}
    .header__nav{{display:flex;gap:2rem;align-items:center}}
    .header__link{{font-size:0.8rem;color:var(--text-dim);text-decoration:none;letter-spacing:0.08em;text-transform:uppercase;transition:color 0.3s}}
    .header__link:hover{{color:#fff;opacity:1}}
    .header__link--accent{{color:var(--gold)}}

    /* Hero */
    .hero{{position:relative;width:100%;height:clamp(300px,40vh,500px);overflow:hidden;margin-top:56px}}
    .hero__img{{width:100%;height:100%;object-fit:cover;filter:brightness(0.5)}}
    .hero__overlay{{position:absolute;bottom:0;left:0;right:0;padding:3rem 2rem;background:linear-gradient(transparent,rgba(12,12,12,0.95))}}
    .hero__label{{display:inline-block;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.15em;color:var(--gold);margin-bottom:0.5rem}}
    .hero__title{{font-family:var(--font-serif);font-weight:300;font-size:clamp(2rem,5vw,3.2rem);color:#fff;line-height:1.2}}
    .hero__jp{{font-family:var(--font-serif);font-weight:300;font-size:clamp(1.2rem,3vw,1.6rem);color:var(--text-dim);margin-top:0.2rem}}
    .hero__credit{{position:absolute;bottom:0.8rem;right:1rem;font-size:0.6rem;color:rgba(255,255,255,0.25)}}

    /* Page content */
    .page{{max-width:800px;margin:0 auto;padding:3rem 2rem 4rem}}

    /* Breadcrumb */
    .breadcrumb{{display:flex;gap:0.5rem;font-size:0.8rem;color:var(--text-dim);margin-bottom:2.5rem}}
    .breadcrumb a{{color:var(--text-dim);text-decoration:none}}
    .breadcrumb a:hover{{color:var(--gold)}}
    .breadcrumb .sep{{opacity:0.3}}

    /* Typography */
    h1{{font-family:var(--font-serif);font-weight:300;font-size:clamp(2rem,5vw,3rem);color:#fff;margin-bottom:0.5rem;line-height:1.2}}
    h2{{font-family:var(--font-serif);font-weight:400;font-size:1.4rem;margin:3rem 0 1.2rem;padding-bottom:0.6rem;border-bottom:1px solid var(--border);color:#fff}}
    h3{{font-size:1rem;font-weight:500;margin:2rem 0 0.8rem;color:#fff}}
    p{{color:var(--text-sec);margin-bottom:1.2rem;font-size:0.92rem}}
    .intro{{font-size:1rem;color:var(--text);line-height:2;margin-bottom:2rem;font-style:italic;border-left:3px solid var(--gold-dim);padding-left:1.5rem}}

    /* Related categories */
    .related-section{{margin-top:4rem;padding-top:2rem;border-top:1px solid var(--border)}}
    .related-section h2{{border-bottom:none;margin-bottom:1.5rem}}
    .related-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1rem}}
    .related-card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;overflow:hidden;transition:all 0.3s ease;text-decoration:none}}
    .related-card:hover{{border-color:var(--border-gold);transform:translateY(-2px);box-shadow:0 8px 30px rgba(0,0,0,0.3)}}
    .related-img{{height:120px;background-size:cover;background-position:center;filter:brightness(0.6);transition:filter 0.3s}}
    .related-card:hover .related-img{{filter:brightness(0.8)}}
    .related-info{{padding:1rem 1.2rem}}
    .related-title{{font-family:var(--font-serif);font-size:1.05rem;color:#fff;margin-bottom:0.2rem}}
    .related-en{{font-size:0.7rem;color:var(--text-dim);font-family:var(--font-serif);letter-spacing:0.04em}}

    /* Footer */
    .footer{{margin-top:4rem;padding:3rem 2rem;border-top:1px solid var(--border);text-align:center}}
    .footer__links{{display:flex;justify-content:center;gap:1.5rem;flex-wrap:wrap;margin-bottom:1rem}}
    .footer__link{{font-size:0.8rem;color:var(--text-dim);text-decoration:none;letter-spacing:0.05em}}
    .footer__link:hover{{color:var(--gold)}}
    .footer__copy{{font-size:0.75rem;color:var(--text-dim)}}

    @media(max-width:640px){{
      .hero__overlay{{padding:2rem 1.3rem}}
      .page{{padding:2rem 1.3rem 3rem}}
      .related-grid{{grid-template-columns:1fr 1fr}}
      .header__nav{{gap:1rem}}
      .header__link{{font-size:0.7rem}}
    }}
  </style>
</head>
<body>

  <header class="header">
    <a href="/" class="header__logo">Edition</a>
    <nav class="header__nav">
      <a href="/artists" class="header__link">Artists</a>
      <a href="/market" class="header__link">Market</a>
      <a href="/categories" class="header__link header__link--accent">Categories</a>
      <a href="/about" class="header__link">About</a>
      <a href="/docs" class="header__link">API</a>
    </nav>
  </header>

  <div class="hero">
    <img class="hero__img" src="{hero}" alt="{esc(image_alt)}" loading="eager">
    <div class="hero__overlay">
      <span class="hero__label">EDITION Categories</span>
      <div class="hero__title">{esc(title_en)}</div>
      <div class="hero__jp">{esc(title_jp)}</div>
    </div>
    {"<span class='hero__credit'>" + esc(image_credit) + "</span>" if image_credit else ""}
  </div>

  <div class="page">

    <nav class="breadcrumb">
      <a href="/">EDITION</a>
      <span class="sep">›</span>
      <a href="/categories">Categories</a>
      <span class="sep">›</span>
      <span>{esc(title_en)}</span>
    </nav>

    <div class="intro">{esc(intro)}</div>

{sections_html}

    <div class="related-section">
      <h2>Explore More Categories</h2>
      <div class="related-grid">
{related_html}
      </div>
    </div>

  </div>

  <footer class="footer">
    <div class="footer__links">
      <a href="/" class="footer__link">Home</a>
      <a href="/artists" class="footer__link">Artists</a>
      <a href="/market" class="footer__link">Market Report</a>
      <a href="/categories" class="footer__link">Categories</a>
      <a href="/about" class="footer__link">About</a>
      <a href="/docs" class="footer__link">API Docs</a>
    </div>
    <p class="footer__copy">© 2026 EDITION — Japanese Cultural Assets Intelligence</p>
  </footer>

</body>
</html>
"""
    return page_html


def main():
    data = load_json("data/categories.json")
    categories = data["categories"]

    count = 0
    for cat in categories:
        slug = cat["slug"]
        out_dir = os.path.join(REPO_ROOT, "categories", slug)
        os.makedirs(out_dir, exist_ok=True)

        page = generate_page(cat, categories)
        out_path = os.path.join(out_dir, "index.html")
        with open(out_path, "w") as f:
            f.write(page)
        count += 1
        print(f"  ✓ /categories/{slug}/index.html ({len(page):,} bytes)")

    print(f"\nGenerated {count} category pages.")


if __name__ == "__main__":
    main()
