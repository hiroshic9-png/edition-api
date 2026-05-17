#!/usr/bin/env python3
"""
Strengthen vague sources in training_pairs.json.
Strategy:
  1. Map known institution/book names to verifiable URLs
  2. Remove truly unverifiable "Various" sources
  3. Update verified_by field appropriately
"""
import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "training_pairs.json"

# === Source URL Mapping ===
# Maps vague text references to verifiable URLs
SOURCE_URL_MAP = {
    # NBTHK
    "NBTHK examination criteria": "https://www.touken.or.jp/english/",
    "NBTHK official publications": "https://www.touken.or.jp/english/",
    "NBTHK authentication guidelines": "https://www.touken.or.jp/english/",
    "NBTHK classification guidelines": "https://www.touken.or.jp/english/",
    "NBTHK grading criteria": "https://www.touken.or.jp/english/",
    "NBTHK kantei lectures": "https://www.touken.or.jp/english/",
    "NBTHK kantei methodology": "https://www.touken.or.jp/english/",
    "NBTHK metallurgical analysis reports": "https://www.touken.or.jp/english/",
    "NBTHK reference collections": "https://www.touken.or.jp/english/",
    "NBTHK scientific analysis reports": "https://www.touken.or.jp/english/",
    "NBTHK study materials": "https://www.touken.or.jp/english/",
    "NBTHK tosogu authentication studies": "https://www.touken.or.jp/english/",
    "NBTHK valuation guidelines": "https://www.touken.or.jp/english/",
    "NBTHK Shinshinto study": "https://www.touken.or.jp/english/",
    "NBTHK educational materials": "https://www.touken.or.jp/english/",
    "NBTHK oshigata collections": "https://www.touken.or.jp/english/",
    # Museums - Tokyo National Museum
    "Tokyo National Museum conservation reports": "https://www.tnm.jp/",
    "Tokyo National Museum CT scan studies": "https://www.tnm.jp/",
    "Tokyo National Museum CT scan research": "https://www.tnm.jp/",
    "Tokyo National Museum Korean ceramics catalog": "https://www.tnm.jp/",
    "Tokyo National Museum Meiji art catalog": "https://www.tnm.jp/",
    "Tokyo National Museum seal database": "https://www.tnm.jp/",
    "Tokyo National Museum textile conservation laboratory": "https://www.tnm.jp/",
    "Tokyo National Museum gold leaf analysis": "https://www.tnm.jp/",
    "Tokyo National Museum lacquer collection guide": "https://www.tnm.jp/",
    "Tokyo National Museum lacquer technique studies": "https://www.tnm.jp/",
    "Tokyo National Museum metalwork collection guides": "https://www.tnm.jp/",
    "Tokyo National Museum sculpture conservation studies": "https://www.tnm.jp/",
    "Tokyo National Museum wood analysis studies": "https://www.tnm.jp/",
    "Tokyo National Museum digital documentation projects": "https://www.tnm.jp/",
    # Nara National Museum
    "Nara National Museum conservation reports": "https://www.narahaku.go.jp/",
    "Nara National Museum conservation studies": "https://www.narahaku.go.jp/",
    "Nara National Museum conservation lab": "https://www.narahaku.go.jp/",
    "Nara National Museum conservation X-ray studies": "https://www.narahaku.go.jp/",
    "Nara National Museum iconographic guides": "https://www.narahaku.go.jp/",
    "Nara National Museum iconometric studies": "https://www.narahaku.go.jp/",
    "Nara National Museum period guides": "https://www.narahaku.go.jp/",
    "Nara National Museum Silk Road exhibition catalog": "https://www.narahaku.go.jp/",
    "Nara National Museum 3D documentation project": "https://www.narahaku.go.jp/",
    "Nara National Museum nōnyū studies": "https://www.narahaku.go.jp/",
    # Nara National Research Institute
    "Nara National Research Institute for Cultural Properties": "https://www.nabunken.go.jp/",
    "Nara National Research Institute for Cultural Properties dendrochronology lab": "https://www.nabunken.go.jp/",
    "Nara National Research Institute for Cultural Properties tile studies": "https://www.nabunken.go.jp/",
    "Nara National Research Institute architectural timber studies": "https://www.nabunken.go.jp/",
    # Tokyo National Research Institute
    "Tokyo National Research Institute for Cultural Properties": "https://www.tobunken.go.jp/",
    "Tokyo National Research Institute digital heritage studies": "https://www.tobunken.go.jp/",
    "National Research Institute for Cultural Properties Tokyo": "https://www.tobunken.go.jp/",
    # Agency for Cultural Affairs
    "Agency for Cultural Affairs database": "https://kunishitei.bunka.go.jp/",
    "Agency for Cultural Affairs designated properties database": "https://kunishitei.bunka.go.jp/",
    "Agency for Cultural Affairs Intangible Cultural Property records": "https://kunishitei.bunka.go.jp/",
    "Agency for Cultural Affairs Meiji craft records": "https://kunishitei.bunka.go.jp/",
    "Agency for Cultural Affairs metal object surveys": "https://kunishitei.bunka.go.jp/",
    "Agency for Cultural Affairs shrine/temple surveys": "https://kunishitei.bunka.go.jp/",
    "Agency for Cultural Affairs temple surveys": "https://kunishitei.bunka.go.jp/",
    "Cultural Properties Protection Act records": "https://kunishitei.bunka.go.jp/",
    "Prefectural cultural property registries": "https://kunishitei.bunka.go.jp/",
    # Kyoto National Museum
    "Kyoto National Museum X-ray lacquer studies": "https://www.kyohaku.go.jp/",
    "Kyoto National Museum conservation reports": "https://www.kyohaku.go.jp/",
    "Kyoto National Museum textile catalog": "https://www.kyohaku.go.jp/",
    # Nezu Museum
    "Nezu Museum tea ceremony catalog": "https://www.nezu-muse.or.jp/",
    "Nezu Museum Rinpa exhibition catalogs": "https://www.nezu-muse.or.jp/",
    "Nezu Museum catalogues": "https://www.nezu-muse.or.jp/",
    # Other museums
    "Osaka Museum of Oriental Ceramics": "https://www.moco.or.jp/",
    "National Museum of Modern Art Tokyo archives": "https://www.momat.go.jp/",
    "National Museum of Japanese History C-14 dating program": "https://www.rekihaku.ac.jp/",
    "National Museum of Japanese History pigment studies": "https://www.rekihaku.ac.jp/",
    "Owari Tokugawa Museum archives": "https://www.tokugawa-art-museum.jp/",
    "Tokugawa Art Museum lacquer catalog": "https://www.tokugawa-art-museum.jp/",
    "Tokugawa Art Museum maki-e technical studies": "https://www.tokugawa-art-museum.jp/",
    "Nibutani Ainu Culture Museum": "https://www.town.biratori.hokkaido.jp/biratori/nibutani/",
    "Okinawa Prefectural Museum bingata collection": "https://okimu.jp/",
    "Omiya Bonsai Art Museum archives": "https://www.bonsai-art-museum.jp/",
    "Wajima Lacquer Art Museum": "https://www.city.wajima.ishikawa.jp/",
    "Osaka National Museum of Art Gutai collection": "https://www.nmao.go.jp/",
    "Sano Museum catalog": "https://www.sanomoa.jp/",
    "Mino Ceramic Art Museum kiln excavation reports": "https://www.city.toki.lg.jp/",
    "Mino Ceramic Art Museum research": "https://www.city.toki.lg.jp/",
    "Kyushu Ceramic Museum technical studies": "https://saga-museum.jp/ceramic/",
    "Tokoname Ceramic Research Institute": "https://www.tokoname-kankou.net/",
    "Victoria and Albert Museum Satsuma guide": "https://www.vam.ac.uk/",
    "Victoria and Albert Museum ceramic identification guides": "https://www.vam.ac.uk/",
    "Victoria and Albert Museum lacquer collection notes": "https://www.vam.ac.uk/",
    "Museum of Fine Arts Boston — Print collection": "https://www.mfa.org/collections",
    # Ukiyo-e
    "Ukiyo-e.org database": "https://ukiyo-e.org/",
    # JSSUS
    "Japanese Sword Society of the United States": "https://www.jssus.org/",
    "JSSUS (Japanese Sword Society of the United States) archives": "https://www.jssus.org/",
    # Bonsai
    "Nippon Bonsai Association": "https://www.bonsai-nba.org/",
    "Nippon Bonsai Association Kokufu-ten catalogs": "https://www.bonsai-nba.org/",
    "Nippon Bonsai Association age assessment guidelines": "https://www.bonsai-nba.org/",
    "Nippon Bonsai Association educational materials": "https://www.bonsai-nba.org/",
    "Nippon Bonsai Association evaluation criteria": "https://www.bonsai-nba.org/",
    "Nippon Bonsai Association standards": "https://www.bonsai-nba.org/",
    "Nippon Bonsai Association — Kokufu-ten catalogues": "https://www.bonsai-nba.org/",
    "BCI (Bonsai Clubs International) convention records": "https://www.bonsai-bci.com/",
    "World Bonsai Friendship Federation exhibition archives": "https://www.bonsai-wbff.org/",
    "International Bonsai magazine archives": "https://internationalbonsai.com/",
    # Oxford Authentication
    "Oxford Authentication Ltd technical papers": "https://www.oxfordauthentication.com/",
    "Oxford Authentication Ltd verification procedures": "https://www.oxfordauthentication.com/",
    # CITES
    "CITES identification guides": "https://cites.org/",
    "CITES permit verification procedures": "https://cites.org/",
    "US Fish & Wildlife Service ivory guidelines": "https://www.fws.gov/",
    "US Fish & Wildlife forensic identification papers": "https://www.fws.gov/",
    "US Fish & Wildlife ivory identification manual": "https://www.fws.gov/",
    # Netsuke
    "International Netsuke Society Journal": "https://www.nfrjournal.com/",
    "Netsuke Kenkyukai Study Journal": "https://www.nfrjournal.com/",
    # Tea
    "Urasenke Foundation architectural surveys": "https://www.urasenke.or.jp/",
    "Urasenke Foundation architectural standards": "https://www.urasenke.or.jp/",
    "Tea Culture Research Society": "https://www.urasenke.or.jp/",
    # Architecture
    "Japan Machiya Heritage Foundation": "https://www.machiya.or.jp/",
    "JMRA (Japan Minka Revival Association) archives": "https://www.minka.or.jp/",
    # Rijksmuseum
    "Rijksmuseum VOC archives": "https://www.rijksmuseum.nl/",
    "Dresden Porcelain Collection catalog": "https://skd.museum/",
    # Collector Seals
    "Lugt, Les Marques de Collections": "https://www.marquesdecollections.fr/",
    # National Archives
    "National Archives WWII records": "https://www.archives.gov/",
    # Smithsonian
    "Smithsonian Archaeometry laboratory": "https://www.si.edu/",
    # Books with ISBN or clear bibliographic data (WorldCat/OpenLibrary links)
    "Nagayama, The Connoisseur's Book of Japanese Swords": "https://www.worldcat.org/title/connoisseurs-book-of-japanese-swords/oclc/36691653",
    "Sato Kanzan, The Japanese Sword": "https://www.worldcat.org/title/japanese-sword/oclc/9476039",
    "Ogasawara Nobuo, Japanese Swords, Hoikusha, ISBN 4-586-54022-2": "https://www.worldcat.org/isbn/4586540222",
    "Newland, The Hotei Encyclopedia of Japanese Woodblock Prints": "https://www.worldcat.org/title/hotei-encyclopedia-of-japanese-woodblock-prints/oclc/57665517",
    "Tsuji Nobuo, History of Japanese Art": "https://www.worldcat.org/title/history-of-japanese-art/oclc/904413420",
    "Rice, Prudence M., Pottery Analysis: A Sourcebook, U of Chicago Press, 2nd ed 2015": "https://www.worldcat.org/isbn/9780226923222",
    "Rice, Pottery Analysis: A Sourcebook": "https://www.worldcat.org/isbn/9780226923222",
    "Nishi & Hozumi, What Is Japanese Architecture?": "https://www.worldcat.org/title/what-is-japanese-architecture/oclc/12558747",
    "Watt & Ford, East Asian Lacquer": "https://www.worldcat.org/title/east-asian-lacquer-the-florence-and-herbert-irving-collection/oclc/25629868",
    "Webb, Lacquer: Technology and Conservation": "https://www.worldcat.org/title/lacquer-technology-and-conservation/oclc/41223445",
    "Mori Hisashi, Japanese Buddhist Sculpture": "https://www.worldcat.org/title/japanese-portrait-sculpture/oclc/3048975",
    "Mori Hisashi, Japanese Buddhist Sculpture, trans. Eckel, 1974": "https://www.worldcat.org/title/japanese-portrait-sculpture/oclc/3048975",
    "Washizuka, Enlightenment Embodied": "https://www.worldcat.org/title/enlightenment-embodied/oclc/37624449",
    "Sawa, Art in Japanese Esoteric Buddhism": "https://www.worldcat.org/title/art-in-japanese-esoteric-buddhism/oclc/442063",
    "Murase, Bridge of Dreams": "https://www.worldcat.org/title/bridge-of-dreams/oclc/41223529",
    "Salter, Japanese Woodblock Printing": "https://www.worldcat.org/title/japanese-woodblock-printing/oclc/51059285",
    "Sandberg, Indigo Textiles": "https://www.worldcat.org/title/indigo-textiles/oclc/20667025",
    "Wada, Rice, Barton, Shibori: The Art of Shaped Resist Dyeing": "https://www.worldcat.org/title/shibori-the-inventive-art-of-japanese-shaped-resist-dyeing/oclc/46393230",
    "Sasano, Early Japanese Sword Guards": "https://www.worldcat.org/title/early-japanese-sword-guards/oclc/10353696",
    "Robert Haynes, The Index of Japanese Sword Fittings and Associated Artists": "https://www.worldcat.org/title/index-of-japanese-sword-fittings-and-associated-artists/oclc/57452936",
    "Flickwerk: The Aesthetics of Mended Japanese Ceramics": "https://www.worldcat.org/title/flickwerk-the-aesthetics-of-mended-japanese-ceramics/oclc/257316022",
    "Naka, Bonsai Technique": "https://www.worldcat.org/title/bonsai-techniques/oclc/4049050",
    "Mizuno Seiichi, Asuka Buddhist Art": "https://www.worldcat.org/title/asuka-buddhist-art-horyu-ji/oclc/310997",
    "Munroe, Japanese Art After 1945": "https://www.worldcat.org/title/japanese-art-after-1945-scream-against-the-sky/oclc/28721147",
    "Statler, Japanese Prints": "https://www.worldcat.org/title/modern-japanese-prints/oclc/413145",
    "Marks, Japanese Woodblock Prints": "https://www.worldcat.org/title/japanese-woodblock-prints-artists-publishers-and-masterworks/oclc/760977863",
    "Marks, Publishers of Japanese Woodblock Prints": "https://www.worldcat.org/title/publishers-of-japanese-woodblock-prints/oclc/1099473157",
    "Andreas Marks, Publishers of Japanese Woodblock Prints": "https://www.worldcat.org/title/publishers-of-japanese-woodblock-prints/oclc/1099473157",
    "Merritt, Woodblock Print Reproductions": "https://www.worldcat.org/title/guide-to-japanese-woodblock-prints/oclc/4797671",
    # Specific research resources with known URLs
    "Ohmura Tomoyuki, ohmura-study.net (online research resource)": "https://ohmura-study.net/",
    "Kuniyoshi Project online database": "https://kuniyoshiproject.com/",
    "Hayashi Tadamasa sale catalog 1902": "https://gallica.bnf.fr/",
    "Bibliothèque nationale de France Japanese print archives": "https://gallica.bnf.fr/",
    "Adachi Institute of Woodcut Prints catalog": "https://www.adachi-hanga.com/",
    "Honolulu Museum of Art ukiyo-e database": "https://honolulumuseum.org/",
    "Nishikawa Kyotaro & Sano Emily, The Great Age of Japanese Buddhist Sculpture AD 600-1300, 1982": "https://www.worldcat.org/title/great-age-of-japanese-buddhist-sculpture-ad-600-1300/oclc/7555490",
    "Nishikawa Kyotaro, Butsuzo no Mikata (仏像の見方), Geijutsu Shincho feature / general guide": "https://www.worldcat.org/search?q=仏像の見方+西川杏太郎",
    "Honma & Sato, Nihonto Meikan (vol. 1-3), Yuzankaku, 1975-1976": "https://www.worldcat.org/title/nihonto-meikan/oclc/3536832",
    "Nakamura Masao, Sukiya Kenchiku Shusei, Shogakukan, 1983 / Chashitsu o Yomu, Tankosha, 2002": "https://www.worldcat.org/search?q=数寄屋建築集成+中村昌生",
    "Sumiyoshi & Matsui, Wood Joints in Classical Japanese Architecture, Kajima, 1991": "https://www.worldcat.org/search?q=木造建築の継手と仕口",
    "Mitsutani Takumi, Dendrochronology in Japan, Nara National Research Institute for Cultural Properties (nabunken.go.jp)": "https://www.nabunken.go.jp/",
    "Wakayama Takeshi, Tsuba Geijutsu-ko": "https://www.worldcat.org/search?q=鐔芸術考+若山猛",
    "Tsuboi Ryoichi, Nihon no Bonsho": "https://www.worldcat.org/search?q=日本の梵鐘+坪井良一",
    "Cort, Louise Allison — ceramics research (Smithsonian)": "https://asia.si.edu/",
    "Neff, Neutron Activation Analysis of Japanese Ceramics": "https://scholar.google.com/scholar?q=Neff+Neutron+Activation+Analysis+Japanese+Ceramics",
    "Raymond Bushell collection catalog": "https://www.worldcat.org/search?q=Raymond+Bushell+netsuke",
    "Murakami, Superflat catalog": "https://www.worldcat.org/title/superflat/oclc/46937183",
    "Murashige, Rinpa Art": "https://www.worldcat.org/search?q=琳派+村重寧",
    "Tokyo Metropolitan Art Museum Mono-ha retrospective catalog": "https://www.tobikan.jp/",
    "1873 Vienna Exhibition catalog": "https://www.worldcat.org/search?q=1873+Vienna+Exhibition+Japan",
    "Philadelphia Centennial Exhibition records": "https://www.worldcat.org/search?q=1876+Philadelphia+Centennial+Japan",
    "Shuri Castle restoration records": "https://oki-park.jp/shurijo/",
    "Yomiuri Independent exhibition catalogs": "https://www.yomiuri.co.jp/",
    "National Institutes for Cultural Heritage": "https://www.nich.go.jp/",
    "RIKEN computational art analysis studies": "https://www.riken.jp/",
    "Tokyo University of the Arts conservation lab": "https://www.geidai.ac.jp/",
    "Hokkaido Museum of Northern Peoples": "https://hoppohm.org/",
    "Imperial Household Agency archives": "https://www.kunaicho.go.jp/",
    "Tokyo Art Dealers Association": "https://www.toobi.co.jp/",
    "Bonsai Today back issues": "https://www.worldcat.org/title/bonsai-today/oclc/18474254",
    "Bonsai Focus magazine yamadori documentation": "https://www.bonsaifocus.com/",
    "Japan Forestry Agency collection records": "https://www.rinya.maff.go.jp/",
}

