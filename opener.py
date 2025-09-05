import random
import os
import json
import requests
import urllib.parse
import time
from colorama import Fore, Style, init

init(autoreset=True)

JSON_PATH = "processed_skins.json"

inventory = []
extraordinary_obtained = []
price_cache = {}

rarity_colors = {
    "Consumer": Fore.WHITE,
    "Industrial": Fore.LIGHTBLUE_EX,
    "Mil-Spec": Fore.BLUE,
    "Restricted": "\033[38;5;54m",
    "Classified": Fore.LIGHTMAGENTA_EX,
    "Covert": Fore.RED,
    "Extraordinary": Fore.YELLOW
}

rarity_odds = {
    "Mil-Spec": 0.79,
    "Restricted": 0.16,
    "Classified": 0.03,
    "Covert": 0.006,
    "Extraordinary": 0.004
}

fallback_prices = {
    "Mil-Spec": 1.0,
    "Restricted": 5.0,
    "Classified": 15.0,
    "Covert": 50.0,
    "Extraordinary": 200.0,
    "Knife": 250.0,
    "Rifle": 10.0,
    "Pistol": 5.0
}

condition_multiplier = {
    "Factory New": 2.0,
    "Minimal Wear": 1.5,
    "Field-Tested": 1.0,
    "Well-Worn": 0.8,
    "Battle-Scarred": 0.5
}

# Load skins
def load_skins(path):
    if not os.path.exists(path):
        print(Fore.RED + "ERROR: File not found.")
        exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Build cases dictionary
def build_cases(skins):
    cases = {}
    for s in skins:
        if "cases" in s and isinstance(s["cases"], list):
            for case_name in s["cases"]:
                if case_name.strip():
                    cases.setdefault(case_name.strip(), []).append(s)
    return cases

# Generate float if applicable
def givefloat(item):
    if "min_float" in item and item["min_float"] is not None:
        return round(random.uniform(item["min_float"], item["max_float"]), 5)
    return None

# Pick rarity based on odds
def pick_rarity():
    rand = random.random()
    cumulative = 0
    for rarity, chance in rarity_odds.items():
        cumulative += chance
        if rand <= cumulative:
            return rarity
    return "Mil-Spec"

# Determine condition from float
def get_condition(skin_float):
    if skin_float is None:
        return "Factory New"
    if 0.00 <= skin_float <= 0.07:
        return "Factory New"
    elif 0.07 < skin_float <= 0.15:
        return "Minimal Wear"
    elif 0.15 < skin_float <= 0.38:
        return "Field-Tested"
    elif 0.38 < skin_float <= 0.45:
        return "Well-Worn"
    else:
        return "Battle-Scarred"

# Fetch Steam market price with caching and delay
def get_market_price(skin_name, condition):
    key = f"{skin_name} ({condition})"
    if key in price_cache:
        return price_cache[key]

    encoded_name = urllib.parse.quote(key)
    url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={encoded_name}"

    try:
         # avoid rate limit
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        if data.get("success"):
            for k in ["lowest_price", "median_price"]:
                price = data.get(k)
                if price and price.strip() != "":
                    price = price.replace("$", "").replace(",", ".").strip()
                    price_float = round(float(price), 2)
                    price_cache[key] = price_float
                    return price_float

    except requests.exceptions.RequestException as e:
        print(f"Warning: {e}. Using fallback price.")

    return None

# Get final price with fallback
def get_skin_price(skin):
    market_price = get_market_price(skin["name"], skin["condition"])
    if market_price is not None:
        return market_price, "Steam market price"

    rarity = skin["rarity"].split()[0]
    base = fallback_prices.get(rarity, 1.0)
    mult = condition_multiplier.get(skin["condition"], 1.0)
    type_base = fallback_prices.get(skin.get("type", "Rifle"), 1.0)
    price = round(max(base, type_base) * mult, 2)

    reason = []
    if rarity in fallback_prices:
        reason.append(f"fallback by rarity ({rarity})")
    if skin.get("type") in fallback_prices:
        reason.append(f"fallback by type ({skin['type']})")
    if not reason:
        reason.append("unknown fallback")

    return price, ", ".join(reason)

