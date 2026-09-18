with source as (
    select * from {{ source('bronze', 'parts_master') }}
),

renamed as (
    select
        trim(part_id) as part_id,
        trim(part_family) as part_family,
        trim(criticality_class) as criticality_class,
        cast(unit_cost as double) as unit_cost,
        cast(lead_time_days as integer) as lead_time_days,
        trim(supplier_id_primary) as supplier_id_primary,
        trim(supplier_risk_class) as supplier_risk_class,
        case when lower(trim(is_repairable)) in ('yes', 'true', '1') then true else false end as is_repairable,
        cast(shelf_life_days as double) as shelf_life_days
    from source
)

select * from renamed
