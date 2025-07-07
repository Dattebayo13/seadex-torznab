import re
import requests
from datetime import datetime, timezone
import seadex

ANIMETOSHO_FEED = "https://feed.animetosho.org/json?show=torrent"

seadex_wrapper = seadex.SeaDexEntry()


def torznab_info(title):
    """Fetch and format torrent info for a given title."""
    results = []
    try:
        entry = seadex_wrapper.from_title(title)
    except Exception as exc:
        # Logging should be handled by the caller
        return results
    notes = entry.notes
    for torrent in entry.torrents:
        if torrent.tracker.is_public():
            nyaa_id = torrent.url.split('/')[-1]
            tosho_response = requests.get(
                f"{ANIMETOSHO_FEED}&nyaa_id={nyaa_id}"
            ).json()
            results.append({
                'title': tosho_response['title'],
                'nyaa_id': nyaa_id,
                'guid': torrent.url,
                'pub_date': datetime.fromtimestamp(
                    tosho_response['timestamp'], timezone.utc
                ),
                'size': tosho_response['total_size'],
                'torrent_link': tosho_response['torrent_url'],
                'magnet_link': tosho_response['magnet_uri'],
                'description': notes,
                'is_best': torrent.is_best,
                'infohash': torrent.infohash,
                'files': tosho_response['num_files']
            })
    return results


def clean_query_and_extract_season(query):
    query = query.replace('+', ' ')
    match = re.search(
        r'(.*?)[\s\-_]*(?:S(?:eason)?\s*0*(\d{1,2}))$',
        query,
        re.IGNORECASE
    )
    if match:
        return match.group(1).strip(), int(match.group(2))
    return query.strip(), None


def create_search_xml(results):
    """Creates an RSS XML string from the search results."""
    rss_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="1.0" xmlns:atom="http://www.w3.org/2005/Atom" '
        'xmlns:torznab="http://torznab.com/schemas/2015/feed">\n'
        '  <channel>\n'
        '    <atom:link rel="self" type="application/rss+xml" />\n'
        '    <title>Seadex Torznab</title>'
    )
    for result in results:
        suffix = "SEABEST" if result['is_best'] else "SEAALT"
        full_title = f"{result['title']} [{suffix}]"
        rss_xml += (
            f'\n    <item>'
            f'\n      <title>{full_title}</title>'
            f'\n      <description>{result["description"]}</description>'
            f'\n      <guid>{result["guid"]}</guid>'
            f'\n      <pubDate>{result["pub_date"]}</pubDate>'
            f'\n      <size>{result["size"]}</size>'
            f'\n      <link>{result["torrent_link"]}</link>'
            f'\n      <category>5070</category>'
            f'\n      <enclosure url="{result["torrent_link"]}" '
            f'length="{result["size"]}" type="application/x-bittorrent" />'
            f'\n      <torznab:attr name="category" value="5070" />'
            f'\n      <torznab:attr name="files" value="{result["files"]}" />'
            f'\n      <torznab:attr name="infohash" value="{result["infohash"]}" />'
            f'\n    </item>'
        )
    rss_xml += '\n  </channel>\n</rss>\n'
    return rss_xml