# Fetch prices for all inventory at once
def fetch_all_inventory_prices():
    print("Fetching inventory prices...")
    for entry in inventory:
        if entry["price"] is None:
            entry["price"], entry["reason"] = get_skin_price(entry["skin"])

# --- Load data ---
skins = load_skins(JSON_PATH)
cases = build_cases(skins)

while True:
    print("Hoofd menu")
    print("1. Laat inventory zien")
    print("2. Kies Lootbox")
    print("3. Stats")

    try:
        keuze = int(input(" "))
    except ValueError:
        print("Ongeldige keuze, typ een nummer.")
        input("")
        os.system('cls')
        continue

    if keuze == 1:
        if not inventory:
            print("Je inventory is leeg.")
        else:
            fetch_all_inventory_prices()
            rarity_order = ["Consumer", "Industrial", "Mil-Spec", "Restricted", "Classified", "Covert", "Extraordinary"]
            sorted_inventory = sorted(
                inventory,
                key=lambda x: rarity_order.index(x["skin"]["rarity"].split()[0])
            )
            for entry in sorted_inventory:
                main_rarity = entry["skin"]["rarity"].split()[0]
                color = rarity_colors.get(main_rarity, Fore.WHITE)
                print(f"{color}{entry['skin']['name']}{Style.RESET_ALL} ({entry['condition']}, float: {entry['float']}) - Market: ${entry['price']} [{entry['reason']}]")
        input("leave: (enter)")
        os.system('cls')

    elif keuze == 2:
        os.system('cls')
        print("Kies een case:")
        case_names = list(cases.keys())
        if not case_names:
            print(Fore.RED + "Geen cases beschikbaar.")
            input("Press Enter om terug te gaan...")
            os.system('cls')
            continue

        for i, name in enumerate(case_names, start=1):
            print(f"{i}. {name}")

        try:
            choice = int(input("Maak een keuze: ")) - 1
            casepick = case_names[choice]
        except (ValueError, IndexError):
            print("Ongeldige keuze")
            input("Press enter to return...")
            os.system('cls')
            continue

        os.system('cls')
        while True:
            chosen_case_skins = cases[casepick]
            rarity = pick_rarity()
            available_skins = [i for i in chosen_case_skins if i["rarity"].startswith(rarity)]
            newitem = random.choice(available_skins or chosen_case_skins)

            qual = givefloat(newitem)
            float_display = qual if qual is not None else "N/A"
            cond = get_condition(qual)
            newitem["condition"] = cond

            inventory.append({
                "skin": newitem,
                "float": float_display,
                "condition": cond,
                "price": None,
                "reason": "not fetched"
            })

            if newitem["rarity"] == "Extraordinary":
                extraordinary_obtained.append(newitem["name"])

            main_rarity = newitem["rarity"].split()[0]
            color = rarity_colors.get(main_rarity, Fore.WHITE)
            print(f"Je hebt een lootbox geopend en kreeg {color}{newitem['name']}{Style.RESET_ALL} ({cond}, float: {float_display}) - Price will fetch on inventory open!")

            again = input("Wil je nog een case openen? (Enter = ja / 1 = nee): ")
            if again == "1":
                os.system('cls')
                break

    elif keuze == 3:
        print(f"Je hebt {len(inventory)} skins geopend.")
        if extraordinary_obtained:
            print(f"Extraordinary skins verkregen ({len(extraordinary_obtained)}):")
            for skin in extraordinary_obtained:
                print(f"- {skin}")
        input("leave: (enter)")
        os.system('cls')

    else:
        print("Ongeldige keuze, probeer opnieuw.")
        input("")
        os.system('cls')
