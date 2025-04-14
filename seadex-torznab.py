import re
import sys
from datetime import datetime, timezone

import requests
from flask import Flask, request, Response
import seadex
import logging

logging.basicConfig(
    filename='seadex_torznab.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
)

ANIMETOSHO_FEED = "https://feed.animetosho.org/json?show=torrent"

seadexWrapper = seadex.SeaDexEntry()

app = Flask(__name__)

def torznabInfo(title):
    results = []
    try:
        entry = seadexWrapper.from_title(title)
    except Exception as e:
        logging.error(f"Failed to fetch entry for title '{title}': {e}")
        return results
    notes = entry.notes
    for torrent in entry.torrents:
        if torrent.tracker.is_public():
            nyaaID = torrent.url.split('/')[-1]
            toshoResponse = requests.get(f"{ANIMETOSHO_FEED}&nyaa_id={nyaaID}").json()
            results.append({
                'title': toshoResponse['title'],
                'nyaaID': nyaaID,
                'guid': torrent.url,
                'pubDate': datetime.fromtimestamp(toshoResponse['timestamp'], timezone.utc),
                'size': toshoResponse['total_size'],
                'torrentLink': toshoResponse['torrent_url'],
                'magnetLink': toshoResponse['magnet_uri'],
                'description': notes,
                'isBest': torrent.is_best,
                'infohash': torrent.infohash,
                'files': toshoResponse['num_files']
            })
    return results

def clean_query_and_extract_season(q):
    q = q.replace('+', ' ')
    match = re.search(r'(.*?)[\s\-_]*(?:S(?:eason)?\s*0*(\d{1,2}))$', q, re.IGNORECASE)
    if match:
        return match.group(1).strip(), int(match.group(2))
    return q.strip(), None

def create_search_xml(results):
    """Creates an RSS XML string from the search results."""
    rss_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="1.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:torznab="http://torznab.com/schemas/2015/feed">
  <channel>
    <atom:link rel="self" type="application/rss+xml" />
    <title>Seadex Torznab</title>'''
    for result in results:
        suffix = "SEABEST" if result['isBest'] else "SEAALT"
        full_title = f"{result['title']} [{suffix}]"
        rss_xml += f'''
    <item>
      <title>{full_title}</title>
      <description>{result['description']}</description>
      <guid>{result['guid']}</guid>
      <pubDate>{result['pubDate']}</pubDate>
      <size>{result['size']}</size>
      <link>{result["torrentLink"]}</link>
      <category>5070</category>
      <enclosure url="{result['torrentLink']}" length="{result['size']}" type="application/x-bittorrent" />
      <torznab:attr name="category" value="5070" />
      <torznab:attr name="files" value="{result['files']}" />
      <torznab:attr name="infohash" value="{result['infohash']}" />
    </item>'''
    rss_xml += '''
  </channel>
</rss>'''
    return rss_xml

@app.route('/api')
def parseURL():
    query_params = request.args.to_dict()
    q = query_params.get("q", "")
    season_param = query_params.get("season")
    title_base, parsed_season = clean_query_and_extract_season(q)

    if season_param and int(season_param) > 1:
        season = int(season_param)
    elif parsed_season and parsed_season > 1:
        season = parsed_season
    else:
        season = None

    title = f"{title_base} Season {season}" if season else title_base

    t = query_params.get("t", "search")

    if t == 'caps':
        capabilities_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<caps>
  <server title="Seadex Torznab" />
  <limits default="100" max="100" />
  <searching>
    <search available="yes" supportedParams="q" />
    <tv-search available="yes" supportedParams="q,season" />
    <movie-search available="no" supportedParams="q" />
    <music-search available="no" supportedParams="q" />
    <audio-search available="no" supportedParams="q" />
    <book-search available="no" supportedParams="q" />
  </searching>
  <categories>
    <category id="0" name="Other" />
    <category id="5000" name="TV">
      <subcat id="5070" name="TV/Anime" />
    </category>
    <category id="8000" name="Other" />
  </categories>
  <tags />
</caps>
        '''
        return Response(capabilities_xml, mimetype='application/rss+xml')
    elif t == 'search' or t == 'tvsearch':
      results = torznabInfo(title if q else "Naruto")
      rss_xml = create_search_xml(results)
      return Response(rss_xml, mimetype='application/rss+xml')

@app.route('/logs')
def show_logs():
    try:
        with open('seadex_torznab.log', 'r', encoding='utf-8') as log_file:
            lines = log_file.readlines()[-100:]  # Show last 100 lines
    except FileNotFoundError:
        lines = ["Log file not found."]

    log_html = "<br>".join(line.strip() for line in lines)

    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Seadex Torznab Logs</title>
        <style>
            body {{
                font-family: monospace;
                background: #1e1e1e;
                color: #e0e0e0;
                padding: 20px;
            }}
            .log-container {{
                background: #2e2e2e;
                border-radius: 8px;
                padding: 20px;
                overflow-y: auto;
                max-height: 90vh;
            }}
            h1 {{
                color: #f39c12;
            }}
            a {{
                color: #3498db;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <h1>📜 Seadex Torznab Logs</h1>
        <div class="log-container">
            <pre>{log_html}</pre>
        </div>
    </body>
    </html>
    '''

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Seadex Torznab API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                color: #333;
                text-align: center;
                padding-top: 50px;
            }
            .container {
                background: white;
                display: inline-block;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
            }
            p {
                font-size: 18px;
            }
            a {
                color: #3498db;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ Seadex-Torznab is running</h1>
            <p>Use the <code>/api?t=search&amp;q=Your+Anime+Name</code> endpoint to search.</p>
        </div>
    </body>
    </html>
    '''

if __name__ == "__main__":
    port = 49152  # default port
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port. Using default port 49152.")
    app.run(port=port)
