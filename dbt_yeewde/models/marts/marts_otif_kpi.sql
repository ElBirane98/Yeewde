with po as (
    select * from {{ ref('stg_purchase_orders') }}
),

parts as (
    select * from {{ ref('stg_parts_master') }}
),

joined as (
    select
        -- Identifiants
        po.po_id,
        po.supplier_id,
        po.site_id,
        po.part_id,

        -- Dates
        po.order_date,
        po.promised_date,
        po.receipt_date,

        -- Délais
        parts.lead_time_days as standard_lead_time_days,
        case
            when po.receipt_date is not null then date_diff('day', po.order_date, po.receipt_date)
            else null
        end as actual_lead_time_days,

        case
            when po.receipt_date is not null then date_diff('day', po.order_date, po.receipt_date) - parts.lead_time_days
            else null
        end as lead_time_variance_days,

        po.delay_days,

        -- Quantités et montants
        po.ordered_qty,
        po.received_qty,
        po.fill_rate,
        parts.unit_cost,
        round(po.ordered_qty * parts.unit_cost, 2) as total_order_cost,

        -- Caractéristiques de la pièce & Fournisseur
        parts.part_family,
        parts.criticality_class,
        parts.supplier_risk_class,
        parts.is_repairable,
        parts.shelf_life_days,

        -- Indicateurs OTIF
        po.is_delivered,
        po.is_on_time,
        po.is_in_full,
        po.is_otif,
        case
            when po.is_otif is true then 1.0
            when po.is_otif is false then 0.0
            else null
        end as otif_score

    from po
    left join parts on po.part_id = parts.part_id
)

select * from joined
