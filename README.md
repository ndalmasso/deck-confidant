# Deck Confidant 🃏
> *"Greatness, at any cost."* — Dark Confidant

A Modern MTG deck builder powered by a real data engineering pipeline and machine learning. Give it your play style, budget, and format constraints — it builds you a 75-card deck and adapts it when you want to swap cards.

---

## What it does

- Ingests all Modern-legal cards from Scryfall, refreshed automatically when the ban list changes
- Scrapes real tournament decklists from MTGTop8 and MTGDecks.net
- Detects meta staleness and re-scrapes the last 3 weeks of tournaments on demand
- Learns macro play style categories (Aggro, Control, Combo, Midrange) from labeled tournament data using a card signal classifier
- Uses hierarchical k-means clustering to discover archetypes within each category — no hardcoded lists
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
Scryfall API        →  raw_cards           →  stg_cards      →  dim_cards
MTGTop8             →  raw_decklists        →  stg_decklists  →  int_deck_vectors
MTGDecks.net        ↗  labeled_decklists                            ↓
                       card_signals                         hierarchical clustering
                       archetype_macro_map                         ↓
                                                            deck_clusters
                                                                   ↓
                                                         archetype_embeddings
                                                                   ↓
                                                          NLP prompt matcher
                                                                   ↓
                                                         deck recommender (WIP)
```

---

## How the classification works

Rather than hardcoding a list of archetypes, the system learns them from data in two stages.

**Stage 1 — Card signal classifier.** MTGTop8 labels every deck as Aggro, Control, or Combo. We scrape 774 labeled decklists and learn which non-land cards are statistically associated with each macro category. Ragavan and Ocelot Pride signal Aggro. Counterspell and Terminus signal Control. Amulet of Vigor and Goryo's Vengeance signal Combo. Any new deck can be classified by looking at which cards it contains and scoring against these learned signals.

**Stage 2 — Hierarchical k-means clustering.** Within each macro category, k-means clusters decks by their feature vectors (CMC, creature count, colour distribution, spell mix). This surfaces specific archetypes automatically — Dimir Control separates from UW Control, Tron separates from Permission, Death and Taxes separates from Boros Energy. The optimal number of clusters is chosen by silhouette score.

The result is 8 categories with named clusters inside each:

| Category | Example clusters |
|---|---|
| Aggro | Boros Aggro, Manufacturing Affinity |
| Combo | Ruby Storm, Amulet Titan, Living End, Instant Reanimator |
| Control - Big Mana | UrzaTron, Eldrazi Ramp |
| Control - Permission | Dimir Control, Scepter Chant |
| Midrange - Taxes | Death And Taxes, Esper Taxes |
| Midrange - Domain | 4/5c Aggro, Domain Zoo |
| Midrange - Black Grind | Dimir Frog, Necrodominance |
| Control - Prison | Lantern Control |

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

| Table | Description |
|---|---|
| raw_cards | All Modern-legal cards from Scryfall bulk API |
| raw_decklists | Tournament decklists from MTGTop8 and MTGDecks.net |
| labeled_decklists | 774 decklists with Aggro/Control/Combo macro labels from MTGTop8 |
| card_signals | 505 cards with learned macro label associations and confidence scores |
| archetype_macro_map | Archetype to macro label mapping |
| dim_cards | Enriched card dimension table |
| int_deck_vectors | Deck-level feature vectors |
| deck_clusters | 353 decks clustered into 8 macro categories and named archetypes |
| archetype_embeddings | NLP embeddings for each archetype cluster profile |

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
# Run notebooks in Databricks in order:
# 01_ingest_cards
# 02_ingest_decklists
# 02b_archetype_classifier
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
- [x] dbt staging, intermediate, and mart models
- [x] dbt tests and documentation
- [x] Card signal classifier — learns macro labels from 774 labeled tournament decklists
- [x] Hierarchical k-means clustering — 8 macro categories, archetypes discovered within each
- [x] NLP play style matching via sentence-transformer embeddings
- [x] Pipeline controller with staleness detection and ban list checking
- [ ] Deck construction engine (budget filter, card selection, curve validation)
- [ ] Card swap cascade engine
- [ ] Streamlit UI

---

## Format

Modern only. 60 card mainboard + 15 card sideboard.
