import json
import pandas as pd

# Load raw MTGJSON atomic cards
with open("data/AtomicCards.json") as f:
    raw = json.load(f)

cards = []
for card_name, printings in raw["data"].items():
    card = printings[0]  # take first printing
    legalities = card.get("legalities", {})
    
    # Only keep Modern-legal cards
    if legalities.get("modern") != "Legal":
        continue

    cards.append({
        "name": card_name,
        "mana_cost": card.get("manaCost", ""),
        "cmc": card.get("manaValue", 0),
        "type_line": card.get("type", ""),
        "oracle_text": card.get("text", ""),
        "colors": ",".join(card.get("colors", [])),
        "color_identity": ",".join(card.get("colorIdentity", [])),
        "keywords": ",".join(card.get("keywords", [])),
        "power": card.get("power", ""),
        "toughness": card.get("toughness", ""),
    })

df = pd.DataFrame(cards)
df.to_csv("data/modern_cards.csv", index=False)
print(f"Saved {len(df)} Modern-legal cards")
