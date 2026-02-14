"""Test if LankaTruth main site is accessible"""
import requests

urls = [
    'https://lankatruth.com/',
    'https://lankatruth.com/si/',
    'https://lankatruth.com/si/?cat=3',
]

for url in urls:
    try:
        resp = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        print(f"{url:50s} | Status: {resp.status_code}")
    except Exception as e:
        print(f"{url:50s} | ERROR: {e}")
