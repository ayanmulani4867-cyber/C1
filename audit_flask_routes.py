from app import create_app

app = create_app('testing')

print(f"{'ENDPOINT':<35} | {'METHODS':<20} | {'RULE':<45}")
print("-" * 105)

endpoints_by_bp = {}
for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
    methods = ','.join([m for m in rule.methods if m not in ('HEAD', 'OPTIONS')])
    bp = rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'global'
    endpoints_by_bp.setdefault(bp, []).append((rule.endpoint, methods, rule.rule))
    print(f"{rule.endpoint:<35} | {methods:<20} | {rule.rule:<45}")

print(f"\nTotal endpoints: {len(list(app.url_map.iter_rules()))}")
