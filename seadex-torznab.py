from flask import Flask, request, Response
import requests
import xml.etree.ElementTree as ET
import re
import sys

app = Flask(__name__)

# Constants
ANIMETOSHO_TORZNAB_URL = "https://feed.animetosho.org/api"
SEADEX_TORRENTS_API = "https://releases.moe/api/collections/entries/records"
TORZNAB_NS = "http://torznab.com/schemas/2015/feed"

# Register torznab namespace
ET.register_namespace("torznab", TORZNAB_NS)

@app.route("/")
def home():
    return "Seadex-Torznab Running"

@app.route("/api")
def proxy():
    query_params = request.args.to_dict()

    # Return capabilities if requested
    if query_params.get("t") == "caps":
        caps_xml = """<?xml version="1.0" encoding="UTF-8" ?>
<caps>
  <server title="Seadex Animetosho Torznab" />
  <searching>
    <search available="yes" supportedParams="q" />
    <tv-search available="yes" supportedParams="q,season" />
    <movie-search available="yes" supportedParams="q" />
    <music-search available="no" supportedParams="q" />
    <audio-search available="no" supportedParams="q" />
    <book-search available="no" supportedParams="q" />
  </searching>
  <categories>
    <category id="5070" name="TV">
      <subcat id="5070" name="TV/Anime" />
    </category>
    <category id="105070" name="Anime" />
    <category id="102020" name="Movies/Other" />
    <category id="0" name="Other" />
  </categories>
  <tags />
</caps>
"""
        return Response(caps_xml, mimetype="application/rss+xml")

    # Normalize tvsearch to search
    if query_params.get("t") == "tvsearch":
        query_params["t"] = "search"

    # Fetch original Animetosho feed
    res = requests.get(ANIMETOSHO_TORZNAB_URL, params=query_params)
    tree = ET.fromstring(res.content)
    items = tree.findall(".//item")

    # If no query, return full results
    if not query_params.get("q"):
        return Response(ET.tostring(tree, encoding="utf-8"), mimetype="application/rss+xml")

    # Build Seadex filtering query from Animetosho links
    animetosho_links_query = ""
    for item in items:
        item_xml = ET.tostring(item, encoding='unicode')
        match = re.search(r'https://nyaa\.si/view/\d+', item_xml)
        if match:
            animetosho_links_query += f"trs.url%3F%3D'{match.group(0)}'%7C%7C"

    if not animetosho_links_query:
        return Response(ET.tostring(tree, encoding="utf-8"), mimetype="application/rss+xml")

    seadex_url = f"{SEADEX_TORRENTS_API}?filter={animetosho_links_query[:-6]}&expand=trs&skipTotal=true"
    seadex_response = requests.get(seadex_url).json()

    valid_animetosho_urls = {
        tr.get("url", "")
        for item in seadex_response.get("items", [])
        for tr in item.get("expand", {}).get("trs", [])
    }

    # Filter items not present in Seadex results
    channel = tree.find(".//channel")
    for item in items:
        desc = item.find("description")
        link_match = re.search(r'href="([^"]+)"', desc.text if desc is not None else "")
        if not link_match or link_match.group(1) not in valid_animetosho_urls:
            channel.remove(item)

    return Response(ET.tostring(tree, encoding="utf-8"), mimetype="application/rss+xml")

if __name__ == "__main__":
    port = 49152  # default port
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port. Using default port 49152.")
    app.run(port=port)
