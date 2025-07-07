from flask import Flask
from seadex_torznab.logging_config import setup_logging
from seadex_torznab.routes import register_routes

app = Flask(__name__)
setup_logging()
register_routes(app) 