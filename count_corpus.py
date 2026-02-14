import os

total = 0
sites = {}

for root, dirs, files in os.walk('vincere_corpus'):
    for f in files:
        if f.endswith('.json'):
            total += 1
            parts = root.split(os.sep)
            site = parts[1] if len(parts) > 1 else 'unknown'
            sites[site] = sites.get(site, 0) + 1

print(f'Total articles: {total}')
print('\nBreakdown by site:')
for s in sorted(sites.keys()):
    print(f'  {s}: {sites[s]} articles')
