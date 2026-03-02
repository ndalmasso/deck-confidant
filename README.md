# Deck Confidant 🃏

> *"Greatness, at any cost."* — Dark Confidant

A Modern MTG deck builder powered by a real data engineering pipeline and machine learning. Give it your play style, budget, and format constraints — it builds you a 60-card deck and adapts it when you want to swap cards.

---

## What it does

- Ingests 21,000+ Modern-legal cards from Scryfall
- Scrapes real tournament decklists from MTGTop8
- Uses k-means clustering to discover archetypes from tournament data
- Matches your play style description to archetypes using NLP embeddings
- Assembles a 60-card deck within your budget
- Propagates card swap requests through the deck maintaining synergy and curve

---

## Stack

| Layer | Technology |
|---|---|
| Data storage | Databricks Delta Lake |
| Transformations | dbt Core |
| ML / NLP | scikit-learn, sentence-transformers |
| Frontend | Streamlit |
| Data sources | Scryfall API, MTGTop8 |

---

## Architecture
```
Scryfall API          →  raw_cards       →  stg_cards   →  dim_cards
MTGTop8 (scraper)     →  raw_decklists   →  stg_decklists  →  int_deck_vectors
                                                              ↓
                                                         k-means clustering
                                                              ↓
                                                         archetype model
                                                              ↓
                                                         deck recommender
```

---

## dbt Models

### Staging
- **stg_cards** — cleaned Modern-legal cards from Scryfall. One row per card.
- **stg_decklists** — cleaned tournament decklists from MTGTop8. One row per card per deck.

### Intermediate
- **int_deck_vectors** — deck-level feature vectors (avg CMC, creature count, colour distribution etc). Direct input to the clustering model.

### Marts
- **dim_cards** — enriched card dimension table with price tiers, colour labels, and mechanic flags (discard, counterspell, land destruction, graveyard hate).

---

## Data

| Table | Rows | Source |
|---|---|---|
| raw_cards | 21,739 | Scryfall bulk API |
| raw_decklists | ~5,000 | MTGTop8 scraper |
| dim_cards | 21,739 | dbt transform |
| int_deck_vectors | ~155 | dbt transform |

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
# Ingest data (run in Databricks notebook)
# See databricks/01_ingest_cards.py
# See databricks/02_ingest_decklists.py

# Run dbt models
cd dbt
dbt run
dbt test
dbt docs serve
```

---

## Project Status

- [x] Data ingestion pipeline
- [x] dbt staging models
- [x] dbt mart models  
- [x] dbt tests and documentation
- [ ] k-means clustering model
- [ ] NLP play style embeddings
- [ ] Deck recommender
- [ ] Card swap cascade engine
- [ ] Streamlit UI

---

## Format

Modern only (for now).
