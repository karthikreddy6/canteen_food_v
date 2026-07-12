from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError
from io import BytesIO
from pathlib import Path

from PIL import Image


ITEMS = [
    "Chicken Biryani",
    "Mutton Biryani",
    "Egg Biryani",
    "Paneer Biryani",
    "Veg Biryani",
    "Chicken Fry Piece Biryani",
    "Special Family Biryani",
    "Chicken 65",
    "Chilli Chicken",
    "Chicken Manchurian",
    "Paneer 65",
    "Paneer Tikka",
    "Gobi Manchurian",
    "Crispy Corn",
    "French Fries",
    "Butter Chicken",
    "Chicken Curry",
    "Kadai Chicken",
    "Paneer Butter Masala",
    "Kadai Paneer",
    "Dal Tadka",
    "Dal Makhani",
    "Palak Paneer",
    "Butter Naan",
    "Garlic Naan",
    "Tandoori Roti",
    "Rumali Roti",
    "Kulcha",
    "Plain Dosa",
    "Masala Dosa",
    "Idli",
    "Vada",
    "Uttapam",
    "Pongal",
    "Veg Noodles",
    "Chicken Noodles",
    "Veg Fried Rice",
    "Chicken Fried Rice",
    "Egg Fried Rice",
    "Tea",
    "Coffee",
    "Sweet Lassi",
    "Buttermilk",
    "Fresh Lime Soda",
    "Mango Shake",
    "Chocolate Milkshake",
    "Coca Cola",
    "Gulab Jamun",
    "Rasgulla",
    "Double Ka Meetha",
    "Qubani Ka Meetha",
    "Ice Cream",
    "Chocolate Brownie",
    "Cheesecake",
]

USE_COMMONS_SEARCH = False


FALLBACK_QUERIES = {
    "Chicken Fry Piece Biryani": "Chicken biryani food",
    "Special Family Biryani": "Biryani food",
    "Paneer 65": "Paneer fry Indian food",
    "Crispy Corn": "Crispy corn food",
    "Kadai Chicken": "Chicken curry Indian food",
    "Kadai Paneer": "Paneer curry Indian food",
    "Rumali Roti": "Roti Indian bread",
    "Kulcha": "Naan Indian bread",
    "Chicken Noodles": "Chicken chow mein noodles food",
    "Egg Fried Rice": "Fried rice egg food",
    "Sweet Lassi": "Lassi drink",
    "Buttermilk": "Chaas buttermilk drink",
    "Fresh Lime Soda": "Lime soda drink",
    "Chocolate Milkshake": "Chocolate milkshake",
    "Coca Cola": "Coca Cola glass",
    "Double Ka Meetha": "Shahi tukda dessert",
    "Qubani Ka Meetha": "Apricot dessert",
}

FALLBACK_TAGS = {
    "Paneer Tikka": ["paneer", "tikka", "indian", "food"],
    "Chicken Curry": ["chicken", "curry", "indian", "food"],
    "Idli": ["idli", "south", "indian", "food"],
}


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "OnFoodLocalSeeder/1.0 (local development)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def search_commons(query: str) -> tuple[str, str] | None:
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrnamespace": "6",
        "gsrsearch": query,
        "gsrlimit": "8",
        "prop": "imageinfo",
        "iiprop": "url|mime",
        "iiurlwidth": "900",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    try:
        data = fetch_json(url)
    except HTTPError as exc:
        if exc.code == 429:
            print(f"RATE LIMITED Commons search for {query}; using fallback")
            return None
        raise
    except URLError:
        return None
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        mime = info.get("mime", "")
        image_url = info.get("thumburl") or info.get("url")
        if image_url and mime in {"image/jpeg", "image/png", "image/webp"}:
            return page.get("title", query), image_url
    return None


def fallback_photo_url(item: str) -> str:
    tags = FALLBACK_TAGS.get(item)
    if tags is None:
        tags = [part for part in re.split(r"[^a-z0-9]+", item.lower()) if part]
        tags.append("food")
    return "https://loremflickr.com/640/420/" + ",".join(tags)


def download_image(url: str) -> Image.Image:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "OnFoodLocalSeeder/1.0 (local development)"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read()
        return Image.open(BytesIO(data)).convert("RGB")


def save_cover(image: Image.Image, path: Path) -> None:
    target_w, target_h = 640, 420
    image.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (target_w, target_h), "white")
    x = (target_w - image.width) // 2
    y = (target_h - image.height) // 2
    canvas.paste(image, (x, y))
    canvas.save(path, "PNG", optimize=True)


def main() -> None:
    requested_items = sys.argv[1:] or ITEMS
    out_dir = Path("app/static/images")
    out_dir.mkdir(parents=True, exist_ok=True)
    source_lines = []
    failures = []

    for item in requested_items:
        queries = [f"{item} food"]
        fallback = FALLBACK_QUERIES.get(item)
        if fallback:
            queries.append(fallback)

        match = None
        if USE_COMMONS_SEARCH:
            for query in queries:
                match = search_commons(query)
                if match:
                    break
                time.sleep(1.5)

        if not match:
            match = ("Online photo search fallback", fallback_photo_url(item))

        title, image_url = match
        try:
            last_exc = None
            for _ in range(3):
                try:
                    image = download_image(image_url)
                    break
                except Exception as exc:
                    last_exc = exc
                    time.sleep(2.0)
            else:
                raise last_exc or RuntimeError("download failed")
            save_cover(image, out_dir / f"{slug(item)}.png")
            source_lines.append(f"{item}\t{title}\t{image_url}")
            print(f"OK {item} <- {title}")
        except Exception as exc:
            failures.append(item)
            print(f"FAIL {item}: {exc}")
        time.sleep(0.4)

    Path("app/static/images/SOURCES.tsv").write_text(
        "item\tcommons_title\tsource_url\n" + "\n".join(source_lines) + "\n",
        encoding="utf-8",
    )
    if failures:
        raise SystemExit("Could not download: " + ", ".join(failures))


if __name__ == "__main__":
    main()