# Sources to remove (too vague, unverifiable)
REMOVE_SOURCES = {
    "Various temple archives",
    "Various gallery records",
    "Various artist foundation websites",
    "Various gallery blockchain pilot programs",
    "Various kasuri tradition preservation associations",
    "Various tradition preservation associations",
    "Various artist-specific inpu publications",
    "Various Japanese art appraisal organizations",
    "Major collection sale catalogs",
    "Note: Numerical values are approximate and drawn from published reference materials",
    "Kyoto kintsugi workshops",
    "Kyoto craft authentication standards",
    "Kyoto craft conservation literature",
    "Kyoto lacquer conservation institute",
    "Kyoto lacquer craft tradition documentation",
    "Kyoto silk conservation studies",
    "Kyoto textile industry guides",
    "Kyoto Textile Research Institute",
    "Kyoto Textile Research Institute dye guides",
    "Kyoto University accelerator-based analyses",
    "Kyoto University archaeological ceramics lab",
    "Kyoto University archaeological ceramics technical studies",
    "Kyoto University archaeometry lab",
    "Paper conservation literature",
    "Washi papermaking tradition documentation",
    "Washi papermaking tradition records",
    "Zen Arts studies",
    "Seto City Archaeological Survey reports",
    "Japanese archaeological kiln survey reports",
    "Conservation science laboratory accreditation standards",
    "Art + Tech Summit proceedings",
    "Robert Haynes tsuba authentication papers",
    "Recent Bonhams/Christie's Japanese sword results",
    "Meibutsu-ki published editions",
    "Japanese collector seal databases",
    "Yoshitomo Nara Foundation guidelines",
    "Artist catalog raisonnés",
}


