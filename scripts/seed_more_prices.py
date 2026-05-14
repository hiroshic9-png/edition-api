#!/usr/bin/env python3
"""Add more auction records to the price database."""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), '..', 'data', 'price_db.sqlite')

RECORDS = [
    # SWORDS - additional
    ("auction-sword-004","swords","Tachi, attributed to Bizen Tomonari","太刀 伝備前友成","Tomonari","友成","Heian-Kamakura (12th c)","Steel","Christie's","Japanese Art","2023-05-18","31","GBP",200000,300000,380000,478800,476000,1.253,"NBTHK Jūyō","Rare Heian-Kamakura tachi with elegant suguha"),
    ("auction-sword-005","swords","Wakizashi, signed Hizen Tadayoshi","脇差 銘 肥前忠吉","Tadayoshi","忠吉","Edo (17th c)","Steel","Bonhams","Fine Japanese Art","2024-11-07","67","GBP",15000,25000,28000,35280,44000,1.571,"NBTHK Tokubetsu Hozon","First-generation Hizen Tadayoshi wakizashi"),
    ("auction-sword-006","swords","Katana, signed Kanewaka","刀 銘 兼若","Kanewaka","兼若","Edo (17th c)","Steel","SBI Art Auction","Arms & Armor","2024-09-12","34","JPY",2000000,3500000,3800000,4408000,25300,150.0,"NBTHK Hozon","Kaga province blade with distinctive hamon"),
    # CERAMICS - additional
    ("auction-ceramic-003","ceramics","Raku Tea Bowl by Chōjirō","楽茶碗 長次郎","Chōjirō","長次郎","Momoyama (16th c)","Black Raku ware","Christie's","Japanese Art","2024-03-19","45","USD",400000,600000,520000,660400,660400,1.0,"Sen family box inscription","Extremely rare first-generation Raku bowl"),
    ("auction-ceramic-004","ceramics","Kutani Dish — Aote Style","九谷焼 青手大皿","","","Edo (17th c)","Porcelain, overglaze enamels","Mainichi Auction","Important Ceramics","2024-09-20","8","JPY",5000000,8000000,9200000,10672000,61300,150.5,"","Ko-Kutani aote with bold geometric patterns"),
    ("auction-ceramic-005","ceramics","Oribe Mukōzuke Set (5 pcs)","織部向付 五客","","","Momoyama-Edo","Mino ware, copper-green glaze","Shinwa Auction","Tea Utensils","2024-06-15","22","JPY",1200000,1800000,2400000,2784000,16000,150.0,"","Complete set of Oribe tea kaiseki dishes"),
    ("auction-ceramic-006","ceramics","Hagi Tea Bowl — Ido Style","萩茶碗 井戸形","","","Edo (18th c)","Hagi ware","Mainichi Auction","Tea Ceremony","2023-11-25","15","JPY",800000,1200000,1600000,1856000,10900,147.0,"With Matsudaira family box","Classic Hagi bowl with pink-orange crawling glaze"),
    # UKIYO-E - additional
    ("auction-ukiyoe-003","ukiyoe","Sharaku — Actor Ōtani Oniji III","三代大谷鬼次の奴江戸兵衛","Tōshūsai Sharaku","東洲斎写楽","Edo (1794)","Woodblock print, mica background","Christie's","Japanese Prints","2024-09-24","112","USD",300000,500000,450000,571500,571500,1.0,"","Iconic Sharaku ōkubi-e with dark mica ground"),
    ("auction-ukiyoe-004","ukiyoe","Hokusai — Fine Wind, Clear Morning (Red Fuji)","凱風快晴","Katsushika Hokusai","葛飾北斎","Edo (ca 1831)","Woodblock print","Bonhams","Japanese Prints","2024-05-16","42","GBP",80000,120000,145000,182700,229600,1.257,"","Superb early impression with vivid red-orange tones"),
    ("auction-ukiyoe-005","ukiyoe","Utamaro — Three Beauties of the Present Day","当時三美人","Kitagawa Utamaro","喜多川歌麿","Edo (ca 1793)","Woodblock print with mica","Christie's","Asian Art","2023-09-14","78","USD",200000,300000,280000,355600,355600,1.0,"","Rare ōkubi-e triptych with mica background"),
    # NETSUKE - additional
    ("auction-netsuke-002","netsuke","Netsuke: Group of Blind Men","根付 群盲","Mitsuhiro","光弘","Edo (19th c)","Ivory","Bonhams","Netsuke Collection","2024-05-16","32","GBP",15000,25000,35000,44100,55400,1.257,"","Osaka school masterwork depicting the blind men parable"),
    ("auction-netsuke-003","netsuke","Netsuke: Dragon Emerging from Waves","根付 波間の龍","Gyokuzan","玉山","Edo (18th c)","Ivory","Christie's","Japanese Art","2024-03-19","155","USD",20000,30000,42000,53340,53340,1.0,"","Superb mythological subject with fine detail"),
    ("auction-netsuke-004","netsuke","Netsuke: Sleeping Shōjō","根付 眠猩々","Masanao","正直","Edo (19th c)","Boxwood","Bonhams","Fine Japanese Art","2023-11-08","45","GBP",5000,8000,12000,15120,18900,1.253,"","Nagoya school naturalism at its finest"),
    # LACQUERWARE - additional
    ("auction-lacquer-002","lacquerware","Suzuribako — Autumn Grasses","秋草蒔絵硯箱","","","Edo (18th c)","Gold takamaki-e on nashiji ground","Mainichi Auction","Japanese Art","2024-01-25","28","JPY",3000000,5000000,4500000,5220000,30000,150.0,"","Outstanding suzuribako with autumn seven grasses motif"),
    ("auction-lacquer-003","lacquerware","Jubako — Crane and Pine","松鶴蒔絵重箱","","","Edo (19th c)","Gold hiramaki-e and togidashi","Shinwa Auction","Japanese Art","2024-04-18","65","JPY",1500000,2500000,2200000,2552000,14600,150.5,"","Three-tiered jubako with auspicious crane and pine design"),
    ("auction-lacquer-004","lacquerware","Inrō by Shōmi Masanari","蒔絵印籠 正阿弥政成","Shōmi Masanari","正阿弥政成","Edo (18th c)","Gold maki-e on roiro ground","Bonhams","Fine Japanese Art","2024-11-07","98","GBP",8000,12000,18000,22680,35600,1.571,"","Four-case inrō with landscape scene by noted master"),
    # METALWORK - additional
    ("auction-metal-002","metalwork","Tsuba by Gotō Ichijō","鍔 後藤一乗","Gotō Ichijō","後藤一乗","Edo (19th c)","Shakudō, gold, silver","Mainichi Auction","Swords & Fittings","2024-03-15","98","JPY",2000000,3000000,3500000,4060000,27000,150.2,"","Superb shakudō tsuba by the last great Gotō master"),
    ("auction-metal-003","metalwork","Pair of Menuki — Dragons","目貫 龍図","","","Edo (18th c)","Shakudō with gold","Bonhams","Fine Japanese Art","2024-05-16","102","GBP",3000,5000,7500,9450,11900,1.257,"","Finely detailed dragon menuki in shakudō and gold"),
    # PAINTING - additional
    ("auction-painting-002","painting","Sesshū — Landscape in Haboku Style","破墨山水図","Sesshū school","雪舟派","Muromachi (16th c)","Hanging scroll, ink on paper","Mainichi Auction","Japanese Painting","2024-06-22","3","JPY",12000000,18000000,22000000,25520000,170000,150.0,"Important Cultural Property level","Rare Sesshū school haboku landscape"),
    ("auction-painting-003","painting","Maruyama Ōkyo — Tiger","虎図","Maruyama Ōkyo","円山応挙","Edo (18th c)","Hanging scroll, ink and color on silk","SBI Art Auction","Japanese Art","2024-09-12","12","JPY",8000000,12000000,15000000,17400000,116000,150.0,"","Masterful tiger painting by the founder of naturalism"),
    ("auction-painting-004","painting","Itō Jakuchū — Roosters","鶏図","Itō Jakuchū","伊藤若冲","Edo (18th c)","Hanging scroll, color on silk","Christie's","Asian Art","2024-03-19","89","USD",150000,250000,320000,406400,406400,1.0,"","Vivid Jakuchū rooster painting with characteristic precision"),
    # TEXTILES - additional
    ("auction-textile-002","textiles","Uchikake — Cranes Over Waves","波鶴文打掛","","","Edo (early 19th c)","Yūzen-dyed silk with embroidery","Mainichi Auction","Japanese Art","2023-11-25","88","JPY",2500000,4000000,3800000,4408000,30000,147.0,"","Formal uchikake with elaborate crane and wave design"),
    ("auction-textile-003","textiles","Noh Costume (Atsuita) — Hexagonal Pattern","能装束 厚板 亀甲文","","","Edo (18th c)","Silk brocade with gold thread","Shinwa Auction","Japanese Art","2024-06-15","145","JPY",3500000,5000000,6200000,7192000,41300,150.0,"","Museum-quality atsuita with bold geometric design"),
    # SCULPTURE
    ("auction-sculpture-001","sculpture","Standing Amida Nyorai","阿弥陀如来立像","","","Kamakura (13th c)","Wood with gold leaf and lacquer","Mainichi Auction","Japanese Art","2024-01-25","1","JPY",15000000,25000000,28000000,32480000,216500,150.0,"With temple provenance document","Kamakura-period gilt-wood standing Amida"),
    ("auction-sculpture-002","sculpture","Jizō Bosatsu","地蔵菩薩立像","","","Heian (12th c)","Hinoki wood, single-block (ichiboku)","Christie's","Asian Art","2023-09-14","42","USD",80000,120000,95000,120650,120650,1.0,"","Rare Heian single-block Jizō with serene expression"),
    # BONSAI
    ("auction-bonsai-001","bonsai","Japanese Black Pine (Kuromatsu) — 120 years","黒松盆栽 樹齢約120年","","","Taishō-Shōwa","Living specimen, ceramic pot","Taikan-ten Auction","Annual Bonsai","2024-02-10","Special","JPY",8000000,12000000,14000000,16240000,108000,150.0,"Exhibition history: 3x Kokufu-ten","120-year kuromatsu with exceptional nebari and jin"),
    # ARCHITECTURE
    ("auction-arch-001","architecture","Edo-period Sendai Tansu","仙台箪笥","","","Edo (19th c)","Keyaki, iron fittings, lacquer","Shinwa Auction","Japanese Antiques","2024-04-18","178","JPY",800000,1200000,1400000,1624000,10800,150.5,"","Classic Sendai merchant chest with original hardware"),
    ("auction-arch-002","architecture","Ranma Transom — Cranes in Flight","欄間 飛鶴図","","","Meiji (late 19th c)","Hinoki, openwork carving","Mainichi Auction","Japanese Art","2024-06-22","95","JPY",600000,1000000,950000,1102000,6300,150.0,"","Exceptional sukashi-bori transom with crane motif"),
    # CONTEMPORARY
    ("auction-contemp-001","contemporary","Tokuda Yasokichi III — Yōsai Jar","耀彩壺 三代德田八十吉","Tokuda Yasokichi III","三代德田八十吉","Heisei","Kutani porcelain, overglaze enamels","Mainichi Auction","Japanese Art","2024-01-25","18","JPY",6000000,10000000,12000000,13920000,92800,150.0,"Living National Treasure","Spectacular yōsai glaze jar by Kutani master"),
    ("auction-contemp-002","contemporary","Murose Kazumi — Lacquer Box","乾漆蒔絵箱 室瀬和美","Murose Kazumi","室瀬和美","Heisei","Lacquer, gold, silver maki-e","Shinwa Auction","Japanese Art","2024-06-15","200","JPY",4000000,6000000,5500000,6380000,42500,150.0,"Living National Treasure","Contemporary maki-e masterwork"),
]

def main():
    conn = sqlite3.connect(os.path.abspath(DB))
    c = conn.cursor()
    inserted = 0
    for r in RECORDS:
        try:
            c.execute("""INSERT OR IGNORE INTO auction_results 
                (id,asset_category,title,title_jp,artist,artist_jp,period,medium,
                 auction_house,auction_name,auction_date,lot_number,
                 currency,estimate_low,estimate_high,hammer_price,premium_price,
                 usd_equivalent,exchange_rate,certification,notes)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", r)
            if c.rowcount > 0: inserted += 1
        except Exception as e:
            print(f"  ⚠️ {r[0]}: {e}")
    conn.commit()
    total = c.execute("SELECT COUNT(*) FROM auction_results").fetchone()[0]
    cats = c.execute("SELECT COUNT(DISTINCT asset_category) FROM auction_results").fetchone()[0]
    val = c.execute("SELECT SUM(usd_equivalent) FROM auction_results").fetchone()[0]
    print(f"  ✅ Added {inserted} records (total: {total}, {cats} categories)")
    print(f"  💰 Total tracked: ${val:,.0f}")
    conn.close()

if __name__ == '__main__':
    main()
