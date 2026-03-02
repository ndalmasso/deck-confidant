-- stg_decklists: cleaned tournament decklist data
-- one row per card per deck

with source as (
    select * from {{ source('deck_confidant', 'raw_decklists') }}
),

cleaned as (
    select
        cast(deck_id as string)          as deck_id,
        trim(archetype)                  as archetype,
        trim(card_name)                  as card_name,
        cast(quantity as int)            as quantity,

        -- normalise unknown archetypes
        case
            when trim(archetype) = 'Unknown' then null
            else trim(archetype)
        end                              as archetype_clean

    from source
    where card_name is not null
      and quantity > 0
)

select * from cleaned
