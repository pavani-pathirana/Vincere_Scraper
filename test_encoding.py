import requests

# Test pcguide encoding
print("=== PCGUIDE.LK ===")
r1 = requests.get('https://www.pcguide.lk/category/tech-news/')
print(f"Encoding: {r1.encoding}")
print(f"Apparent encoding: {r1.apparent_encoding}")
print(f"Content-Type: {r1.headers.get('Content-Type')}")
print(f"First 200 chars of text: {r1.text[:200]}")

print("\n=== ADA.LK (for comparison) ===")
r2 = requests.get('https://www.ada.lk/technology')
print(f"Encoding: {r2.encoding}")
print(f"Apparent encoding: {r2.apparent_encoding}")
print(f"Content-Type: {r2.headers.get('Content-Type')}")
print(f"First 200 chars of text: {r2.text[:200]}")
