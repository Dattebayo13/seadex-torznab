from flask import request, Response, jsonify
from seadex_torznab.torznab import torznab_info, create_search_xml, clean_query_and_extract_season
import logging


def _parse_search_params():
    query_params = request.args.to_dict()
    query = query_params.get("q", "")
    season_param = query_params.get("season")
    title_base, parsed_season = clean_query_and_extract_season(query)

    if season_param and int(season_param) > 1:
        season = int(season_param)
    elif parsed_season and parsed_season > 1:
        season = parsed_season
    else:
        season = None

    title = f"{title_base} Season {season}" if season else title_base
    return query_params, query, title


def register_routes(app):
    """Register all routes for the Flask app."""

    @app.route('/api')
    def api_parse_url():
        """Handle the /api endpoint for search and capabilities."""
        query_params, query, title = _parse_search_params()
        search_type = query_params.get("t", "search")

        if search_type == 'caps':
            capabilities_xml = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<caps>\n'
                '  <server title="Seadex Torznab" />\n'
                '  <limits default="100" max="100" />\n'
                '  <searching>\n'
                '    <search available="yes" supportedParams="q" />\n'
                '    <tv-search available="yes" supportedParams="q,season" />\n'
                '    <movie-search available="no" supportedParams="q" />\n'
                '    <music-search available="no" supportedParams="q" />\n'
                '    <audio-search available="no" supportedParams="q" />\n'
                '    <book-search available="no" supportedParams="q" />\n'
                '  </searching>\n'
                '  <categories>\n'
                '    <category id="0" name="Other" />\n'
                '    <category id="5000" name="TV">\n'
                '      <subcat id="5070" name="TV/Anime" />\n'
                '    </category>\n'
                '    <category id="8000" name="Other" />\n'
                '  </categories>\n'
                '  <tags />\n'
                '</caps>'
            )
            return Response(capabilities_xml, mimetype='application/rss+xml')
        elif search_type in ('search', 'tvsearch'):
            try:
                results = torznab_info(title if query else "Naruto")
            except Exception as error:
                logging.error(f"Error in torznab_info: {error}")
                results = []
            rss_xml = create_search_xml(results)
            return Response(rss_xml, mimetype='application/rss+xml')
        return Response("", status=204)

    @app.route('/json')
    def api_json():
        """Handle the /api/json endpoint for direct JSON search results."""
        _, query, title = _parse_search_params()
        try:
            results = torznab_info(title if query else "Naruto")
        except Exception as error:
            logging.error(f"Error in torznab_info (JSON): {error}")
            results = []
        return jsonify(results)

    @app.route('/logs')
    def show_logs():
        """Display the last 100 lines of the log file as HTML."""
        try:
            with open('seadex_torznab.log', 'r', encoding='utf-8') as log_file:
                log_lines = log_file.readlines()[-100:]
        except FileNotFoundError:
            log_lines = ["Log file not found."]
        log_html = "<br>".join(line.strip() for line in log_lines)
        return (
            '<!DOCTYPE html>'
            '<html lang="en">'
            '<head>'
            '    <meta charset="UTF-8">'
            '    <title>Seadex Torznab Logs</title>'
            '    <style>'
            '        body {font-family: monospace; background: #1e1e1e; color: #e0e0e0; padding: 20px;}'
            '        .log-container {background: #2e2e2e; border-radius: 8px; padding: 20px; overflow-y: auto; max-height: 90vh;}'
            '        h1 {color: #4169E1;}'
            '        a {color: #3498db; text-decoration: none;}'
            '    </style>'
            '</head>'
            '<body>'
            '    <h1>Seadex Torznab Logs</h1>'
            '    <div class="log-container">'
            f'        <pre>{log_html}</pre>'
            '    </div>'
            '</body>'
            '</html>'
        )

    @app.route('/')
    def home():
        """Display the home page."""
        return (
            '<!DOCTYPE html>'
            '<html lang="en">'
            '<head>'
            '    <meta charset="UTF-8">'
            '    <title>Seadex Torznab API</title>'
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">'
            '    <style>'
            '        body {font-family: "Segoe UI", Arial, sans-serif; background: linear-gradient(120deg, #f4f4f4 0%, #e0e7ff 100%); color: #333; text-align: center; padding-top: 60px; margin: 0;}'
            '        .container {background: white; display: inline-block; padding: 40px 40px 30px 40px; border-radius: 16px; box-shadow: 0 8px 24px rgba(44,62,80,0.10); min-width: 350px;}'
            '        h1 {color: #2c3e50; font-size: 2.2em; margin-bottom: 1em;}'
            '        form {margin-bottom: 1.5em;}'
            '        .search-bar {display: flex; justify-content: center; align-items: center; gap: 0;}'
            '        input[type="text"] {padding: 12px 16px; border: 1px solid #bfc9d9; border-radius: 6px 0 0 6px; font-size: 1em; outline: none; width: 220px;}'
            '        button {padding: 12.6px 20px; border: none; background: #4169E1; color: white; font-size: 1em; border-radius: 0 6px 6px 0; cursor: pointer;}'
            '    </style>'
            '</head>'
            '<body>'
            '    <div class="container">'
            '        <h1>Seadex-Torznab is running</h1>'
            '        <form action="/api" method="get" autocomplete="off">'
            '            <div class="search-bar">'
            '                <input type="hidden" name="t" value="search">'
            '                <input type="text" name="q" placeholder="Search anime..." required>'
            '                <button type="submit">Search</button>'
            '            </div>'
            '        </form>'
            '        <div class="footer">'
            '            <a href="/logs">View Logs</a>'
            '        </div>'
            '    </div>'
            '</body>'
            '</html>'
        )
