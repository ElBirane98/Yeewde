select po_id
from {{ ref('marts_otif_kpi') }}
where otif_score is not null
  and (otif_score < 0 or otif_score > 1)
