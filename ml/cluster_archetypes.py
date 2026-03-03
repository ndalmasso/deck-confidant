"""
Archetype clustering model.
Reads int_deck_vectors from Databricks, fits k-means, saves deck_clusters table.
Run this inside a Databricks notebook - paste contents into a cell.
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

FEATURE_COLS = [
    'avg_cmc', 'max_cmc',
    'creature_count', 'instant_count', 'sorcery_count',
    'land_count', 'artifact_count', 'enchantment_count',
    'red_cards', 'blue_cards', 'black_cards', 'green_cards', 'white_cards'
]

CLUSTER_NAMES = {
    0: 'Tron / Big Mana',
    1: 'White Aggro',
    2: 'Green Combo',
    3: 'Cascade Combo',
    4: 'Blue Black Control',
    5: 'Affinity',
    6: 'UR Prowess',
    7: 'Landless Belcher',
    8: 'Storm',
    9: 'Black Midrange'
}

K = 10

def run(spark):
    df = spark.sql("SELECT * FROM workspace.deck_confidant.int_deck_vectors").toPandas()
    df_clean = df.dropna(subset=FEATURE_COLS).copy()
    print(f"Clustering {len(df_clean)} decks into {K} archetypes")

    scaler = StandardScaler()
    X = scaler.fit_transform(df_clean[FEATURE_COLS])

    km = KMeans(n_clusters=K, random_state=42, n_init=10)
    df_clean['cluster'] = km.fit_predict(X)
    df_clean['cluster_name'] = df_clean['cluster'].map(CLUSTER_NAMES)

    score = silhouette_score(X, df_clean['cluster'])
    print(f"Silhouette score: {score:.3f}")

    spark.createDataFrame(df_clean).write \
        .mode("overwrite") \
        .saveAsTable("workspace.deck_confidant.deck_clusters")

    print("Saved to workspace.deck_confidant.deck_clusters")
    return df_clean, km, scaler
