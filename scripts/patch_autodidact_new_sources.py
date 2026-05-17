"""
Patch for KANTEISHI Autodidact — Add Art Institute of Chicago + V&A Museum collectors.
This generates the collector classes and patches autodidact.py on Mac Mini.
"""

AIC_COLLECTOR = '''

class ArtInstituteChicagoCollector:
    """Collect Japanese art from Art Institute of Chicago API (14,000+ items).
    Uses Elasticsearch POST query for accurate place_of_origin filtering.
    No API key needed. Rate limit: 60 req/min for anonymous users.
    """
    BASE = "https://api.artic.edu/api/v1"
    IIIF_BASE = "https://www.artic.edu/iiif/2"
    FIELDS = [
        "id", "title", "place_of_origin", "department_title", "date_display",
        "medium_display", "image_id", "is_public_domain", "artist_display",
        "credit_line", "classification_title", "dimensions",
        "provenance_text", "catalogue_display", "exhibition_history",
        "publication_history", "inscriptions", "style_title", "technique_titles"
    ]

    # Category mapping based on AIC classification/department
    CATEGORY_MAP = {
        "sword": "swords", "blade": "swords", "katana": "swords",
        "tsuba": "metalwork", "guard": "metalwork", "fitting": "metalwork",
        "inro": "lacquerware", "lacquer": "lacquerware", "maki-e": "lacquerware",
        "netsuke": "netsuke", "toggle": "netsuke", "ojime": "netsuke",
        "print": "ukiyoe", "woodblock": "ukiyoe", "ukiyo": "ukiyoe",
        "painting": "painting", "screen": "painting", "scroll": "painting",
        "calligraphy": "painting",
        "textile": "textiles", "kimono": "textiles", "robe": "textiles",
        "ceramic": "ceramics", "porcelain": "ceramics", "stoneware": "ceramics",
        "tea bowl": "ceramics", "jar": "ceramics", "dish": "ceramics",
        "sculpture": "sculpture", "figure": "sculpture", "buddha": "sculpture",
        "bodhisattva": "sculpture",
        "bonsai": "bonsai",
        "furniture": "architecture", "architectural": "architecture",
        "screen": "architecture",
    }

    def _classify(self, item: dict) -> str:
        """Determine EDITION category from AIC data."""
        text = " ".join([
            str(item.get("title", "")),
            str(item.get("classification_title", "")),
            str(item.get("medium_display", "")),
            str(item.get("department_title", ""))
        ]).lower()
        for keyword, category in self.CATEGORY_MAP.items():
            if keyword in text:
                return category
        # Fallback by department
        dept = str(item.get("department_title", "")).lower()
        if "print" in dept:
            return "ukiyoe"
        if "asian" in dept:
            return "painting"
        if "textile" in dept:
            return "textiles"
        if "decorative" in dept:
            return "lacquerware"
        return "painting"  # safe default for Japanese art

    def collect_batch(self, batch_size: int = 20) -> int:
        """Collect a batch of Japanese artworks from AIC."""
        collected = 0
        page = random.randint(1, 500)

        try:
            # Use Elasticsearch query for accurate Japan filtering
            query_data = json.dumps({
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"place_of_origin": "Japan"}}
                        ],
                        "filter": [
                            {"term": {"is_public_domain": True}}
                        ]
                    }
                },
                "fields": self.FIELDS,
                "limit": batch_size,
                "page": page
            }).encode()

            req = urllib.request.Request(
                f"{self.BASE}/artworks/search",
                data=query_data,
                headers={"User-Agent": UA, "Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())

            for item in data.get("data", []):
                item_id = item.get("id")
                if not item_id:
                    continue

                category = self._classify(item)
                out_dir = DATA_ROOT / "data" / "aic" / category / str(item_id)

                if (out_dir / "metadata.json").exists():
                    continue

                out_dir.mkdir(parents=True, exist_ok=True)

                record = {
                    "source": "art_institute_chicago",
                    "source_url": f"https://www.artic.edu/artworks/{item_id}",
                    "aic_id": item_id,
                    "title": item.get("title", ""),
                    "artist": item.get("artist_display", ""),
                    "date": item.get("date_display", ""),
                    "medium": item.get("medium_display", ""),
                    "dimensions": item.get("dimensions", ""),
                    "department": item.get("department_title", ""),
                    "classification": item.get("classification_title", ""),
                    "style": item.get("style_title", ""),
                    "techniques": item.get("technique_titles", []),
                    "credit_line": item.get("credit_line", ""),
                    "provenance": item.get("provenance_text", ""),
                    "catalogue": item.get("catalogue_display", ""),
                    "exhibitions": item.get("exhibition_history", ""),
                    "publications": item.get("publication_history", ""),
                    "inscriptions": item.get("inscriptions", ""),
                    "place_of_origin": item.get("place_of_origin", ""),
                    "is_public_domain": item.get("is_public_domain", False),
                    "category": category,
                    "collected_at": datetime.now(timezone.utc).isoformat()
                }

                with open(out_dir / "metadata.json", "w", encoding="utf-8") as f:
                    json.dump(record, f, ensure_ascii=False, indent=2)

                # Download image via IIIF
                image_id = item.get("image_id")
                if image_id:
                    try:
                        img_url = f"{self.IIIF_BASE}/{image_id}/full/843,/0/default.jpg"
                        img_req = urllib.request.Request(img_url, headers={"User-Agent": UA})
                        with urllib.request.urlopen(img_req, timeout=60) as img_resp:
                            img_data = img_resp.read()
                        with open(out_dir / "primary.jpg", "wb") as f:
                            f.write(img_data)
                    except Exception:
                        pass

                collected += 1
                time.sleep(0.3)

        except Exception as e:
            log.warning(f"AIC collection error: {e}")

        return collected
'''

