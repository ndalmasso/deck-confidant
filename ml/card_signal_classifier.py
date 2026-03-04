"""
Card signal classifier.
Learns macro labels (Aggro/Control/Combo) from MTGTop8 labeled decklists.
Each card gets a dominant macro label and confidence score based on
how often it appears in each category across tournament data.
Run the corresponding Databricks notebook (02b_archetype_classifier) to
rebuild the card_signals Delta table.
"""

from collections import defaultdict
import pandas as pd


def build_card_signals(df_labeled: pd.DataFrame, lands: set, min_appearances: int = 3) -> pd.DataFrame:
    """
    Build card -> macro label signal table from labeled decklists.
    
    Args:
        df_labeled: DataFrame with columns deck_id, card_name, quantity, macro_label
        lands: set of land card names to exclude (lowercase)
        min_appearances: minimum times a card must appear to be included
    
    Returns:
        DataFrame with card_name, dominant_macro, confidence, total_appearances
    """
    df_nonland = df_labeled[~df_labeled["card_name"].str.lower().isin(lands)].copy()

    card_macro_counts = defaultdict(lambda: defaultdict(int))
    for _, row in df_nonland.iterrows():
        card_macro_counts[row["card_name"]][row["macro_label"]] += row["quantity"]

    card_signals = []
    for card, counts in card_macro_counts.items():
        total = sum(counts.values())
        dominant = max(counts, key=counts.get)
        confidence = counts[dominant] / total
        card_signals.append({
            "card_name": card,
            "dominant_macro": dominant,
            "confidence": round(confidence, 3),
            "total_appearances": total,
            "aggro_count": counts.get("Aggro", 0),
            "control_count": counts.get("Control", 0),
            "combo_count": counts.get("Combo", 0),
        })

    df_signals = pd.DataFrame(card_signals)
    df_signals = df_signals[df_signals["total_appearances"] >= min_appearances]
    df_signals = df_signals.sort_values("confidence", ascending=False)
    return df_signals


def classify_deck(card_list: list, df_signals: pd.DataFrame, min_confidence: float = 0.6):
    """
    Classify a deck into Aggro/Control/Combo using learned card signals.

    Args:
        card_list: list of (card_name, quantity) tuples
        df_signals: card signal table from build_card_signals
        min_confidence: minimum card confidence to use as signal

    Returns:
        (dominant_macro, score_percentages, evidence_cards)
    """
    scores = defaultdict(float)
    evidence = defaultdict(list)

    for card_name, quantity in card_list:
        match = df_signals[df_signals["card_name"].str.lower() == card_name.lower()]
        if match.empty:
            continue
        row = match.iloc[0]
        if row["confidence"] >= min_confidence:
            weight = row["confidence"] * quantity
            scores[row["dominant_macro"]] += weight
            evidence[row["dominant_macro"]].append(
                f"{card_name} (conf={row['confidence']:.2f})"
            )

    if not scores:
        return "Unknown", {}, []

    dominant = max(scores, key=scores.get)
    total = sum(scores.values())
    pct = {k: round(v / total * 100, 1) for k, v in scores.items()}
    return dominant, pct, evidence[dominant]
