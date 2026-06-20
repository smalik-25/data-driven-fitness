-- silver_dexa grain must be unique on (scan_date, region). Returns offending rows.
select scan_date, region, count(*) as n
from {{ ref('silver_dexa') }}
group by scan_date, region
having count(*) > 1
