"""Script temporaire pour explorer marts_otif_summary."""
import duckdb
import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

con = duckdb.connect("data/yeewde.duckdb")

print("\n=== 5 pires fournisseurs (OTIF le plus bas) ===")
print(con.sql("""
    SELECT * FROM gold.marts_otif_summary
    WHERE segment_type = 'supplier'
    ORDER BY otif_rate_pct ASC
    LIMIT 5
""").fetchdf())

print("\n=== OTIF par classe de criticité ===")
print(con.sql("""
    SELECT * FROM gold.marts_otif_summary
    WHERE segment_type = 'criticality_class'
    ORDER BY otif_rate_pct ASC
""").fetchdf())

print("\n=== OTIF par famille de pièce ===")
print(con.sql("""
    SELECT * FROM gold.marts_otif_summary
    WHERE segment_type = 'part_family'
    ORDER BY otif_rate_pct ASC
""").fetchdf())
print("\n=== 10 pires fournisseurs (vue complète avec incidents qualité) ===")
print(con.sql("""
    SELECT supplier_id, supplier_risk_class, total_orders, otif_rate,
           avg_delay_days, max_delay_days, total_incidents, critical_incidents
    FROM gold.marts_supplier_kpi
    ORDER BY otif_rate ASC
    LIMIT 10
""").fetchdf())