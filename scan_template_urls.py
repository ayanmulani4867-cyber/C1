import os
import re
from app import create_app

app = create_app('testing')
valid_endpoints = set(rule.endpoint for rule in app.url_map.iter_rules())

template_dir = os.path.join(os.path.dirname(__file__), 'app', 'templates')
url_for_pattern = re.compile(r"url_for\(\s*['\"]([^'\"]+)['\"]([^)]*)\)")

print(f"Scanning templates in {template_dir}...")
broken_urls = []

for root, dirs, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, template_dir)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = url_for_pattern.findall(content)
                for endpoint, args in matches:
                    if endpoint not in valid_endpoints and endpoint != 'static':
                        broken_urls.append((relpath, endpoint, args.strip()))

if broken_urls:
    print(f"\nFOUND {len(broken_urls)} BROKEN URL_FOR REFERENCES:")
    for relpath, endpoint, args in broken_urls:
        print(f"  In '{relpath}': url_for('{endpoint}', {args})")
else:
    print("\nALL url_for references in all templates are valid!")
