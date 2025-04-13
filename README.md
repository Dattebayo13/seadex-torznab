## Seadex-Torznab
A Torznab-compatible proxy that filters [Animetosho](https://animetosho.org/) search results using metadata from [Seadex](https://releases.moe).
## Installation
```bash
bash <(curl -s https://raw.githubusercontent.com/Dattebayo13/seadex-torznab/main/install.sh)
```
## Usage
Once the service is running, configure your indexer (e.g., Prowlarr) to point to http://localhost:49152/api. For Sonarr, it’s recommended to add the anime as a standard series type, as Sonarr will search for both individual episodes and the season pack for anime.