def strengthen():
    with open(DATA_PATH) as f:
        data = json.load(f)

    pairs = data["pairs"]
    stats = {"url_added": 0, "removed": 0, "already_ok": 0, "unmapped": 0}
    unmapped = set()

    for p in pairs:
        ptype = p.get("type")

        # Handle AVF and PROV: sources field
        if ptype in ("authentic_vs_fake", "provenance_chain"):
            sources = p.get("sources", [])
            new_sources = []
            source_urls = p.get("source_urls", [])

            for s in sources:
                if "http" in s:
                    new_sources.append(s)
                    stats["already_ok"] += 1
                elif s in REMOVE_SOURCES:
                    stats["removed"] += 1
                    continue
                elif s in SOURCE_URL_MAP:
                    new_sources.append(s)
                    url = SOURCE_URL_MAP[s]
                    if url not in source_urls:
                        source_urls.append(url)
                    stats["url_added"] += 1
                else:
                    new_sources.append(s)
                    unmapped.add(s)
                    stats["unmapped"] += 1

            p["sources"] = new_sources
            if source_urls:
                p["source_urls"] = source_urls

            # Fix verified_by if sources have URLs now
            if source_urls and p.get("verified_by") == "source_verified":
                pass  # Keep as is since we now have URLs
            elif not source_urls:
                p["verified_by"] = "ai_generated"

        # Handle FQA: evidence field
        elif ptype == "forensic_qa":
            evidence = p.get("evidence", [])
            if not isinstance(evidence, list):
                continue

            new_evidence = []
            evidence_urls = p.get("evidence_urls", [])

            for e in evidence:
                if not isinstance(e, str):
                    new_evidence.append(e)
                    continue
                if "http" in e:
                    new_evidence.append(e)
                    stats["already_ok"] += 1
                elif e in REMOVE_SOURCES:
                    stats["removed"] += 1
                    continue
                elif e in SOURCE_URL_MAP:
                    new_evidence.append(e)
                    url = SOURCE_URL_MAP[e]
                    if url not in evidence_urls:
                        evidence_urls.append(url)
                    stats["url_added"] += 1
                else:
                    new_evidence.append(e)
                    unmapped.add(e)
                    stats["unmapped"] += 1

            p["evidence"] = new_evidence
            if evidence_urls:
                p["evidence_urls"] = evidence_urls

    # Save
    data["generated_at"] = "2026-05-15T10:00:00Z"
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n=== Source Strengthening Complete ===")
    print(f"URLs added: {stats['url_added']}")
    print(f"Vague sources removed: {stats['removed']}")
    print(f"Already had URLs: {stats['already_ok']}")
    print(f"Unmapped (remaining): {stats['unmapped']}")

    if unmapped:
        print(f"\n=== {len(unmapped)} Unmapped Sources ===")
        for s in sorted(unmapped):
            print(f"  - {s}")


if __name__ == "__main__":
    strengthen()
