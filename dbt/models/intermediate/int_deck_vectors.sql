-- int_deck_vectors: one row per deck, aggregated card quantities
-- this is the input format needed for k-means clustering

with decklists as (
    select * from {{ ref('stg_decklists') }}
),

-- join to dim_cards to only keep Modern-legal cards we know about
cards as (
    select * from {{ ref('dim_cards') }}
),

joined as (
    select
        d.deck_id,
        d.archetype_clean                as archetype,
        d.card_name,
        d.quantity,
        c.card_category,
        c.cmc,
        c.colors
    from decklists d
    inner join cards c on lower(d.card_name) = lower(c.name)
),

-- deck-level aggregates (used as features for clustering)
deck_features as (
    select
        deck_id,
        archetype,
        COUNT(distinct card_name)        as unique_cards,
        SUM(quantity)                    as total_cards,
        AVG(cmc)                         as avg_cmc,
        MAX(cmc)                         as max_cmc,
        SUM(case when card_category = 'Creature' then quantity else 0 end)    as creature_count,
        SUM(case when card_category = 'Instant' then quantity else 0 end)     as instant_count,
        SUM(case when card_category = 'Sorcery' then quantity else 0 end)     as sorcery_count,
        SUM(case when card_category = 'Land' then quantity else 0 end)        as land_count,
        SUM(case when card_category = 'Artifact' then quantity else 0 end)    as artifact_count,
        SUM(case when card_category = 'Enchantment' then quantity else 0 end) as enchantment_count,
        SUM(case when colors like '%R%' then quantity else 0 end)             as red_cards,
        SUM(case when colors like '%U%' then quantity else 0 end)             as blue_cards,
        SUM(case when colors like '%B%' then quantity else 0 end)             as black_cards,
        SUM(case when colors like '%G%' then quantity else 0 end)             as green_cards,
        SUM(case when colors like '%W%' then quantity else 0 end)             as white_cards
    from joined
    group by deck_id, archetype
)

select * from deck_features
