#!/usr/bin/env python3
"""Generate static artist pages for SEO (edition.sh/artist/{slug}/index.html)

Each page contains:
- Full HTML with SEO meta, OGP, JSON-LD (for Google crawlers)  
- SPA redirect script (so the app.js router handles actual rendering)
- Enough static content for search engines to index even without JS
"""
import json, os, re, unicodedata, html

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "top_artists.json")
ARTISTS_DIR = os.path.join(BASE, "artist")

def slugify(name):
    """Create URL-safe slug from artist name."""
    # Remove full-width spaces, normalize
    n = name.replace("\u3000", "-").replace(" ", "-").strip()
    n = re.sub(r'-+', '-', n).strip('-')
    return n

def fmt_jpy(v):
    if not v: return "—"
    v = int(v)
    if v >= 100_000_000: return f"¥{v/100_000_000:.1f}億"
    if v >= 10_000: return f"¥{v:,}"
    return f"¥{v:,}"

def movement_ja(m):
    mapping = {
        "pop_art": "ポップアート", "contemporary": "現代美術", "sculpture": "彫刻",
        "nihonga": "日本画", "postwar": "戦後美術", "modern": "近代美術",
        "impressionism": "印象派", "surrealism": "シュルレアリスム",
        "abstract": "抽象美術", "mingei": "民藝", "ceramics": "陶芸",
        "ukiyo-e": "浮世絵", "print": "版画",
    }
    return mapping.get(m, m)

