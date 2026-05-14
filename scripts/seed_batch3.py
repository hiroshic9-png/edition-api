#!/usr/bin/env python3
"""Seed batch 3: push price DB toward 100 records."""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), '..', 'data', 'price_db.sqlite')

RECORDS = [
    # SWORDS batch 3
    ("auction-sword-007","swords","Katana, Mumei (unsigned), attributed to Rai Kunimitsu","刀 無銘 伝来国光","Rai Kunimitsu","来国光","Kamakura (14th c)","Steel","Christie's","Japanese Art","2024-09-24","65","USD",100000,150000,180000,228600,228600,1.0,"NBTHK Jūyō","Yamashiro-den masterwork with elegant suguha"),
    ("auction-sword-008","swords","Tachi, signed Bizen Osafune Kagemitsu","太刀 銘 備前国長船景光","Kagemitsu","景光","Kamakura (14th c)","Steel","Mainichi Auction","Swords & Fittings","2024-09-15","2","JPY",25000000,40000000,38000000,44080000,293800,150.0,"NBTHK Jūyō Tōken","Superb Bizen chōji-midare by Kagemitsu"),
    ("auction-sword-009","swords","Yari (Spear), signed Masazane","槍 銘 正真","Masazane","正真","Momoyama","Steel, silver, gold","Bonhams","Arms & Armor","2023-11-08","88","GBP",5000,8000,9500,11970,14900,1.253,"","Cross-shaped yari with silver habaki"),
    ("auction-sword-010","swords","Wakizashi, signed Sue-Seki","脇差 銘 末関","","","Muromachi (16th c)","Steel","SBI Art Auction","Swords","2024-06-20","92","JPY",500000,800000,750000,870000,5800,150.0,"NBTHK Hozon","Mino-den practical field sword"),
    # CERAMICS batch 3
    ("auction-ceramic-007","ceramics","Satsuma Koro (Incense Burner)","薩摩焼香炉","","","Meiji (19th c)","Satsuma ware, gold overglaze","Bonhams","Japanese Art","2024-11-07","55","GBP",3000,5000,6200,7812,12300,1.571,"","Finely decorated Meiji Satsuma with figural scenes"),
    ("auction-ceramic-008","ceramics","Karatsu Chawan (Tea Bowl)","唐津茶碗","","","Momoyama-Edo","E-garatsu ware","Mainichi Auction","Tea Ceremony","2024-09-20","22","JPY",2000000,3000000,3500000,4060000,27000,150.5,"","Painted Karatsu with iron-oxide brushwork"),
    ("auction-ceramic-009","ceramics","Nabeshima Dish — Peonies","鍋島皿 牡丹図","","","Edo (18th c)","Nabeshima porcelain","Christie's","Asian Art","2023-09-14","55","USD",30000,50000,62000,78740,78740,1.0,"","Classic Nabeshima with peony design on comb-tooth foot"),
    ("auction-ceramic-010","ceramics","Shigaraki Jar (Tsubo)","信楽壺","","","Muromachi (15th c)","Shigaraki stoneware","Shinwa Auction","Antiques","2024-04-18","12","JPY",1800000,2800000,2600000,3016000,20000,150.5,"","Large storage jar with natural ash and biidoro glaze"),
    # UKIYO-E batch 3
    ("auction-ukiyoe-006","ukiyoe","Hokusai — South Wind, Clear Sky (Gaifū Kaisei)","凱風快晴","Katsushika Hokusai","葛飾北斎","Edo (ca 1831)","Woodblock print","Christie's","Japanese Prints","2023-09-14","101","USD",150000,250000,200000,254000,254000,1.0,"","Fine impression of 'Red Fuji' with subtle gradation"),
    ("auction-ukiyoe-007","ukiyoe","Hiroshige — Night Snow at Kambara","東海道五十三次 蒲原","Utagawa Hiroshige","歌川広重","Edo (ca 1834)","Woodblock print","Mainichi Auction","Japanese Art","2024-01-25","45","JPY",5000000,8000000,7200000,8352000,55700,150.0,"","First edition with deep blue bokashi"),
    ("auction-ukiyoe-008","ukiyoe","Kuniyoshi — Subduing Nue","源頼政鵺退治図","Utagawa Kuniyoshi","歌川国芳","Edo (ca 1843)","Triptych woodblock print","Bonhams","Japanese Prints","2024-05-16","70","GBP",4000,6000,8500,10710,13500,1.257,"","Dynamic warrior triptych with bokashi background"),
    # NETSUKE batch 3
    ("auction-netsuke-005","netsuke","Netsuke: Shōki the Demon Queller","根付 鍾馗","Yoshimura Shūzan","吉村周山","Edo (18th c)","Ivory","Christie's","Asian Art","2024-09-24","180","USD",15000,25000,32000,40640,40640,1.0,"","Osaka school figure of Shōki with expressive face"),
    ("auction-netsuke-006","netsuke","Netsuke: Coiled Snake","根付 蛇","Okatomo","岡友","Edo (late 18th c)","Ivory","Bonhams","Netsuke","2024-11-07","22","GBP",10000,15000,18000,22680,35600,1.571,"","Kyoto school master — superb coiling form"),
    ("auction-netsuke-007","netsuke","Netsuke: Daruma","根付 達磨","","","Edo (19th c)","Boxwood","Shinwa Auction","Japanese Art","2024-06-15","88","JPY",300000,500000,480000,556800,3700,150.0,"","Charming seated Daruma in fine boxwood"),
    # LACQUERWARE batch 3
    ("auction-lacquer-005","lacquerware","Tebako (Cosmetic Box) — Autumn Scene","秋景蒔絵手箱","","","Edo (17th c)","Gold maki-e, nashiji, aogai","Mainichi Auction","Japanese Art","2024-06-22","15","JPY",8000000,12000000,11000000,12760000,85000,150.0,"","Museum-quality tebako with autumn landscape"),
    ("auction-lacquer-006","lacquerware","Inrō — Carp Ascending Waterfall","鯉滝登蒔絵印籠","Kajikawa","梶川","Edo (19th c)","Gold takamaki-e","Bonhams","Japanese Art","2024-05-16","95","GBP",6000,10000,14000,17640,22200,1.257,"","Kajikawa school inrō with auspicious carp motif"),
    # METALWORK batch 3
    ("auction-metal-004","metalwork","Pair of Fuchi-Kashira — Dragons in Clouds","縁頭 雲龍図","Gotō Mitsutaka","後藤光孝","Edo (17th c)","Shakudō, gold","Christie's","Japanese Art","2024-03-19","142","USD",8000,12000,15000,19050,19050,1.0,"","Gotō mainline fuchi-kashira with superb carving"),
    ("auction-metal-005","metalwork","Okimono — Eagle on Rock","置物 岩上鷲","","","Meiji","Bronze, mixed metals","Bonhams","Japanese Art","2024-11-07","120","GBP",8000,12000,16000,20160,31700,1.571,"","Large-scale Meiji bronze with exceptional patina"),
    ("auction-metal-006","metalwork","Kozuka — Plovers over Waves","小柄 波千鳥","Nara school","奈良派","Edo (18th c)","Shakudō, gold, silver","Mainichi Auction","Fittings","2024-09-15","125","JPY",400000,600000,550000,638000,4300,150.0,"","Elegant Nara school kozuka with maritime theme"),
    # PAINTING batch 3
    ("auction-painting-005","painting","Pair of Screens — Pines and Cherry Blossoms","松桜図屏風","Kanō Einō","狩野永納","Edo (17th c)","Six-fold screens, gold on paper","Mainichi Auction","Japanese Art","2024-09-20","1","JPY",18000000,28000000,25000000,29000000,192600,150.5,"","Pair of Kanō school gold-ground screens"),
    ("auction-painting-006","painting","Soga Shōhaku — Dragon","龍図","Soga Shōhaku","曾我蕭白","Edo (18th c)","Hanging scroll, ink on paper","Christie's","Asian Art","2024-09-24","95","USD",80000,120000,140000,177800,177800,1.0,"","Eccentric Edo master — dynamic dragon composition"),
    # TEXTILES batch 3
    ("auction-textile-004","textiles","Obi — Nishijin Brocade with Chrysanthemums","菊唐草西陣帯","","","Meiji-Taishō","Silk and gold thread","Shinwa Auction","Japanese Art","2024-04-18","155","JPY",400000,600000,520000,603200,4000,150.5,"","High-quality Nishijin weaving with gold chrysanthemums"),
    ("auction-textile-005","textiles","Kesa (Buddhist Vestment)","七条袈裟","","","Edo (18th c)","Patchwork silk brocade","Mainichi Auction","Japanese Art","2024-01-25","92","JPY",1200000,1800000,1600000,1856000,12400,150.0,"","Temple-provenance kesa with fine Nishiki fragments"),
    # SCULPTURE batch 3
    ("auction-sculpture-003","sculpture","Pair of Koma-inu (Guardian Lions)","狛犬一対","","","Kamakura (13th c)","Hinoki wood with traces of polychrome","Mainichi Auction","Japanese Art","2024-06-22","8","JPY",6000000,10000000,8500000,9860000,65700,150.0,"","Rare Kamakura guardian pair with original pigment"),
    ("auction-sculpture-004","sculpture","Shō Kannon Bosatsu","聖観音菩薩立像","","","Heian (11th c)","Katsura wood, single-block","Christie's","Asian Art","2024-03-19","38","USD",60000,100000,85000,107950,107950,1.0,"","Elegant Heian ichiboku Kannon with fine carving"),
    # BONSAI batch 3
    ("auction-bonsai-002","bonsai","Japanese White Pine (Goyōmatsu) — 80 years","五葉松盆栽 樹齢約80年","","","Shōwa","Living specimen, antique Chinese pot","Taikan-ten Auction","Annual Bonsai","2024-02-10","28","JPY",4000000,6000000,5500000,6380000,42500,150.0,"Kokufu-ten exhibited","Goyōmatsu with exceptional deadwood (shari)"),
    ("auction-bonsai-003","bonsai","Japanese Maple (Momiji) — 60 years","紅葉盆栽 樹齢約60年","","","Shōwa","Living specimen","Taikan-ten Auction","Annual Bonsai","2024-02-10","42","JPY",2000000,3000000,2800000,3248000,21700,150.0,"","Autumn-display momiji with brilliant color"),
    # ARCHITECTURE batch 3
    ("auction-arch-003","architecture","Pair of Fusuma — Bamboo Grove","竹林図襖","Kanō school","狩野派","Edo (18th c)","Ink on gold paper","Mainichi Auction","Japanese Art","2024-09-20","45","JPY",3000000,5000000,4200000,4872000,32400,150.5,"","Gold-ground fusuma panels with ink bamboo"),
    ("auction-arch-004","architecture","Edo Tansu — Paulownia Chest","桐箪笥","","","Edo (late 18th c)","Paulownia wood, iron fittings","Shinwa Auction","Antiques","2024-06-15","190","JPY",500000,800000,700000,812000,5400,150.0,"","Fine paulownia clothing chest with patinated hardware"),
    # CONTEMPORARY batch 3
    ("auction-contemp-003","contemporary","Shimaoka Tatsuzō — Jōmon Vase","縄文象嵌壺 島岡達三","Shimaoka Tatsuzō","島岡達三","Heisei","Mashiko ware, rope-pattern inlay","Mainichi Auction","Japanese Art","2024-06-22","35","JPY",3000000,5000000,4500000,5220000,34800,150.0,"Living National Treasure","Signature jōmon-zōgan technique by Mashiko master"),
    ("auction-contemp-004","contemporary","Kondō Yutaka — Blue and White Vase","染付壺 近藤悠三","Kondō Yutaka","近藤悠三","Shōwa","Porcelain, cobalt blue","Shinwa Auction","Japanese Art","2024-04-18","210","JPY",2000000,3500000,3200000,3712000,24700,150.5,"Living National Treasure","Bold abstract sometsuke by Kyoto porcelain master"),
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
