import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://www.mtgtop8.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_modern_events(pages=3):
    events = []
    for page in range(1, pages + 1):
        url = f"{BASE_URL}/format?f=MO&meta=44&cp={page}"
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "event?e=" in href and "f=MO" in href and "&d=" not in href:
                # href already looks like "event?e=12345&f=MO"
                full_url = BASE_URL + "/" + href
                events.append(full_url)
        time.sleep(1)
    return list(set(events))

def get_deck_links_from_event(event_url):
    r = requests.get(event_url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    decks = []
    for row in soup.find_all(class_=["hover_tr", "chosen_tr"]):
        link = row.find("a", href=True)
        if not link:
            continue
        href = link["href"]
        if "&d=" not in href:
            continue
        deck_id = href.split("&d=")[-1].split("&")[0]
        s14s = row.find_all(class_="S14")
        archetype = s14s[1].text.strip() if len(s14s) > 1 else "Unknown"
        # href looks like "?e=12345&d=67890&f=MO"
        deck_url = BASE_URL + "/event" + href
        decks.append({
            "deck_id": deck_id,
            "archetype": archetype,
            "url": deck_url
        })
    return decks

def parse_decklist(deck_info):
    r = requests.get(deck_info["url"], headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    cards = []
    for row in soup.find_all(class_="deck_line"):
        text = row.text.strip()
        parts = text.split(" ", 1)
        if len(parts) == 2 and parts[0].isdigit():
            cards.append({
                "deck_id": deck_info["deck_id"],
                "archetype": deck_info["archetype"],
                "card_name": parts[1].strip(),
                "quantity": int(parts[0])
            })
    return cards

def main():
    print("Fetching Modern events...")
    events = get_modern_events(pages=3)
    print(f"Found {len(events)} events")

    all_cards = []
    deck_count = 0

    for i, event_url in enumerate(events[:20]):
        print(f"Event {i+1}/20: {event_url}")
        deck_links = get_deck_links_from_event(event_url)
        print(f"  Found {len(deck_links)} decks")
        for deck_info in deck_links[:8]:
            cards = parse_decklist(deck_info)
            if cards:
                all_cards.extend(cards)
                deck_count += 1
                print(f"    Parsed deck {deck_info['deck_id']} ({deck_info['archetype']}): {len(cards)} cards")
            time.sleep(0.5)

    if not all_cards:
        print("No cards found - check scraper")
        return

    df = pd.DataFrame(all_cards)
    df.to_csv("data/raw_decklists.csv", index=False)
    print(f"\nDone: {len(df)} card rows across {deck_count} decklists")
    print(df["archetype"].value_counts().head(10))

if __name__ == "__main__":
    main()
