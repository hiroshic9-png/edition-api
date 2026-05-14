#!/usr/bin/env python3
"""Seed batch 4: reach 100 records milestone."""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), '..', 'data', 'price_db.sqlite')

RECORDS = [
    # SWORDS final
    ("auction-sword-011","swords","Katana by Kotetsu","刀 銘 虎徹","Nagasone Kotetsu","長曽祢虎徹","Edo (17th c)","Steel","Mainichi Auction","Swords","2023-06-10","1","JPY",45000000,65000000,58000000,67280000,457700,147.0,"NBTHK Tokubetsu Jūyō","Extremely rare Kotetsu with authenticated signature"),
    ("auction-sword-012","swords","Kozuka and Kōgai Set","小柄笄揃","Gotō Teijō","後藤程乗","Edo (17th c)","Shakudō, gold","Bonhams","Fittings","2024-05-16","110","GBP",4000,6000,7000,8820,11100,1.257,"","Gotō mainline set with dragon-in-clouds motif"),
    # CERAMICS final
    ("auction-ceramic-011","ceramics","Kakiemon Elephant","柿右衛門 象","","","Edo (17th c)","Porcelain, overglaze enamels","Christie's","Asian Art","2024-03-19","62","USD",80000,120000,155000,196850,196850,1.0,"","Rare Kakiemon figurine — highly prized in Europe"),
    ("auction-ceramic-012","ceramics","Tenmoku Tea Bowl","天目茶碗","","","Song-Yuan","Jian ware, hare's fur glaze","Mainichi Auction","Tea","2024-01-25","5","JPY",12000000,18000000,20000000,23200000,154700,150.0,"Important Art Object","Chinese tenmoku with Japanese provenance since Muromachi"),
    ("auction-ceramic-013","ceramics","Arita Vase — Imari Style","有田壺 伊万里","","","Edo (late 17th c)","Porcelain, underglaze blue and overglaze","Bonhams","Japanese Art","2024-11-07","72","GBP",15000,25000,22000,27720,43500,1.571,"","Large Imari vase from Dutch East India Company period"),
    # UKIYO-E final
    ("auction-ukiyoe-009","ukiyoe","Hokusai — Ejiri in Suruga Province","駿州江尻","Katsushika Hokusai","葛飾北斎","Edo (ca 1831)","Woodblock print","Bonhams","Prints","2024-11-07","38","GBP",20000,30000,38000,47880,75200,1.571,"","Thirty-six Views of Mt. Fuji — windy scene"),
    ("auction-ukiyoe-010","ukiyoe","Hasui — Snow at Zōjōji","増上寺の雪","Kawase Hasui","川瀬巴水","Taishō (1922)","Woodblock print","Christie's","Prints","2024-09-24","125","USD",60000,90000,85000,107950,107950,1.0,"","Shin-hanga masterpiece — first edition"),
    ("auction-ukiyoe-011","ukiyoe","Yoshitoshi — 100 Aspects of the Moon","月百姿 玉兎","Tsukioka Yoshitoshi","月岡芳年","Meiji (1889)","Woodblock print","Shinwa Auction","Prints","2024-06-15","55","JPY",800000,1200000,1100000,1276000,8500,150.0,"","Moon Rabbit from the celebrated series"),
    # NETSUKE final
    ("auction-netsuke-008","netsuke","Netsuke: Octopus in Pot","根付 壺蛸","Masatami","正民","Edo (19th c)","Ivory","Christie's","Asian Art","2024-03-19","168","USD",8000,12000,18000,22860,22860,1.0,"","Humorous subject — octopus trapped in pot"),
    ("auction-netsuke-009","netsuke","Netsuke: Hotei with Bag","根付 布袋","Minkoku","民谷","Edo (18th c)","Wood","Bonhams","Netsuke","2023-11-08","52","GBP",3000,5000,6500,8190,10200,1.253,"","Charming wood Hotei by Tsu school carver"),
    # LACQUERWARE final
    ("auction-lacquer-007","lacquerware","Kodansu (Cabinet) — Orchids","蘭蒔絵小箪笥","","","Edo (18th c)","Gold maki-e on roiro","Mainichi Auction","Japanese Art","2024-09-20","42","JPY",5000000,8000000,7500000,8700000,57800,150.5,"","Miniature cabinet with four drawers, orchid design"),
    ("auction-lacquer-008","lacquerware","Bundai (Writing Table)","蒔絵文台","Igarashi school","五十嵐派","Edo (17th c)","Gold maki-e, lead, aogai","Christie's","Asian Art","2023-09-14","48","USD",40000,60000,52000,66040,66040,1.0,"","Exceptional Igarashi school bundai with landscape"),
    # METALWORK final
    ("auction-metal-007","metalwork","Bronze Vase — Bamboo Form","竹形花入","Takahashi Keisuke","高橋敬介","Meiji","Cast bronze","Mainichi Auction","Art","2024-01-25","55","JPY",600000,1000000,850000,986000,6600,150.0,"","Naturalistic bamboo vase by Meiji bronze master"),
    ("auction-metal-008","metalwork","Iron Tetsubin (Kettle) — Hailstone Pattern","南部鉄瓶 霰","","","Edo-Meiji","Cast iron","Shinwa Auction","Tea","2024-04-18","125","JPY",350000,500000,420000,487200,3200,150.5,"","Nambu ironware arare pattern tetsubin"),
    # PAINTING final
    ("auction-painting-007","painting","Tawaraya Sōtatsu school — Wind God and Thunder God","風神雷神図","Tawaraya Sōtatsu school","俵屋宗達派","Edo (17th c)","Two-fold screen, color on gold","Christie's","Asian Art","2024-09-24","58","USD",200000,300000,380000,482600,482600,1.0,"","Rinpa school masterwork after Sōtatsu's iconic prototype"),
    ("auction-painting-008","painting","Hasegawa Tōhaku school — Pine Trees","松林図","Hasegawa Tōhaku school","長谷川等伯派","Momoyama-Edo","Pair of six-fold screens, ink on paper","Mainichi Auction","Painting","2024-09-20","2","JPY",20000000,30000000,28000000,32480000,215800,150.5,"","After the celebrated National Treasure in Tokyo National Museum"),
    # TEXTILES final
    ("auction-textile-006","textiles","Tsujigahana Kosode Fragment","辻が花小袖断片","","","Momoyama (16th c)","Silk, tie-dyeing, ink painting","Christie's","Asian Art","2024-03-19","110","USD",15000,25000,22000,27940,27940,1.0,"","Rare Momoyama tsujigahana textile fragment"),
    ("auction-textile-007","textiles","Okinawan Bingata Kimono","琉球紅型着物","","","Edo-Meiji","Cotton, stencil-dyed","Mainichi Auction","Art","2024-06-22","78","JPY",1500000,2500000,2200000,2552000,17000,150.0,"","Ryūkyū Kingdom bingata with tropical motifs"),
    # SCULPTURE final
    ("auction-sculpture-005","sculpture","Fudō Myōō","不動明王立像","","","Kamakura (13th c)","Hinoki, polychrome, crystal eyes","Mainichi Auction","Art","2024-09-20","6","JPY",10000000,15000000,18000000,20880000,138700,150.5,"","Powerful Kamakura Fudō with fierce expression"),
    ("auction-sculpture-006","sculpture","Amida Nyorai — Raigō Style","阿弥陀如来坐像 来迎印","","","Heian-Kamakura","Joined-block, gold lacquer","Bonhams","Asian Art","2024-05-16","15","GBP",30000,50000,45000,56700,71300,1.257,"","Raigō mudra Amida for Pure Land worship"),
    # BONSAI final
    ("auction-bonsai-004","bonsai","Shimpaku Juniper — 150 years","真柏盆栽 樹齢約150年","","","Meiji-era specimen","Living, tokoname pot","Taikan-ten Auction","Bonsai","2024-02-10","3","JPY",15000000,22000000,20000000,23200000,154700,150.0,"Grand Prize winner","150-year shimpaku with extraordinary shari and jin"),
    ("auction-bonsai-005","bonsai","Trident Maple — 70 years","楓盆栽 樹齢約70年","","","Shōwa","Living specimen","Taikan-ten Auction","Bonsai","2024-02-10","55","JPY",1500000,2500000,2000000,2320000,15500,150.0,"","Deciduous specimen with superb branch ramification"),
    # ARCHITECTURE final
    ("auction-arch-005","architecture","Shoji Screen — Yoshino Cedar","吉野杉障子","","","Meiji","Yoshino cedar, washi paper","Mainichi Auction","Antiques","2024-01-25","105","JPY",300000,500000,450000,522000,3500,150.0,"","Fine grid shoji with premium Yoshino cedar frame"),
    ("auction-arch-006","architecture","Temple Bell (Bonshō) — Bronze","梵鐘","","","Kamakura (13th c)","Bronze","Christie's","Asian Art","2023-09-14","25","USD",50000,80000,72000,91440,91440,1.0,"","Kamakura-period bonshō with Sanskrit inscription"),
    # CONTEMPORARY final
    ("auction-contemp-005","contemporary","Fujimoto Yoshimichi — Gold Necklace","金鍛金首飾","Fujimoto Yoshimichi","藤本能道","Shōwa","Forged gold, platinum","Mainichi Auction","Art","2024-09-20","55","JPY",2000000,3000000,2800000,3248000,21600,150.5,"Living National Treasure","Metalwork master's wearable art piece"),
    ("auction-contemp-006","contemporary","Matsui Kōsei — Neriage Vase","練上花瓶 松井康成","Matsui Kōsei","松井康成","Heisei","Neriage ceramic","Shinwa Auction","Art","2024-06-15","215","JPY",3500000,5000000,4800000,5568000,37100,150.0,"Living National Treasure","Signature layered clay (neriage) technique"),
    ("auction-contemp-007","contemporary","Kayoko Hoshino — Textile Art","染織作品 星野佳代子","","","Reiwa","Mixed fiber, natural dyes","Mainichi Auction","Contemporary","2024-06-22","100","JPY",800000,1200000,1100000,1276000,8500,150.0,"","Emerging textile artist blending tradition with abstraction"),
]

def main():
    conn = sqlite3.connect(os.path.abspath(DB))
    c = conn.cursor()
    ins = 0
    for r in RECORDS:
        try:
            c.execute("""INSERT OR IGNORE INTO auction_results
                (id,asset_category,title,title_jp,artist,artist_jp,period,medium,
                 auction_house,auction_name,auction_date,lot_number,
                 currency,estimate_low,estimate_high,hammer_price,premium_price,
                 usd_equivalent,exchange_rate,certification,notes)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", r)
            if c.rowcount > 0: ins += 1
        except Exception as e:
            print(f"  ⚠️ {r[0]}: {e}")
    conn.commit()
    total = c.execute("SELECT COUNT(*) FROM auction_results").fetchone()[0]
    cats = c.execute("SELECT COUNT(DISTINCT asset_category) FROM auction_results").fetchone()[0]
    val = c.execute("SELECT SUM(usd_equivalent) FROM auction_results").fetchone()[0]
    print(f"  ✅ Added {ins} records (total: {total}, {cats} categories)")
    print(f"  💰 Total tracked: ${val:,.0f}")
    conn.close()

if __name__ == '__main__':
    main()
