import requests

print("Checking which pages exist...\n")
for i in range(1, 6):
    url = f"https://www.pcguide.lk/category/tech-news/page/{i}/"
    r = requests.get(url, timeout=10)
    print(f"Page {i}: {r.status_code}")
