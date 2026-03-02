-- stg_cards: clean and standardise raw card data
-- one row per Modern-legal card, nulls handled, types cast correctly

with source as (
    select * from {{ source('deck_confidant', 'raw_cards') }}
),

cleaned as (
    select
        name,
        mana_cost,
        cast(cmc as int)                          as cmc,
        type_line,
        oracle_text,
        colors,
        keywords,
        power,
        toughness,
        cast(price_usd as double)                 as price_usd,

        -- derived fields
        case
            when type_line like '%Creature%'   then 'Creature'
            when type_line like '%Instant%'    then 'Instant'
            when type_line like '%Sorcery%'    then 'Sorcery'
            when type_line like '%Enchantment%' then 'Enchantment'
            when type_line like '%Artifact%'   then 'Artifact'
            when type_line like '%Land%'       then 'Land'
            when type_line like '%Planeswalker%' then 'Planeswalker'
            else 'Other'
        end                                       as card_category,

        -- mechanic flags (used later for hate target matching)
        case when lower(oracle_text) like '%discard%' then true else false end as has_discard,
        case when lower(oracle_text) like '%counter target%' then true else false end as has_counterspell,
        case when lower(oracle_text) like '%destroy target land%' then true else false end as has_land_destruction,
        case when lower(oracle_text) like '%exile%graveyard%' then true else false end as has_graveyard_hate

    from source
    where name is not null
)

select * from cleaned
