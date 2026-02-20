import json
import glob

files = glob.glob('vincere_corpus/asianmirror/local/*.json')
print(f'Asian Mirror articles found: {len(files)}\n')

if files:
    for f in files[:3]:
        data = json.load(open(f, encoding='utf-8'))
        print('='*70)
        print(f"Headline: {data['headline']}")
        print(f"Word count: {data['word_count']}")
        print(f"Date: {data.get('date', 'N/A')}")
        print(f"Body preview:\n{data['body'][:300]}...")
        print()
