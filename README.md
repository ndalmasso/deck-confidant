# Deck Confidant 🃏
> *"Greatness, at any cost."* — Dark Confidant

A Modern MTG deck builder powered by a real data engineering pipeline and machine learning. Give it your play style, budget, and format constraints — it builds you a 75-card deck and adapts it when you want to swap cards.

---

## What it does

- Ingests all Modern-legal cards from Scryfall, refreshed automatically when the ban list changes
- Scrapes real tournament decklists from MTGTop8 and MTGDecks.net
- Detects meta staleness and re-scrapes the last 3 weeks of tournaments on demand
- Uses k-means clustering to discover archetypes from tournament data (no hardcoded lists)
- Matches your play style description to archetypes using NLP embeddings
- Assembles a 75-card deck within your budget
- Propagates card swap requests through the deck maintaining synergy and curve

---

## Stack

| Layer | Technology |
|---|---|
| Data storage | Databricks Delta Lake |
| Transformations | dbt Core |
| ML / NLP | scikit-learn, sentence-transformers |
| Frontend | Streamlit |
| Data sources | Scryfall API, MTGTop8, MTGDecks.net |

---

## Architecture
```
Scryfall API        →  raw_cards      →  stg_cards      →  dim_cards
MTGTop8             →  raw_decklists  →  stg_decklists  →  int_deck_vectors
MTGDecks.net        ↗                                           ↓
                                                        k-means clustering
                                                               ↓
                                                       archetype embeddings
                                                               ↓
                                                        NLP prompt matcher
                                                               ↓
                                                       deck recommender (WIP)
```

---

## dbt Models

### Staging
- **stg_cards** — cleaned Modern-legal cards from Scryfall. One row per card.
- **stg_decklists** — cleaned tournament decklists. One row per card per deck.

### Intermediate
- **int_deck_vectors** — deck-level feature vectors (avg CMC, creature count, colour distribution etc). Direct input to the clustering model.

### Marts
- **dim_cards** — enriched card dimension table with price tiers, colour labels, and mechanic flags (discard, counterspell, land destruction, graveyard hate).

---

## Data

| Table | Source |
|---|---|
| raw_cards | Scryfall bulk API |
| raw_decklists | MTGTop8 + MTGDecks.net scrapers |
| dim_cards | dbt transform |
| int_deck_vectors | dbt transform |
| deck_clusters | k-means clustering (10 archetypes, silhouette 0.503) |
| archetype_embeddings | sentence-transformers all-MiniLM-L6-v2 |

---

## Setup

### Prerequisites
- Python 3.11+
- Databricks account (Community Edition works)
- dbt Core

### Install
```bash
git clone https://github.com/ndalmasso/deck-confidant.git
cd deck-confidant
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Configure dbt
```bash
cp .dbt/profiles.example.yml ~/.dbt/profiles.yml
# edit profiles.yml with your Databricks credentials
```

### Run the pipeline
```bash
# Ingest data (run notebooks in Databricks)
# 01_ingest_cards
# 02_ingest_decklists
# 03_clustering
# 04_embeddings

# Run dbt models
cd dbt
dbt run
dbt test
dbt docs serve
```

---

## Project Status

- [x] Data ingestion pipeline from Scryfall, MTGTop8, MTGDecks.net
- [x] dbt staging models
- [x] dbt mart models
- [x] dbt tests and documentation
- [x] k-means clustering model (10 archetypes discovered from tournament data)
- [x] NLP play style embeddings via sentence-transformers
- [x] Pipeline controller with staleness detection and ban list checking
- [ ] Deck recommender
- [ ] Card swap cascade engine
- [ ] Streamlit UI

---

## Format

Modern only. 60 card mainboard + 15 card sideboard.
