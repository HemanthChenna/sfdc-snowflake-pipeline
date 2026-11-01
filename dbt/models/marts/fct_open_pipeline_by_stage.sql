select
    o.stage_name,
    count(*)                       as open_opportunities,
    sum(coalesce(o.amount, 0))     as total_open_amount
from {{ ref('stg_sf__opportunities') }} o
where not o.is_closed
  and not o.is_deleted
group by o.stage_name
