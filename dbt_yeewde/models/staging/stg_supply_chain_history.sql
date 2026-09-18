with source as (
    select * from {{ source('bronze', 'supply_chain_history') }}
),

renamed as (
    select
        try_cast(date as date) as snapshot_date,
        trim(site_id) as site_id,
        trim(part_id) as part_id,
        coalesce(planned_maintenance, false) as planned_maintenance,
        cast(consumption_qty as bigint) as consumption_qty,
        cast(on_hand_qty as bigint) as on_hand_qty,
        cast(backorder_qty as bigint) as backorder_qty,
        cast(blocked_qty as bigint) as blocked_qty,
        cast(forecast_qty as bigint) as forecast_qty,
        trim(forecast_type) as forecast_type,
        cast(forecast_uplift_pct as double) as forecast_uplift_pct
    from source
)

select * from renamed
