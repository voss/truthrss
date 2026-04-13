# TruthRSS

A serverless RSS feed generator and viewer for Truth Social posts archived on [trumpstruth.org](https://trumpstruth.org).

## Features
- **Automated Scraping**: A Python script (`generate_rss.py`) scrapes the latest posts and generates an RSS 2.0 feed.
- **GitHub Actions Integration**: Updates the feed automatically every 10 minutes.
- **Web Interface**: A clean, single-page application (`index.html`) to view the feed with auto-refresh.
- **Timezone Support**: Displays post timestamps in the original format and Central European Time (CET/CEST).

## Architecture
- **Scraper**: Python (BeautifulSoup, requests)
- **Frontend**: Vanilla HTML/JS/CSS
- **Storage/Automation**: GitHub Actions & Repository

## Local Development
To view the feed locally, run a simple web server:
```bash
python3 -m http.server
```
Then open `http://localhost:8000` in your browser.
