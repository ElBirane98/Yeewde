with source as (
    select * from {{ source('bronze', 'quality_incidents') }}
),

renamed as (
    select
        trim(incident_id) as incident_id,
        try_cast(incident_date as date) as incident_date,
        trim(part_id) as part_id,
        trim(supplier_id) as supplier_id,
        trim(site_id) as site_id,
        trim(defect_severity) as defect_severity,
        trim(defect_type) as defect_type,
        cast(scrap_qty as bigint) as scrap_qty
    from source
)

select * from renamed
