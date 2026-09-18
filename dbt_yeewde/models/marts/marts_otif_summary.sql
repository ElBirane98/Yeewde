-- Modèle Gold : synthèse OTIF segmentée
-- Agrège le KPI OTIF par fournisseur, famille de pièce et classe de criticité

with base as (

    select * from {{ ref('marts_otif_kpi') }}
    where is_otif is not null  -- uniquement les commandes déjà livrées

),

by_supplier as (

    select
        'supplier' as segment_type,
        supplier_id as segment_value,
        count(*) as total_orders,
        sum(case when is_otif then 1 else 0 end) as otif_orders,
        round(100.0 * sum(case when is_otif then 1 else 0 end) / count(*), 2) as otif_rate_pct,
        round(avg(delay_days), 1) as avg_delay_days,
        round(avg(fill_rate), 3) as avg_fill_rate

    from base
    group by supplier_id

),

by_part_family as (

    select
        'part_family' as segment_type,
        part_family as segment_value,
        count(*) as total_orders,
        sum(case when is_otif then 1 else 0 end) as otif_orders,
        round(100.0 * sum(case when is_otif then 1 else 0 end) / count(*), 2) as otif_rate_pct,
        round(avg(delay_days), 1) as avg_delay_days,
        round(avg(fill_rate), 3) as avg_fill_rate

    from base
    group by part_family

),

by_criticality as (

    select
        'criticality_class' as segment_type,
        criticality_class as segment_value,
        count(*) as total_orders,
        sum(case when is_otif then 1 else 0 end) as otif_orders,
        round(100.0 * sum(case when is_otif then 1 else 0 end) / count(*), 2) as otif_rate_pct,
        round(avg(delay_days), 1) as avg_delay_days,
        round(avg(fill_rate), 3) as avg_fill_rate

    from base
    group by criticality_class

),

unioned as (

    select * from by_supplier
    union all
    select * from by_part_family
    union all
    select * from by_criticality

)

select * from unioned
order by segment_type, otif_rate_pct asc