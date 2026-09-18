with otif as (
    select * from {{ ref('marts_otif_kpi') }}
),

incidents as (
    select
        supplier_id,
        count(incident_id) as total_incidents,
        sum(scrap_qty) as total_scrap_qty,
        count(case when defect_severity = 'Critical' then 1 end) as critical_incidents
    from {{ ref('stg_quality_incidents') }}
    group by supplier_id
),

supplier_stats as (
    select
        supplier_id,
        max(supplier_risk_class) as supplier_risk_class,
        count(po_id) as total_orders,
        count(case when is_delivered then 1 end) as delivered_orders,
        count(case when not is_delivered then 1 end) as pending_orders,

        -- Agrégations OTIF
        count(case when is_on_time then 1 end) as on_time_orders,
        count(case when is_in_full then 1 end) as in_full_orders,
        count(case when is_otif then 1 end) as otif_orders,

        -- Taux
        round(count(case when is_on_time then 1 end) * 1.0 / nullif(count(case when is_delivered then 1 end), 0), 4) as on_time_rate,
        round(count(case when is_in_full then 1 end) * 1.0 / nullif(count(case when is_delivered then 1 end), 0), 4) as in_full_rate,
        round(count(case when is_otif then 1 end) * 1.0 / nullif(count(case when is_delivered then 1 end), 0), 4) as otif_rate,

        -- Retard moyen
        round(avg(delay_days), 2) as avg_delay_days,
        max(delay_days) as max_delay_days,

        -- Dépenses
        round(sum(total_order_cost), 2) as total_ordered_spend

    from otif
    group by supplier_id
),

final as (
    select
        s.supplier_id,
        s.supplier_risk_class,
        s.total_orders,
        s.delivered_orders,
        s.pending_orders,
        s.on_time_orders,
        s.in_full_orders,
        s.otif_orders,
        s.on_time_rate,
        s.in_full_rate,
        s.otif_rate,
        s.avg_delay_days,
        s.max_delay_days,
        s.total_ordered_spend,
        coalesce(i.total_incidents, 0) as total_incidents,
        coalesce(i.critical_incidents, 0) as critical_incidents,
        coalesce(i.total_scrap_qty, 0) as total_scrap_qty

    from supplier_stats s
    left join incidents i on s.supplier_id = i.supplier_id
)

select * from final
order by total_orders desc