def generate_page(artist):
    name = artist["name"]
    slug = slugify(name)
    roman = artist.get("roman_name", "")
    lots = artist["lot_count"]
    avg = artist["avg_price"]
    median = artist["median_price"]
    max_p = artist.get("max_price", 0)
    total_val = artist.get("total_value", 0)
    n_houses = artist.get("n_houses", 1)
    houses = artist.get("houses", [])
    birth = artist.get("birth_year", "")
    death = artist.get("death_year", "")
    fields = artist.get("fields", [])
    movements = artist.get("movements", [])
    birth_place = artist.get("birth_place", "")
    daj_url = artist.get("daj_url", "")
    wiki_langs = artist.get("wiki_lang_count", 0)
    
    # Construct lifespan
    lifespan = ""
    if birth:
        lifespan = f"{birth}年"
        if death:
            lifespan += f" – {death}年"
        elif artist.get("is_deceased"):
            lifespan += " – "
        else:
            lifespan += " –"
    
    # Title
    title_name = f"{name}" + (f" ({roman})" if roman else "")
    page_title = f"{title_name} — オークション相場・落札価格分析 | EDITION"
    meta_desc = f"{name}のオークション落札価格データ。{lots:,}件の取引実績、平均落札価格{fmt_jpy(avg)}、最高額{fmt_jpy(max_p)}。{n_houses}つのオークションハウスの横断分析。"
    
    # Houses string
    houses_str = "、".join(houses) if houses else f"{n_houses}社"
    
    # Fields string
    fields_str = "、".join(fields) if fields else ""
    movements_str = "、".join(movement_ja(m) for m in movements) if movements else ""
    
    # JSON-LD structured data (Person schema)
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": name,
        "url": f"https://edition.sh/artist/{slug}",
    }
    if roman:
        json_ld["alternateName"] = roman
    if birth:
        json_ld["birthDate"] = str(birth)
    if death:
        json_ld["deathDate"] = str(death)
    if birth_place:
        json_ld["birthPlace"] = {"@type": "Place", "name": birth_place}
    if fields:
        json_ld["jobTitle"] = "Artist"
        json_ld["description"] = f"{name}。{fields_str}。" + (f"{movements_str}。" if movements_str else "")
    
    # Authority links
    auth_links = ""
    auths = artist.get("authorities", {})
    if auths.get("wikidata"):
        auth_links += f'<a href="https://www.wikidata.org/wiki/{auths["wikidata"]}" rel="noopener" target="_blank">Wikidata</a> · '
    if auths.get("viaf"):
        auth_links += f'<a href="https://viaf.org/viaf/{auths["viaf"]}" rel="noopener" target="_blank">VIAF</a> · '
    if auths.get("ulan"):
        auth_links += f'<a href="https://www.getty.edu/vow/ULANFullDisplay?find=&role=&nation=&prev_page=1&subjectid={auths["ulan"]}" rel="noopener" target="_blank">ULAN</a> · '
    if daj_url:
        auth_links += f'<a href="{daj_url}" rel="noopener" target="_blank">NCAR Art Platform Japan</a>'
    auth_links = auth_links.rstrip(" · ")
    
    page_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(page_title)}</title>
  <meta name="description" content="{html.escape(meta_desc)}">
  <meta name="robots" content="index, follow">
  
  <!-- Open Graph -->
  <meta property="og:type" content="profile">
  <meta property="og:title" content="{html.escape(title_name)} — オークション相場 | EDITION">
  <meta property="og:description" content="{html.escape(meta_desc)}">
  <meta property="og:url" content="https://edition.sh/artist/{slug}">
  <meta property="og:site_name" content="EDITION">
  <meta property="og:locale" content="ja_JP">
  <meta property="og:locale:alternate" content="en_US">
  
  <!-- Twitter -->
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{html.escape(title_name)} — オークション相場 | EDITION">
  <meta name="twitter:description" content="{html.escape(meta_desc)}">
  
  <link rel="canonical" href="https://edition.sh/artist/{slug}">
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500&family=Inter:wght@300;400;500&family=Noto+Serif+JP:wght@300;400;500&family=Noto+Sans+JP:wght@300;400;500&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="/style.css?v=08a">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>◆</text></svg>">
  
  <!-- Structured Data -->
  <script type="application/ld+json">
  {json.dumps(json_ld, ensure_ascii=False, indent=2)}
  </script>
  
  <style>
    .artist-seo {{ 
      max-width: 900px; margin: 0 auto; padding: 6rem 2rem 4rem;
      font-family: var(--font-sans, 'Inter', 'Noto Sans JP', sans-serif);
      color: var(--text, #1a1a1a);
    }}
    .artist-seo h1 {{
      font-family: var(--font-serif, 'Cormorant Garamond', 'Noto Serif JP', serif);
      font-weight: 300; font-size: clamp(2rem, 5vw, 3rem);
      margin-bottom: 0.25rem; line-height: 1.2;
    }}
    .artist-seo .roman {{ color: var(--text-secondary, #888); font-size: 1.1rem; margin-bottom: 2rem; }}
    .artist-seo .lifespan {{ color: var(--text-secondary, #888); font-size: 0.9rem; }}
    .artist-seo .stats-grid {{
      display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 1.5rem; margin: 2.5rem 0;
    }}
    .artist-seo .stat {{
      background: var(--surface, #f8f8f8); border: 1px solid var(--border, #e0e0e0);
      border-radius: 12px; padding: 1.5rem; text-align: center;
    }}
    .artist-seo .stat-value {{
      font-family: var(--font-serif); font-size: 1.5rem; 
      color: var(--gold, #b8860b); display: block; margin-bottom: 0.3rem;
    }}
    .artist-seo .stat-label {{
      font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em;
      color: var(--text-secondary, #888);
    }}
    .artist-seo .section-title {{
      font-family: var(--font-serif); font-weight: 400; font-size: 1.3rem;
      margin: 3rem 0 1rem; padding-bottom: 0.5rem;
      border-bottom: 1px solid var(--border, #e0e0e0);
    }}
    .artist-seo .meta-line {{
      display: flex; gap: 0.5rem; align-items: baseline;
      padding: 0.6rem 0; border-bottom: 1px solid var(--border, #f0f0f0);
      font-size: 0.9rem;
    }}
    .artist-seo .meta-key {{ color: var(--text-secondary, #888); min-width: 140px; flex-shrink: 0; }}
    .artist-seo .meta-val {{ font-weight: 500; }}
    .artist-seo .auth-links {{ margin-top: 1rem; font-size: 0.8rem; }}
    .artist-seo .auth-links a {{ color: var(--gold, #b8860b); text-decoration: none; }}
    .artist-seo .auth-links a:hover {{ text-decoration: underline; }}
    .artist-seo .back-link {{
      display: inline-block; margin-bottom: 2rem; font-size: 0.85rem;
      color: var(--text-secondary, #888); text-decoration: none;
    }}
    .artist-seo .back-link:hover {{ color: var(--gold, #b8860b); }}
    .artist-seo .cta {{
      margin-top: 3rem; padding: 2rem; background: var(--surface, #f8f8f8);
      border: 1px solid var(--border, #e0e0e0); border-radius: 12px;
      text-align: center;
    }}
    .artist-seo .cta a {{
      color: var(--gold, #b8860b); text-decoration: none; font-weight: 500;
    }}
    .artist-seo footer {{
      margin-top: 4rem; padding-top: 2rem;
      border-top: 1px solid var(--border, #e0e0e0);
      font-size: 0.75rem; color: var(--text-secondary, #888);
      text-align: center;
    }}
    @media (prefers-color-scheme: dark) {{
      .artist-seo {{ color: #e0e0e0; }}
      .artist-seo .stat {{ background: #1a1a1a; border-color: #333; }}
    }}
  </style>
</head>
<body>
  <div class="artist-seo">
    <a href="/" class="back-link">← EDITION トップへ戻る</a>
    
    <h1>{html.escape(name)}</h1>
    {f'<p class="roman">{html.escape(roman)}</p>' if roman else ''}
    {f'<p class="lifespan">{html.escape(lifespan)}' + (f' · {html.escape(birth_place)}' if birth_place else '') + '</p>' if lifespan else ''}
    
    <div class="stats-grid">
      <div class="stat">
        <span class="stat-value">{lots:,}</span>
        <span class="stat-label">オークション出品数</span>
      </div>
      <div class="stat">
        <span class="stat-value">{fmt_jpy(avg)}</span>
        <span class="stat-label">平均落札価格</span>
      </div>
      <div class="stat">
        <span class="stat-value">{fmt_jpy(median)}</span>
        <span class="stat-label">中央値</span>
      </div>
      <div class="stat">
        <span class="stat-value">{fmt_jpy(max_p)}</span>
        <span class="stat-label">最高額</span>
      </div>
      <div class="stat">
        <span class="stat-value">{houses_str}</span>
        <span class="stat-label">取扱ハウス</span>
      </div>
      <div class="stat">
        <span class="stat-value">{fmt_jpy(total_val)}</span>
        <span class="stat-label">総取引額</span>
      </div>
    </div>
    
    {f'''<h2 class="section-title">アーティスト情報</h2>
    <div>
      {f'<div class="meta-line"><span class="meta-key">活動分野</span><span class="meta-val">{html.escape(fields_str)}</span></div>' if fields_str else ''}
      {f'<div class="meta-line"><span class="meta-key">芸術運動</span><span class="meta-val">{html.escape(movements_str)}</span></div>' if movements_str else ''}
      {f'<div class="meta-line"><span class="meta-key">出身地</span><span class="meta-val">{html.escape(birth_place)}</span></div>' if birth_place else ''}
      {f'<div class="meta-line"><span class="meta-key">Wikipedia</span><span class="meta-val">{wiki_langs}言語版に掲載</span></div>' if wiki_langs > 0 else ''}
    </div>''' if any([fields_str, movements_str, birth_place, wiki_langs]) else ''}
    
    <h2 class="section-title">市場概要</h2>
    <p style="line-height: 1.8; color: var(--text-secondary, #555);">
      {html.escape(name)}の作品は、日本国内{n_houses}つの主要オークションハウス（{html.escape(houses_str)}）で合計{lots:,}件の落札実績があります。
      平均落札価格は{fmt_jpy(avg)}、中央値は{fmt_jpy(median)}です。
      {f'過去の最高落札価格は{fmt_jpy(max_p)}を記録しています。' if max_p else ''}
      {f'総取引額は{fmt_jpy(total_val)}に達します。' if total_val else ''}
    </p>
    <p style="line-height: 1.8; color: var(--text-secondary, #555); margin-top: 1rem;">
      このデータはEDITIONのKANTEISHI（鑑定士）AIエンジンにより、SBI Art Auction、毎日オークション、シンワオークション
      の落札記録を横断的に分析したものです。ヘドニック価格モデル v0.8（R²=0.898）による推定価格算出にも活用されています。
    </p>
    
    {f'<div class="auth-links"><strong>典拠データ：</strong>{auth_links}</div>' if auth_links else ''}
    
    <div class="cta">
      <p style="margin-bottom: 0.5rem; font-size: 0.9rem; color: var(--text-secondary, #888);">KANTEISHI Intelligence Engine</p>
      <p style="font-family: var(--font-serif); font-size: 1.1rem;">
        <a href="/prices">全{lots:,}件の落札データを見る →</a>
      </p>
      <p style="font-size: 0.8rem; color: var(--text-secondary, #888); margin-top: 0.5rem;">
        49,968件 · 7,258名のアーティスト · 3社横断分析
      </p>
    </div>
    
    <footer>
      <p>© 2026 EDITION — Japanese Cultural Assets Intelligence</p>
      <p style="margin-top: 0.3rem;">
        <a href="/" style="color: var(--text-secondary, #888); text-decoration: none;">トップ</a> · 
        <a href="/prices" style="color: var(--text-secondary, #888); text-decoration: none;">落札価格</a> · 
        <a href="/kanteishi" style="color: var(--text-secondary, #888); text-decoration: none;">KANTEISHI</a>
      </p>
    </footer>
  </div>
  
  <!-- SPA redirect for JavaScript-enabled browsers -->
  <script>
    // If the SPA app.js is available, redirect to the SPA route
    if (window.history && window.history.replaceState) {{
      // Let the static content be visible for bots, but
      // for real users, load the full SPA experience
      var loadSPA = document.createElement('script');
      loadSPA.src = '/app.js?v=08a';
      document.head.appendChild(loadSPA);
    }}
  </script>
</body>
</html>"""
    
    return slug, page_html


def main():
    with open(DATA) as f:
        artists = json.load(f)
    
    os.makedirs(ARTISTS_DIR, exist_ok=True)
    
    sitemap_entries = []
    index_entries = []
    
    for artist in artists:
        slug, page = generate_page(artist)
        page_dir = os.path.join(ARTISTS_DIR, slug)
        os.makedirs(page_dir, exist_ok=True)
        
        with open(os.path.join(page_dir, "index.html"), "w") as f:
            f.write(page)
        
        sitemap_entries.append(f"https://edition.sh/artist/{slug}")
        index_entries.append({
            "name": artist["name"],
            "slug": slug,
            "roman_name": artist.get("roman_name", ""),
            "lot_count": artist["lot_count"],
            "avg_price": artist["avg_price"],
        })
        print(f"  ✓ {artist['name']} -> /artist/{slug}/")
    
    # Generate sitemap.xml
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Main pages
    for path in ["", "/prices", "/authenticate", "/kanteishi", "/discover"]:
        sitemap += f'  <url><loc>https://edition.sh{path}</loc><changefreq>weekly</changefreq><priority>{"1.0" if not path else "0.8"}</priority></url>\n'
    
    # Artist pages
    for url in sitemap_entries:
        sitemap += f'  <url><loc>{url}</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>\n'
    
    sitemap += '</urlset>\n'
    
    with open(os.path.join(BASE, "sitemap.xml"), "w") as f:
        f.write(sitemap)
    print(f"\n  ✓ sitemap.xml ({len(sitemap_entries) + 5} URLs)")
    
    # Generate robots.txt  
    robots = """User-agent: *
Allow: /
Sitemap: https://edition.sh/sitemap.xml

User-agent: Googlebot
Allow: /artist/
Allow: /prices
Allow: /kanteishi
"""
    with open(os.path.join(BASE, "robots.txt"), "w") as f:
        f.write(robots)
    print("  ✓ robots.txt")
    
    # Save artist index for SPA use
    with open(os.path.join(BASE, "data", "artist_index.json"), "w") as f:
        json.dump(index_entries, f, ensure_ascii=False, indent=2)
    print(f"  ✓ artist_index.json ({len(index_entries)} artists)")


if __name__ == "__main__":
    print("Generating artist pages for edition.sh...\n")
    main()
    print("\nDone!")
