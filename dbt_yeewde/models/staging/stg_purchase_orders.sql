with source as (
    select * from {{ source('bronze', 'purchase_orders') }}
),

renamed as (
    select
        trim(po_id) as po_id,
        trim(supplier_id) as supplier_id,
        trim(site_id) as site_id,
        trim(part_id) as part_id,
        try_cast(order_date as date) as order_date,
        try_cast(promised_date as date) as promised_date,
        try_cast(receipt_date as date) as receipt_date,
        cast(ordered_qty as bigint) as ordered_qty,
        cast(received_qty as bigint) as received_qty,

        -- Indicateurs de livraison
        receipt_date is not null as is_delivered,

        -- Retard en jours (positif = retard, négatif/zéro = en avance ou à l'heure)
        case
            when receipt_date is not null then date_diff('day', try_cast(promised_date as date), try_cast(receipt_date as date))
            else null
        end as delay_days,

        -- On-Time (respect du délai promis)
        case
            when receipt_date is null then null
            when try_cast(receipt_date as date) <= try_cast(promised_date as date) then true
            else false
        end as is_on_time,

        -- In-Full (quantité livrée conforme)
        case
            when receipt_date is null then null
            when cast(received_qty as bigint) >= cast(ordered_qty as bigint) then true
            else false
        end as is_in_full,

        -- OTIF (On-Time ET In-Full)
        case
            when receipt_date is null then null
            when try_cast(receipt_date as date) <= try_cast(promised_date as date)
                 and cast(received_qty as bigint) >= cast(ordered_qty as bigint) then true
            else false
        end as is_otif,

        -- Taux de complétion
        case
            when ordered_qty > 0 then round(cast(received_qty as double) / cast(ordered_qty as double), 4)
            else 1.0
        end as fill_rate

    from source
)

select * from renamed
