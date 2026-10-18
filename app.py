import os
import re
from urllib.parse import urlparse
import requests
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv

load_dotenv()  # .env file se TINYFISH_API_KEY padhta hai

app = Flask(__name__)

API_KEY = os.getenv("TINYFISH_API_KEY")
SEARCH_URL = "https://api.search.tinyfish.ai"

# Har branch ke liye keywords. Yahan apni branches add kar sakte ho.
BRANCH_TOPICS = {
    "CSE": "computer science software AI",
    "ECE": "electronics embedded systems VLSI IoT",
    "EEE": "electrical engineering power systems",
    "Mechanical": "mechanical engineering robotics automotive",
    "Civil": "civil engineering infrastructure construction",
}


# Har branch ke hackathon kis theme ke hote hain. Isse search specific hota hai.
BRANCH_HACK_THEMES = {
    "CSE": "AI web app software",
    "ECE": "IoT embedded hardware VLSI semiconductor",
    "EEE": "power energy electric vehicle smart grid",
    "Mechanical": "robotics automotive design manufacturing",
    "Civil": "smart city infrastructure sustainability construction",
}

# Social media links aksar login maangte hain ya khulte nahi, isliye hata dete hain.
BLOCKED_DOMAINS = (
    "instagram.com", "facebook.com", "fb.com", "tiktok.com",
    "pinterest.com", "linkedin.com", "twitter.com", "x.com",
)

# Hackathon ke asli platforms. Ye results mein pehle dikhte hain.
HACKATHON_SITES = (
    "unstop.com", "devfolio.co", "devpost.com", "mlh.io",
    "hackerearth.com", "dorahacks.io", "hack2skill.com",
)


def domain_of(url):
    host = urlparse(url or "").netloc.lower()
    return host[4:] if host.startswith("www.") else host


def matches(host, domains):
    return any(host == d or host.endswith("." + d) for d in domains)


# Ye "listing" pages hain (jaise "2540+ Hackathons in India"). User inhe seedha
# Unstop/Internshala pe bhi dekh sakta hai, isliye hum asli event pages dikhate hain.
LISTING_TITLE = re.compile(
    r"\b\d[\d,]*\+?\s+hackathons?\b|hackathons? in (india|\w+ 20\d\d)"
    r"|find\s*&?\s*join|list of|best hackathons|^upcoming (events?|hackathons?)$",
    re.IGNORECASE,
)
LISTING_PATHS = ("/hackathons", "/allhacks", "/competitions/hackathons", "/hackathon-listing")


def is_listing(item):
    path = urlparse(item["url"]).path.rstrip("/").lower()
    return bool(LISTING_TITLE.search(item["title"] or "")) or path.endswith(LISTING_PATHS)


def tinyfish_search(query, news=False, prefer=(), drop_listings=False, limit=6):
    """TinyFish search chalata hai, social links hata deta hai, aur
    prefer wali sites ko pehle rakhta hai."""
    params = {"query": query, "location": "IN", "language": "en"}
    if news:
        params["domain_type"] = "news"  # agar error aaye to ye line hata dena
    headers = {"X-API-Key": API_KEY}
    r = requests.get(SEARCH_URL, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()

    items = []
    for item in data.get("results", []):
        site = item.get("site_name") or ""
        if item.get("date"):
            site = f"{site} \u00b7 {item['date']}"
        items.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "snippet": item.get("snippet"),
            "site": site,
        })

    # social media wale links hatao
    items = [i for i in items if i["url"] and not matches(domain_of(i["url"]), BLOCKED_DOMAINS)]
    if drop_listings:
        items = [i for i in items if not is_listing(i)]
    # asli platforms ko upar lao (sort stable hai, baaki ka order wahi rehta hai)
    if prefer:
        items.sort(key=lambda i: 0 if matches(domain_of(i["url"]), prefer) else 1)
    return items[:limit]


def search_hackathons(branch):
    """Branch ke theme ke hisaab se 2 searches, phir merge aur duplicates hatao."""
    theme = BRANCH_HACK_THEMES.get(branch, branch)
    queries = [
        f"{theme} hackathon India 2026 registration deadline",
        f"{branch} students hackathon India 2026 register",
    ]
    merged, seen = [], set()
    for q in queries:
        for item in tinyfish_search(q, prefer=HACKATHON_SITES, drop_listings=True, limit=10):
            if item["url"] not in seen:
                seen.add(item["url"])
                merged.append(item)
    return merged[:6]


@app.route("/")
def home():
    return render_template("index.html", branches=list(BRANCH_TOPICS.keys()))


@app.route("/api/feed")
def feed():
    branch = request.args.get("branch", "CSE")
    topic = BRANCH_TOPICS.get(branch)
    if not topic:
        return jsonify({"error": "Unknown branch"}), 400
    if not API_KEY:
        return jsonify({"error": "TINYFISH_API_KEY set nahi hai (.env check karo)"}), 500

    try:
        return jsonify({
            "branch": branch,
            "news": tinyfish_search(f"latest {topic} news", news=True),
            "hackathons": search_hackathons(branch),
            "tech": tinyfish_search(f"new technology trends {topic} 2026"),
        })
    except requests.RequestException as e:
        return jsonify({"error": f"TinyFish call fail hui: {e}"}), 502


if __name__ == "__main__":
    app.run(debug=True)
