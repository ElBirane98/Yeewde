# Dictionnaire des données ERP (Bronze)

## parts_master
Référentiel pièces : `part_id`, `part_family`, `criticality_class`, `unit_cost`, `lead_time_days`, `supplier_id_primary`, `supplier_risk_class`, `is_repairable`, `shelf_life_days`.

## purchase_orders
Commandes : `po_id`, `supplier_id`, `site_id`, `part_id`, `order_date`, `promised_date`, `receipt_date`, `ordered_qty`, `received_qty`. Base du calcul OTIF.

## quality_incidents
Incidents qualité (contexte RAG) : `incident_id`, `incident_date`, `part_id`, `supplier_id`, `site_id`, `defect_severity`, `defect_type`, `scrap_qty`.

## supply_chain_history
Historique stocks/consommations : `date`, `site_id`, `part_id`, `planned_maintenance`, `consumption_qty`, `on_hand_qty`, `backorder_qty`, `blocked_qty`, `forecast_qty`, `forecast_type`, `forecast_uplift_pct`.

Clés de jointure : `part_id`, `supplier_id`, `site_id`, `po_id` (commandes).