VA_COLLECTOR = '''

class VAMuseumCollector:
    """Collect Japanese art from Victoria & Albert Museum API.
    No API key needed. Rich metadata including maker, materials, techniques.
    """
    BASE = "https://api.vam.ac.uk/v2"

    QUERIES = [
        ("swords", "Japanese sword katana"),
        ("swords", "Japanese blade tanto"),
        ("ceramics", "Japanese tea bowl"),
        ("ceramics", "Japanese porcelain"),
        ("ceramics", "Japanese stoneware pottery"),
        ("ukiyoe", "Japanese print woodblock"),
        ("ukiyoe", "Japanese ukiyo-e"),
        ("painting", "Japanese painting scroll"),
        ("painting", "Japanese screen byobu"),
        ("lacquerware", "Japanese lacquer"),
        ("lacquerware", "Japanese inro"),
        ("netsuke", "Japanese netsuke"),
        ("netsuke", "Japanese toggle carving"),
        ("textiles", "Japanese textile kimono"),
        ("textiles", "Japanese embroidery"),
        ("metalwork", "Japanese tsuba sword guard"),
        ("metalwork", "Japanese metalwork bronze"),
        ("sculpture", "Japanese sculpture figure"),
        ("sculpture", "Japanese Buddhist"),
        ("bonsai", "Japanese bonsai"),
        ("architecture", "Japanese furniture"),
        ("contemporary", "Japanese contemporary art"),
    ]

    def collect_batch(self, batch_size: int = 15) -> int:
        """Collect a batch of Japanese artworks from V&A."""
        collected = 0
        category, query = random.choice(self.QUERIES)
        page = random.randint(1, 20)

        try:
            url = (f"{self.BASE}/objects/search"
                   f"?q={urllib.parse.quote(query)}"
                   f"&q_place_name=Japan"
                   f"&page_size={batch_size}"
                   f"&page={page}"
                   f"&images_exist=true")
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())

            for item in data.get("records", []):
                sys_num = item.get("systemNumber", "")
                if not sys_num:
                    continue

                out_dir = DATA_ROOT / "data" / "va_museum" / category / sys_num
                if (out_dir / "metadata.json").exists():
                    continue

                # Fetch full object details
                try:
                    detail_url = f"{self.BASE}/museumobject/{sys_num}"
                    detail_req = urllib.request.Request(detail_url, headers={"User-Agent": UA})
                    with urllib.request.urlopen(detail_req, timeout=30) as detail_resp:
                        detail = json.loads(detail_resp.read().decode())
                    obj = detail.get("record", {})
                except Exception:
                    obj = item

                out_dir.mkdir(parents=True, exist_ok=True)

                images = item.get("_images", {})
                record = {
                    "source": "victoria_albert_museum",
                    "source_url": f"https://collections.vam.ac.uk/item/{sys_num}",
                    "va_system_number": sys_num,
                    "accession_number": item.get("accessionNumber", ""),
                    "object_type": item.get("objectType", ""),
                    "title": item.get("_primaryTitle", obj.get("titles", [{}])[0].get("title", "") if obj.get("titles") else ""),
                    "maker": item.get("_primaryMaker", {}).get("name", ""),
                    "date": item.get("_primaryDate", ""),
                    "place": item.get("_primaryPlace", ""),
                    "materials": obj.get("materialsAndTechniques", ""),
                    "dimensions": obj.get("dimensionsNote", ""),
                    "description": obj.get("briefDescription", ""),
                    "history_note": obj.get("historyNote", ""),
                    "physical_description": obj.get("physicalDescription", ""),
                    "museum_number": item.get("accessionNumber", ""),
                    "category": category,
                    "thumbnail": images.get("_primary_thumbnail", ""),
                    "iiif_url": images.get("_iiif_image_base_url", ""),
                    "collected_at": datetime.now(timezone.utc).isoformat()
                }

                with open(out_dir / "metadata.json", "w", encoding="utf-8") as f:
                    json.dump(record, f, ensure_ascii=False, indent=2)

                # Download thumbnail
                thumb_url = images.get("_primary_thumbnail", "")
                if thumb_url:
                    try:
                        # Get higher res version
                        iiif_base = images.get("_iiif_image_base_url", "")
                        if iiif_base:
                            hi_res_url = f"{iiif_base}full/!800,800/0/default.jpg"
                        else:
                            hi_res_url = thumb_url
                        img_req = urllib.request.Request(hi_res_url, headers={"User-Agent": UA})
                        with urllib.request.urlopen(img_req, timeout=60) as img_resp:
                            img_data = img_resp.read()
                        with open(out_dir / "primary.jpg", "wb") as f:
                            f.write(img_data)
                    except Exception:
                        pass

                collected += 1
                time.sleep(0.5)

        except Exception as e:
            log.warning(f"V&A collection error: {e}")

        return collected
'''

