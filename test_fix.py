#!/usr/bin/env python
"""Test encoding fix for pcguide scraper"""

import requests
from bs4 import BeautifulSoup

# Test WITHOUT encoding fix
print("=== WITHOUT ENCODING FIX ===")
r1 = requests.get('https://www.pcguide.lk/youtube-studio-new-update/')
print(f"Response encoding: {r1.encoding}")
soup1 = BeautifulSoup(r1.text, 'lxml')
title1 = soup1.select_one('h1').get_text(strip=True)
print(f"Title: {title1}")
print(f"First 100 chars: {title1[:100]}")

# Test WITH encoding fix
print("\n=== WITH ENCODING FIX (UTF-8) ===")
r2 = requests.get('https://www.pcguide.lk/youtube-studio-new-update/')
r2.encoding = 'utf-8'  # Force UTF-8
print(f"Response encoding: {r2.encoding}")
soup2 = BeautifulSoup(r2.text, 'lxml')
title2 = soup2.select_one('h1').get_text(strip=True)
print(f"Title: {title2}")
print(f"First 100 chars: {title2[:100]}")

# Check if it's proper Sinhala
if 'à' in title1:
    print("\n❌ WITHOUT FIX: Contains mojibake characters")
else:
    print("\n✓ WITHOUT FIX: Looks OK")
    
if 'à' in title2:
    print("❌ WITH FIX: Still has mojibake")
else:
    print("✓ WITH FIX: Proper Sinhala!")
