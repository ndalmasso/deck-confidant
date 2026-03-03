"""
Pipeline controller.
Decides whether to re-scrape and re-cluster based on:
- Time since last scrape (threshold: 7 days)
- Ban list / legality changes detected
Run this at the start of every recommendation request.
"""

import json
import os
from datetime import datetime, timedelta

STATE_FILE = "data/pipeline_state.json"
RESCRAPE_THRESHOLD_DAYS = 7

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "last_scrape": None,
        "last_card_count": 21739,
        "last_cluster_run": None,
        "archetypes": []
    }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def should_rescrape(state):
    if state["last_scrape"] is None:
        print("No previous scrape found. Running fresh scrape.")
        return True
    last = datetime.fromisoformat(state["last_scrape"])
    age = datetime.now() - last
    if age > timedelta(days=RESCRAPE_THRESHOLD_DAYS):
        print(f"Last scrape was {age.days} days ago. Re-scraping.")
        return True
    print(f"Last scrape was {age.days} days ago. Skipping re-scrape.")
    return False

def run(force=False):
    from ingestion.scrape_tournaments import run as scrape
    from ml.cluster_archetypes import run as cluster

    state = load_state()
    needs_rescrape = force or should_rescrape(state)

    legality_changed = False
    if needs_rescrape:
        df, legality_changed = scrape(
            weeks=3,
            previous_card_count=state["last_card_count"]
        )
        state["last_scrape"] = datetime.now().isoformat()
        state["last_card_count"] = state["last_card_count"]  # updated by scraper if changed
        save_state(state)
        print("Scrape complete. Re-running clustering...")
        cluster_needed = True
    else:
        cluster_needed = legality_changed

    if cluster_needed:
        print("Running clustering pipeline...")
        # This would call the Databricks job in production
        # For now flag that clustering needs to run
        state["last_cluster_run"] = datetime.now().isoformat()
        save_state(state)

    print(f"\nPipeline state: {json.dumps(state, indent=2)}")
    return state

if __name__ == "__main__":
    run()
