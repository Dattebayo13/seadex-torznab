# Seadex-Torznab

A Torznab-compatible proxy that searches for anime using [Seadex](https://releases.moe) and gets torrent information from [Animetosho](https://animetosho.org/).

## Installation

Requires Python 3.10+ and git.

### Quick Install (Recommended)

```bash
bash <(curl -s https://raw.githubusercontent.com/Dattebayo13/seadex-torznab/main/install.sh)
```
- The script will set up a Python virtual environment in your home directory, install the latest version from GitHub, and optionally set up a user systemd service to run on login.
- To uninstall, run the script again and choose "Uninstall".

### Manual Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install "git+https://github.com/Dattebayo13/seadex-torznab.git"
```

## Usage

```bash
# If installed via the script or pip:
seadex-torznab
# Or, if running from source:
python -m seadex_torznab
```

- By default, the service runs on port 49152.
- To run as a background service on login, use the systemd option in the install script.

Once the service is running, configure your indexer (e.g., Prowlarr) to point to http://localhost:49152/api.

For Sonarr, it's recommended to add the anime as a standard series type, as Sonarr will search for both individual episodes and the season pack for anime. Torrent titles are appended with [SEABEST] or [SEAALT] to allow for easy identification.
