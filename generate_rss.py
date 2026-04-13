import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime
import email.utils
import time
import re
import os
from urllib.parse import urljoin
from xml.dom import minidom

# Set the absolute path for the output file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "trumpstruth_feed.xml")

def parse_date(date_str):
    date_str = date_str.strip()
    try:
        dt = datetime.strptime(date_str, "%B %d, %Y, %I:%M %p")
        return email.utils.formatdate(time.mktime(dt.timetuple()), localtime=True)
    except Exception:
        return email.utils.formatdate()

def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def generate_rss():
    base_url = "https://trumpstruth.org"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    max_pages = 5
    current_url = base_url
    all_statuses = []

    print(f"[{datetime.now()}] Starting RSS generation - Fetching up to {max_pages} pages...")

    for page_num in range(1, max_pages + 1):
        try:
            print(f"[{datetime.now()}] Fetching page {page_num}: {current_url}")
            response = requests.get(current_url, headers=headers, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"[{datetime.now()}] Error fetching page {page_num}: {e}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        
        page_statuses = soup.find_all('div', class_='status')
        if not page_statuses:
            print(f"[{datetime.now()}] No posts found on page {page_num}. Ending scrape.")
            break
            
        all_statuses.extend(page_statuses)
        print(f"[{datetime.now()}] Collected {len(page_statuses)} posts from page {page_num}.")

        # More robust search for "Next Page"
        next_link = None
        for a in soup.find_all('a', class_='button'):
            if 'Next Page' in a.get_text():
                next_link = a
                break
        
        if next_link and next_link.get('href'):
            current_url = urljoin(base_url, next_link.get('href'))
        else:
            print(f"[{datetime.now()}] No 'Next Page' link found. Ending scrape.")
            break
        
        time.sleep(1)

    print(f"[{datetime.now()}] Total posts collected: {len(all_statuses)}")

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = "Trump's Truth RSS Feed"
    ET.SubElement(channel, "link").text = base_url
    ET.SubElement(channel, "description").text = f"Truth Social Archive - Latest {len(all_statuses)} Posts"
    ET.SubElement(channel, "lastBuildDate").text = email.utils.formatdate()

    for status in all_statuses:
        item = ET.SubElement(channel, "item")
        
        body = status.find('div', class_='status__body')
        description = body.get_text(separator=' ', strip=True) if body else ""
        ET.SubElement(item, "description").text = description
        ET.SubElement(item, "title").text = (description[:77] + '...') if len(description) > 80 else description

        header = status.find('div', class_='status__header')
        if header:
            link_tag = header.find('a', class_='status__external-link')
            link = link_tag.get('href') if link_tag else base_url
            ET.SubElement(item, "link").text = link
            ET.SubElement(item, "guid").text = link
            
            header_text = header.get_text(separator=' ', strip=True)
            match = re.search(r'·\s*(.*?)\s*Original Post', header_text)
            date_str = match.group(1) if match else ""
            ET.SubElement(item, "pubDate").text = parse_date(date_str)

    # Use prettify for multi-line output
    xml_str = prettify(rss)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(xml_str)
        
    print(f"[{datetime.now()}] RSS feed generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_rss()
