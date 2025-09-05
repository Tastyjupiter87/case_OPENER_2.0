import json

# Load JSON file
with open("all_skins2.json", "r", encoding="utf-8") as f:
    skins = json.load(f)

# Collect all unique cases
all_cases = set()
for skin in skins:
    for case_name in skin.get("cases", []):
        if case_name:  # skip empty entries
            all_cases.add(case_name)

# Convert to sorted list
all_cases = sorted(all_cases)

# Print the list
print("All cases found in JSON:")
for i, case in enumerate(all_cases, start=1):
    print(f"{i}. {case}")