# Generate the patch script to apply on Mac Mini
PATCH_SCRIPT = f'''#!/usr/bin/env python3
"""Apply AIC + V&A collector patches to autodidact.py"""
import re

AUTODIDACT_PATH = "/Users/hiroshi/edition-collab/kanteishi/autodidact.py"

with open(AUTODIDACT_PATH, "r") as f:
    content = f.read()

# Check if already patched
if "ArtInstituteChicagoCollector" in content:
    print("Already patched with AIC collector")
else:
    # Insert AIC collector before JapanSearchCollector
    aic_code = """{AIC_COLLECTOR}"""
    content = content.replace(
        "class JapanSearchCollector:",
        aic_code + "\\n\\nclass JapanSearchCollector:"
    )
    print("Added ArtInstituteChicagoCollector")

if "VAMuseumCollector" in content:
    print("Already patched with V&A collector")
else:
    # Insert V&A collector before ForgeryIntelligenceCollector
    va_code = """{VA_COLLECTOR}"""
    content = content.replace(
        "class ForgeryIntelligenceCollector:",
        va_code + "\\n\\nclass ForgeryIntelligenceCollector:"
    )
    print("Added VAMuseumCollector")

# Update run_learning_cycle to include new sources
old_cycle_steps = """    # 2. Japan Search collection (ColBase + NDL + national museums)
    log.info("[2/5] Japan Search collection...")"""

new_cycle_steps = """    # 2. Art Institute of Chicago collection
    log.info("[2/7] Art Institute of Chicago collection...")
    aic = ArtInstituteChicagoCollector()
    try:
        c = aic.collect_batch(batch_size=20)
        total_collected += c
        log.info(f"  Collected {{c}} items from Art Institute of Chicago")
    except Exception as e:
        log.warning(f"  AIC error: {{e}}")
    time.sleep(2)

    # 3. V&A Museum collection
    log.info("[3/7] V&A Museum collection...")
    va = VAMuseumCollector()
    try:
        c = va.collect_batch(batch_size=15)
        total_collected += c
        log.info(f"  Collected {{c}} items from V&A Museum")
    except Exception as e:
        log.warning(f"  V&A error: {{e}}")
    time.sleep(2)

    # 4. Japan Search collection (ColBase + NDL + national museums)
    log.info("[4/7] Japan Search collection...")"""

if "[2/7]" not in content:
    content = content.replace(old_cycle_steps, new_cycle_steps)
    # Update step numbers
    content = content.replace("[3/5] Forgery intelligence", "[5/7] Forgery intelligence")
    content = content.replace("[4/5] Japan Search knowledge", "[6/7] Japan Search knowledge")
    content = content.replace("[5/5] Growth metrics", "[7/7] Growth metrics")
    print("Updated learning cycle to 7 steps")

# Update total_items count to include AIC and V&A
old_count = """    met_dir = DATA_ROOT / "data" / "met_museum"
    total_items = 0
    cat_counts = {{}}
    if met_dir.exists():
        for cat_dir in met_dir.iterdir():
            if cat_dir.is_dir():
                count = len([d for d in cat_dir.iterdir() if d.is_dir()])
                cat_counts[cat_dir.name] = count
                total_items += count"""

new_count = """    # Count items across all museum sources
    total_items = 0
    cat_counts = {{}}
    for source_name in ["met_museum", "aic", "va_museum"]:
        source_dir = DATA_ROOT / "data" / source_name
        if source_dir.exists():
            for cat_dir in source_dir.iterdir():
                if cat_dir.is_dir():
                    count = len([d for d in cat_dir.iterdir() if d.is_dir()])
                    cat_counts[cat_dir.name] = cat_counts.get(cat_dir.name, 0) + count
                    total_items += count"""

if "aic" not in content.split("source_name")[0] if "source_name" in content else True:
    content = content.replace(old_count, new_count)
    print("Updated item counter to include AIC + V&A")

with open(AUTODIDACT_PATH, "w") as f:
    f.write(content)

print("\\nPatch complete! Restart autodidact to activate new sources.")
'''

# Write out
with open("/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/scripts/patch_autodidact_new_sources.py", "w") as f:
    f.write("# Auto-generated patch script\n")
    f.write(PATCH_SCRIPT)

print("Patch script generated")
