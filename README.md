# Minecraft Plugin/Mod Crawler

This repository contains:
- **scraper**: Python scripts to crawl data from various Minecraft plugin/mod hosting sites.
- **data**: Raw JSON outputs and aggregated data.
- **web**: A React SPA for viewing and querying the scraped data.
- **.github/workflows**: GitHub Actions CI/CD workflows (e.g. daily scraper jobs).

## Getting Started
1. Run `pip install -r requirements.txt` in the `scraper` folder (when your dependencies are defined).
2. Run `python scraper/run_scraper.py` to scrape and generate aggregated data.
3. Go to `web` folder, run `npm install` and `npm run build` to build the React app.

See more documentation in `docs`.
