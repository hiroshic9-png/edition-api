#!/usr/bin/env python3
"""
Generate SEO-optimized artist pages for edition.sh
Each page is a static HTML file at /artist/{slug}/index.html
"""
import json
import os
import re
import urllib.parse

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(SITE_DIR, 'data', 'artist_seo_data.json')
ARTIST_DIR = os.path.join(SITE_DIR, 'artist')

# Also load top_artists.json for additional metadata (birth_year, etc.)
TOP_ARTISTS_FILE = os.path.join(SITE_DIR, 'data', 'top_artists.json')


def format_price(price):
    """Format price in Japanese yen with commas"""
    if price >= 100_000_000:
        return f"¥{price/100_000_000:.1f}億"
    elif price >= 10_000_000:
        return f"¥{price/10_000:,.0f}万"
    elif price >= 1_000_000:
        return f"¥{price:,.0f}"
    else:
        return f"¥{price:,.0f}"


def format_price_full(price):
    """Format full price with commas"""
    return f"¥{price:,.0f}"


def make_slug(name):
    """Create URL-safe slug from artist name"""
    # Replace full-width spaces with hyphens
    slug = name.replace('　', '-').replace(' ', '-')
    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def house_name_ja(house):
    """Convert house code to Japanese name"""
    mapping = {
        'SBI': 'SBI Art Auction',
        'Mainichi': '毎日オークション',
        'Shinwa': 'シンワオークション',
    }
    return mapping.get(house, house)


def generate_market_text(artist):
    """Generate unique market overview text for each artist"""
    name = artist['name']
    houses_ja = '、'.join([house_name_ja(h) for h in artist['houses']])
    n_houses = artist['n_houses']
    count = artist['price_count']
    avg = format_price_full(artist['avg_price'])
    median = format_price_full(artist['median_price'])
    max_p = format_price_full(artist['max_price'])
    total = format_price_full(artist['total_value'])

    # Price tier classification
    avg_price = artist['avg_price']
    if avg_price >= 10_000_000:
        tier = "プレミアム・マーケット"
        tier_desc = "ハイエンド市場で安定的に高額取引される作家"
    elif avg_price >= 1_000_000:
        tier = "ミドル・マーケット"
        tier_desc = "中堅〜上位の価格帯で活発に取引される作家"
    elif avg_price >= 300_000:
        tier = "エマージング・マーケット"
        tier_desc = "成長中の市場で注目を集める作家"
    else:
        tier = "エントリー・マーケット"
        tier_desc = "比較的手に取りやすい価格帯でコレクション入門に適した作家"

    # Spread analysis
    spread = artist['max_price'] / max(artist['min_price'], 1)
    if spread > 100:
        spread_text = f"最高額と最低額の間に{spread:.0f}倍以上の開きがあり、作品の種類や状態によって価格が大きく変動します。"
    elif spread > 10:
        spread_text = f"作品間の価格差は{spread:.0f}倍程度あり、技法やサイズによる価格変動が見られます。"
    else:
        spread_text = "作品間の価格は比較的安定しており、予測可能性の高い市場です。"

    # Multi-house text
    if n_houses >= 3:
        cross_text = f"3つの主要オークションハウス全てで取り扱われており、市場での高い流動性と需要を示しています。"
    elif n_houses == 2:
        cross_text = f"複数のオークションハウスで取り扱われており、一定の市場流動性があります。"
    else:
        cross_text = f"現在{houses_ja}で取り扱われています。"

    text = f"""<p style="line-height: 1.8; color: var(--text-secondary, #555);">
      {name}の作品は、国内{n_houses}つのオークションハウス（{houses_ja}）において合計{count}件の落札実績が確認されています。
      平均落札価格は{avg}、中央値は{median}で、{tier}に位置づけられます。
      過去の最高落札価格は{max_p}、総取引額は{total}に達します。
    </p>
    <p style="line-height: 1.8; color: var(--text-secondary, #555); margin-top: 1rem;">
      {spread_text}{cross_text}
    </p>
    <p style="line-height: 1.8; color: var(--text-secondary, #555); margin-top: 1rem;">
      本データはEDITIONのKANTEISHI（鑑定士）インテリジェンスエンジンにより、
      SBI Art Auction・毎日オークション・シンワオークションの落札記録を横断的に分析したものです。
      ヘドニック価格モデル v0.8（R²=0.898）による公正市場価格の推定にも活用されています。
    </p>"""
    return text, tier


