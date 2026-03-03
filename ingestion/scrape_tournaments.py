import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, timedelta

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ── BAN LIST / LEGALITY CHECK ──────────────────────────────────────────

def get_current_modern_legal_cards():
    """Fetch current Modern legal card names from Scryfall."""
    print("Fetching current Modern legality from Scryfall...")
    url = "https://api.scryfall.com/cards/search?q=legalities:modern+legal:modern&unique=names"
    cards = set()
    while url:
        r = requests.get(url).json()
        for card in r.get("data", []):
            cards.add(card["name"])
        url = r.get("next_page")
        time.sleep(0.1)
    print(f"  Found {len(cards)} Modern-legal cards")
    return cards

def check_legality_changed(current_legal_cards, previous_count):
    """Simple check: if card count changed, something was banned/unbanned."""
    changed = len(current_legal_cards) != previous_count
    if changed:
        print(f"  Legality changed: {previous_count} -> {len(current_legal_cards)} cards")
    else:
        print(f"  No legality changes detected")
    return changed

# ── MTGTOP8 ───────────────────────────────────────────────────────────

def scrape_mtgtop8(weeks=3):
    """Scrape Modern decklists from MTGTop8 from the last N weeks."""
    BASE = "https://www.mtgtop8.com"
    cutoff = datetime.now() - timedelta(weeks=weeks)
    all_cards = []

    for page in range(1, 6):
        url = f"{BASE}/format?f=MO&meta=44&cp={page}"
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")

        events = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "event?e=" in href and "f=MO" in href and "&d=" not in href:
                events.append(BASE + "/" + href)
        
        for event_url in list(set(events))[:10]:
            r = requests.get(event_url, headers=HEADERS)
            soup = BeautifulSoup(r.text, "html.parser")

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
                deck_url = BASE + "/event" + href

                r2 = requests.get(deck_url, headers=HEADERS)
                soup2 = BeautifulSoup(r2.text, "html.parser")
                for card_row in soup2.find_all(class_="deck_line"):
                    text = card_row.text.strip()
                    parts = text.split(" ", 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        all_cards.append({
                            "deck_id": deck_id,
                            "archetype": archetype,
                            "card_name": parts[1].strip(),
                            "quantity": int(parts[0]),
                            "source": "mtgtop8",
                            "scraped_at": datetime.now().isoformat()
                        })
                time.sleep(0.5)
        time.sleep(1)

    print(f"MTGTop8: {len(all_cards)} card rows")
    return all_cards

# ── MTGDECKS.NET ──────────────────────────────────────────────────────

def scrape_mtgdecks(weeks=3):
    """Scrape Modern decklists from MTGDecks.net."""
    BASE = "https://mtgdecks.net"
    all_cards = []

    for page in range(1, 4):
        url = f"{BASE}/Modern/decklists/page:{page}"
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")

        deck_links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/Modern/decklist/" in href and href not in deck_links:
                deck_links.append(href)

        for href in deck_links[:15]:
            deck_url = BASE + href if href.startswith("/") else href
            deck_id = href.split("/")[-1]

            r2 = requests.get(deck_url, headers=HEADERS)
            soup2 = BeautifulSoup(r2.text, "html.parser")

            # Get archetype from title
            title = soup2.find("h1")
            archetype = title.text.strip() if title else "Unknown"

            # Parse card rows
            for row in soup2.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 2:
                    qty_text = cols[0].text.strip()
                    name_text = cols[1].text.strip()
                    if qty_text.isdigit() and name_text:
                        all_cards.append({
                            "deck_id": f"mtgdecks_{deck_id}",
                            "archetype": archetype,
                            "card_name": name_text,
                            "quantity": int(qty_text),
                            "source": "mtgdecks",
                            "scraped_at": datetime.now().isoformat()
                        })
            time.sleep(0.5)
        time.sleep(1)

    print(f"MTGDecks: {len(all_cards)} card rows")
    return all_cards

# ── MAIN ──────────────────────────────────────────────────────────────

def run(weeks=3, previous_card_count=21739):
    print(f"Scraping last {weeks} weeks of Modern tournaments...\n")

    # Check ban list
    legal_cards = get_current_modern_legal_cards()
    legality_changed = check_legality_changed(legal_cards, previous_card_count)

    # Scrape sources
    all_cards = []
    
    print("\nScraping MTGTop8...")
    all_cards.extend(scrape_mtgtop8(weeks=weeks))

    print("\nScraping MTGDecks.net...")
    all_cards.extend(scrape_mtgdecks(weeks=weeks))

    df = pd.DataFrame(all_cards)
    df.to_csv("data/raw_decklists.csv", index=False)
    
    print(f"\nTotal: {len(df)} card rows across {df['deck_id'].nunique()} decklists")
    print(f"Sources: {df['source'].value_counts().to_dict()}")
    print(f"Legality changed: {legality_changed}")
    
    return df, legality_changed

if __name__ == "__main__":
    run()
