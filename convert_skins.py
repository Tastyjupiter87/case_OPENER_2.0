import json
import os

INPUT_FILE = "all_skins2.json"
OUTPUT_FILE = "processed_skins.json"

if not os.path.exists(INPUT_FILE):
    print(f"Error: {INPUT_FILE} not found in current folder!")
    input("Press Enter to exit...")
    exit()

# Load JSON
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    try:
        data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error reading JSON: {e}")
        input("Press Enter to exit...")
        exit()

processed_skins = []

for skin in data:
    name = skin.get("name", "Unknown")
    rarity = skin.get("rarity", {}).get("name", "Unknown")
    weapon_name = skin.get("weapon", {}).get("name", "Unknown")
    min_float = skin.get("min_float", None)
    max_float = skin.get("max_float", None)
    # Collect all crate names this skin can drop from
    crates = [crate.get("name") for crate in skin.get("crates", [])]
    
    processed_skins.append({
        "name": name,
        "rarity": rarity,
        "weapon": weapon_name,
        "min_float": min_float,
        "max_float": max_float,
        "cases": crates
    })

# Save to new JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(processed_skins, f, indent=4)

print(f"Processed {len(processed_skins)} skins. Output saved to {OUTPUT_FILE}.")
input("Press Enter to exit...")
