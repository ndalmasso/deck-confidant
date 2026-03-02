-- dim_cards: final card dimension table
-- clean, enriched, ready for the recommender and budget filter

with stg as (
    select * from {{ ref('stg_cards') }}
)

select
    name,
    mana_cost,
    cmc,
    type_line,
    card_category,
    oracle_text,
    colors,
    keywords,
    power,
    toughness,
    price_usd,

    -- budget tiers
    case
        when price_usd is null    then 'unknown'
        when price_usd < 1        then 'budget'
        when price_usd < 5        then 'mid'
        when price_usd < 20       then 'expensive'
        else 'staple'
    end as price_tier,

    -- colour identity tags
    case
        when colors = ''          then 'Colorless'
        when colors like '%,%'    then 'Multicolor'
        when colors = 'W'         then 'White'
        when colors = 'U'         then 'Blue'
        when colors = 'B'         then 'Black'
        when colors = 'R'         then 'Red'
        when colors = 'G'         then 'Green'
        else 'Other'
    end as color_label,

    -- mechanic flags inherited from staging
    has_discard,
    has_counterspell,
    has_land_destruction,
    has_graveyard_hate

from stg
