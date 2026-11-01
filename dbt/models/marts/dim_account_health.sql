select
    a.account_id,
    a.account_name,
    a.industry,
    count(o.opportunity_id)                                   as total_opportunities,
    sum(case when o.is_won then o.amount else 0 end)          as won_amount,
    sum(case when not o.is_closed then o.amount else 0 end)   as open_amount
from {{ ref('stg_sf__accounts') }} a
left join {{ ref('stg_sf__opportunities') }} o
       on o.account_id = a.account_id and not o.is_deleted
where not a.is_deleted
group by 1, 2, 3
