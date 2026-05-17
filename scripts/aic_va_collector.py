"""
Art Institute of Chicago + V&A Museum Collectors for KANTEISHI Autodidact.
This file is transferred to Mac Mini and inserted into autodidact.py.
"""


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
    }

    def _classify(self, item):
        text = " ".join([
            str(item.get("title", "")),
            str(item.get("classification_title", "")),
            str(item.get("medium_display", "")),
            str(item.get("department_title", ""))
        ]).lower()
        for keyword, category in self.CATEGORY_MAP.items():
            if keyword in text:
                return category
        dept = str(item.get("department_title", "")).lower()
        if "print" in dept:
            return "ukiyoe"
        if "asian" in dept:
            return "painting"
        if "textile" in dept:
            return "textiles"
        if "decorative" in dept:
            return "lacquerware"
        return "painting"

    def collect_batch(self, batch_size=20):
        collected = 0
        page = random.randint(1, 500)
        try:
            query_data = json.dumps({
                "query": {
                    "bool": {
                        "must": [{"match": {"place_of_origin": "Japan"}}],
                        "filter": [{"term": {"is_public_domain": True}}]
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

    def collect_batch(self, batch_size=15):
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
                    "title": item.get("_primaryTitle", ""),
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
                thumb_url = images.get("_primary_thumbnail", "")
                if thumb_url:
                    try:
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
