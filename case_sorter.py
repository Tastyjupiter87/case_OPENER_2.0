import json

with open("all_skins2.json", "r", encoding="utf-8") as f:
    skins = json.load(f)

all_cases = set()

for skin in skins:
    for crate in skin.get("crates", []):
        all_cases.add(crate["name"])

all_cases = sorted(all_cases)

print("All Cases:")
for case_name in all_cases:
    print(case_name)