def generate_page(artist, extra_meta=None):
    """Generate full HTML page for an artist"""
    name = artist['name']
    roman = artist.get('roman_name', '')
    slug = make_slug(name)
    encoded_slug = urllib.parse.quote(slug, safe='')

    houses_text = '、'.join([house_name_ja(h) for h in artist['houses']])
    count = artist['price_count']
    avg = format_price_full(artist['avg_price'])
    median = format_price_full(artist['median_price'])
    max_p = format_price_full(artist['max_price'])
    total = format_price_full(artist['total_value'])

    desc = f"{name}のオークション落札価格データ。{count}件の取引実績、平均落札価格{avg}、最高額{max_p}。{artist['n_houses']}つのオークションハウスの横断分析。"

    # Build extra metadata sections
    extra = extra_meta or {}
    birth_year = extra.get('birth_year')
    death_year = extra.get('death_year')
    is_deceased = extra.get('is_deceased', False)
    movements = extra.get('movements', [])
    fields = extra.get('fields', [])
    birth_place = extra.get('birth_place', '')
    daj_url = extra.get('daj_url', '')
    authorities = extra.get('authorities', {})
    extra_roman = extra.get('roman_name', '') or roman

    if extra_roman and not roman:
        roman = extra_roman

    # Lifespan text
    lifespan = ''
    if birth_year:
        if death_year:
            lifespan = f'{birth_year}–{death_year}'
        elif is_deceased:
            lifespan = f'{birth_year}–'
        else:
            lifespan = f'{birth_year}–'

    # Profile section
    profile_lines = []
    if birth_place:
        profile_lines.append(('出身地', birth_place))
    if movements:
        movement_names = {
            'nihonga': '日本画', 'yoga': '洋画', 'contemporary': '現代美術',
            'pop_art': 'ポップアート', 'sculpture': '彫刻', 'ceramics': '陶芸',
            'calligraphy': '書道', 'print': '版画', 'photography': '写真',
            'ink_wash': '水墨画', 'crafts': '工芸', 'mixed_media': 'ミクストメディア',
        }
        mv_text = '、'.join([movement_names.get(m, m) for m in movements])
        profile_lines.append(('ジャンル', mv_text))
    if fields:
        profile_lines.append(('活動分野', '、'.join(fields[:4])))

    # Generate market text
    market_text, tier = generate_market_text(artist)

    # Build profile HTML
    profile_html = ''
    if profile_lines:
        profile_html = '<h2 class="section-title">プロフィール</h2>\n'
        for key, val in profile_lines:
            profile_html += f'    <div class="meta-line"><span class="meta-key">{key}</span><span class="meta-val">{val}</span></div>\n'

    # Authority links
    auth_html = ''
    if authorities or daj_url:
        links = []
        if daj_url:
            links.append(f'<a href="{daj_url}" target="_blank" rel="noopener">文化庁 ArtPlatform</a>')
        if authorities.get('wikidata'):
            links.append(f'<a href="https://www.wikidata.org/wiki/{authorities["wikidata"]}" target="_blank" rel="noopener">Wikidata</a>')
        if authorities.get('viaf'):
            links.append(f'<a href="https://viaf.org/viaf/{authorities["viaf"]}" target="_blank" rel="noopener">VIAF</a>')
        if authorities.get('ulan'):
            links.append(f'<a href="https://www.getty.edu/vow/ULANFullDisplay?find=&role=&nation=&subjectid={authorities["ulan"]}" target="_blank" rel="noopener">Getty ULAN</a>')
        if links:
            auth_html = f'<div class="auth-links"><span class="meta-key">外部リンク:</span> {" · ".join(links)}</div>'

    # JSON-LD
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": name,
        "url": f"https://edition.sh/artist/{encoded_slug}"
    }
    if roman:
        jsonld["alternateName"] = roman
    if birth_year:
        jsonld["birthDate"] = str(birth_year)
    if death_year:
        jsonld["deathDate"] = str(death_year)
    if birth_place:
        jsonld["birthPlace"] = {"@type": "Place", "name": birth_place}

    roman_html = f'<p class="roman">{roman}</p>' if roman else ''
    lifespan_html = f'<p class="lifespan">{lifespan}</p>' if lifespan else ''

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} — オークション相場・落札価格分析 | EDITION</title>
  <meta name="description" content="{desc}">
  <meta name="robots" content="index, follow">
  
  <!-- Open Graph -->
  <meta property="og:type" content="profile">
  <meta property="og:title" content="{name} — オークション相場 | EDITION">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="https://edition.sh/artist/{encoded_slug}">
  <meta property="og:site_name" content="EDITION">
  <meta property="og:locale" content="ja_JP">
  <meta property="og:locale:alternate" content="en_US">
  
  <!-- Twitter -->
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{name} — オークション相場 | EDITION">
  <meta name="twitter:description" content="{desc}">
  
  <link rel="canonical" href="https://edition.sh/artist/{encoded_slug}">
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500&family=Inter:wght@300;400;500&family=Noto+Serif+JP:wght@300;400;500&family=Noto+Sans+JP:wght@300;400;500&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="/style.css?v=08b">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>◆</text></svg>">
  
  <!-- Structured Data -->
  <script type="application/ld+json">
  {json.dumps(jsonld, ensure_ascii=False, indent=2)}
  </script>
  
  <style>
    .artist-page {{
      max-width: 900px; margin: 0 auto; padding: 6rem 2rem 4rem;
      font-family: var(--font-sans, 'Inter', 'Noto Sans JP', sans-serif);
      color: var(--text, #e0e0e0);
      min-height: 100vh;
    }}
    body {{
      background: #0C0C0C;
      margin: 0;
    }}
    .artist-page h1 {{
      font-family: var(--font-serif, 'Cormorant Garamond', 'Noto Serif JP', serif);
      font-weight: 300; font-size: clamp(2rem, 5vw, 3rem);
      margin-bottom: 0.25rem; line-height: 1.2;
      color: #fff;
    }}
    .artist-page .roman {{
      color: rgba(255,255,255,0.4); font-size: 1.1rem; margin-bottom: 0.5rem;
      font-family: var(--font-serif, 'Cormorant Garamond', serif);
      letter-spacing: 0.05em;
    }}
    .artist-page .lifespan {{
      color: rgba(255,255,255,0.35); font-size: 0.85rem; margin-bottom: 2rem;
    }}
    .artist-page .tier-badge {{
      display: inline-block; padding: 0.3rem 0.8rem;
      border: 1px solid rgba(184,134,11,0.4); border-radius: 20px;
      font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase;
      color: #b8860b; margin-bottom: 2rem;
    }}
    .artist-page .stats-grid {{
      display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 1rem; margin: 2rem 0;
    }}
    .artist-page .stat {{
      background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
      border-radius: 12px; padding: 1.5rem; text-align: center;
      transition: border-color 0.3s ease;
    }}
    .artist-page .stat:hover {{
      border-color: rgba(184,134,11,0.4);
    }}
    .artist-page .stat-value {{
      font-family: var(--font-serif); font-size: 1.3rem;
      color: #b8860b; display: block; margin-bottom: 0.3rem;
    }}
    .artist-page .stat-label {{
      font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;
      color: rgba(255,255,255,0.4);
    }}
    .artist-page .section-title {{
      font-family: var(--font-serif); font-weight: 400; font-size: 1.3rem;
      margin: 3rem 0 1rem; padding-bottom: 0.5rem;
      border-bottom: 1px solid rgba(255,255,255,0.1);
      color: #fff;
    }}
    .artist-page .meta-line {{
      display: flex; gap: 0.5rem; align-items: baseline;
      padding: 0.6rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);
      font-size: 0.9rem;
    }}
    .artist-page .meta-key {{
      color: rgba(255,255,255,0.4); min-width: 120px; flex-shrink: 0;
    }}
    .artist-page .meta-val {{ color: rgba(255,255,255,0.8); font-weight: 400; }}
    .artist-page .auth-links {{ margin-top: 1.5rem; font-size: 0.8rem; }}
    .artist-page .auth-links a {{
      color: #b8860b; text-decoration: none; transition: opacity 0.2s;
    }}
    .artist-page .auth-links a:hover {{ opacity: 0.7; }}
    .artist-page .back-link {{
      display: inline-flex; align-items: center; gap: 0.5rem;
      margin-bottom: 2rem; font-size: 0.85rem;
      color: rgba(255,255,255,0.4); text-decoration: none;
      transition: color 0.2s;
    }}
    .artist-page .back-link:hover {{ color: #b8860b; }}
    .artist-page .cta {{
      margin-top: 3rem; padding: 2rem;
      background: rgba(255,255,255,0.02);
      border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;
      text-align: center;
    }}
    .artist-page .cta a {{
      color: #b8860b; text-decoration: none; font-weight: 500;
      transition: opacity 0.2s;
    }}
    .artist-page .cta a:hover {{ opacity: 0.7; }}
    .artist-page .house-bars {{
      margin: 1.5rem 0; display: flex; flex-direction: column; gap: 0.5rem;
    }}
    .artist-page .house-bar {{
      display: flex; align-items: center; gap: 1rem;
    }}
    .artist-page .house-bar .bar-label {{
      min-width: 160px; font-size: 0.8rem; color: rgba(255,255,255,0.5);
    }}
    .artist-page .house-bar .bar-track {{
      flex: 1; height: 4px; background: rgba(255,255,255,0.05);
      border-radius: 2px; overflow: hidden;
    }}
    .artist-page .house-bar .bar-fill {{
      height: 100%; background: #b8860b; border-radius: 2px;
      transition: width 0.8s ease;
    }}
    .artist-page footer {{
      margin-top: 4rem; padding-top: 2rem;
      border-top: 1px solid rgba(255,255,255,0.08);
      font-size: 0.75rem; color: rgba(255,255,255,0.3);
      text-align: center;
    }}
    .artist-page footer a {{
      color: rgba(255,255,255,0.3); text-decoration: none;
    }}
    .artist-page footer a:hover {{ color: #b8860b; }}
    .artist-page p {{
      color: rgba(255,255,255,0.5) !important;
    }}
    @media (max-width: 600px) {{
      .artist-page {{ padding: 4rem 1.2rem 3rem; }}
      .artist-page .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .artist-page .meta-line {{ flex-direction: column; gap: 0.2rem; }}
      .artist-page .meta-key {{ min-width: auto; }}
    }}
  </style>
</head>
<body>
  <div class="artist-page">
    <a href="/" class="back-link">← EDITION</a>
    
    <h1>{name}</h1>
    {roman_html}
    {lifespan_html}
    <span class="tier-badge">{tier}</span>
    
    <div class="stats-grid">
      <div class="stat">
        <span class="stat-value">{count}</span>
        <span class="stat-label">落札実績</span>
      </div>
      <div class="stat">
        <span class="stat-value">{format_price(artist['avg_price'])}</span>
        <span class="stat-label">平均落札価格</span>
      </div>
      <div class="stat">
        <span class="stat-value">{format_price(artist['median_price'])}</span>
        <span class="stat-label">中央値</span>
      </div>
      <div class="stat">
        <span class="stat-value">{format_price(artist['max_price'])}</span>
        <span class="stat-label">最高額</span>
      </div>
      <div class="stat">
        <span class="stat-value">{artist['n_houses']}</span>
        <span class="stat-label">取扱ハウス</span>
      </div>
      <div class="stat">
        <span class="stat-value">{format_price(artist['total_value'])}</span>
        <span class="stat-label">総取引額</span>
      </div>
    </div>
    
    {profile_html}
    {auth_html}
    
    <h2 class="section-title">市場分析</h2>
    {market_text}
    
    <h2 class="section-title">取扱オークションハウス</h2>
    <div class="house-bars">
      {"".join([f'''<div class="house-bar">
        <span class="bar-label">{house_name_ja(h)}</span>
        <div class="bar-track"><div class="bar-fill" style="width: {100 / artist["n_houses"]}%"></div></div>
      </div>''' for h in artist['houses']])}
    </div>
    
    <div class="cta">
      <p style="margin-bottom: 0.5rem; font-size: 0.9rem; color: rgba(255,255,255,0.4) !important;">KANTEISHI Intelligence Engine</p>
      <p style="font-family: var(--font-serif); font-size: 1.1rem;">
        <a href="/">全{count}件の市場データを分析する →</a>
      </p>
      <p style="font-size: 0.8rem; margin-top: 0.5rem;">
        49,968件 · 7,258名のアーティスト · 3社横断分析
      </p>
    </div>
    
    <footer>
      <p>© 2026 EDITION — Japanese Cultural Assets Intelligence</p>
      <p style="margin-top: 0.3rem;">
        <a href="/">トップ</a> · 
        <a href="/#artists">アーティスト一覧</a> · 
        <a href="/#kanteishi">KANTEISHI</a>
      </p>
    </footer>
  </div>
</body>
</html>"""
    return html


def main():
    with open(DATA_FILE) as f:
        artists = json.load(f)

    # Load extra metadata from top_artists.json
    extra_meta = {}
    try:
        with open(TOP_ARTISTS_FILE) as f:
            for a in json.load(f):
                extra_meta[a['name']] = a
    except:
        pass

    # Generate pages
    generated = 0
    index_entries = []

    for artist in artists:
        slug = make_slug(artist['name'])
        page_dir = os.path.join(ARTIST_DIR, slug)
        os.makedirs(page_dir, exist_ok=True)

        extra = extra_meta.get(artist['name'], {})
        html = generate_page(artist, extra)

        page_file = os.path.join(page_dir, 'index.html')
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(html)

        index_entries.append({
            'name': artist['name'],
            'slug': slug,
            'roman_name': artist.get('roman_name', '') or extra.get('roman_name', ''),
            'lot_count': artist['price_count'],
            'avg_price': artist['avg_price'],
        })
        generated += 1

    # Update artist_index.json
    index_file = os.path.join(SITE_DIR, 'data', 'artist_index.json')
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_entries, f, ensure_ascii=False, indent=2)

    print(f"Generated {generated} artist pages")
    print(f"Updated artist_index.json with {len(index_entries)} entries")

    # Generate sitemap entries
    sitemap_entries = []
    for entry in index_entries:
        encoded_slug = urllib.parse.quote(entry['slug'], safe='')
        sitemap_entries.append(f"https://edition.sh/artist/{encoded_slug}")

    sitemap_file = os.path.join(SITE_DIR, 'data', 'artist_sitemap_urls.txt')
    with open(sitemap_file, 'w') as f:
        f.write('\n'.join(sitemap_entries))
    print(f"Wrote {len(sitemap_entries)} sitemap URLs")


if __name__ == '__main__':
    main()
