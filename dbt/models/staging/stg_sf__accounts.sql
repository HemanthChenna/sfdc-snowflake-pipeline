{{ config(unique_key='account_id') }}
select
    payload:Id::string                     as account_id,
    payload:Name::string                   as account_name,
    payload:Industry::string               as industry,
    payload:AnnualRevenue::number(18,2)    as annual_revenue,
    payload:BillingCountry::string         as billing_country,
    payload:IsDeleted::boolean             as is_deleted,
    to_timestamp_tz(payload:SystemModstamp::string,
        'YYYY-MM-DD"T"HH24:MI:SS.FF3TZHTZM') as system_modstamp,
    _loaded_at
from {{ source('salesforce_raw', 'sf_account') }}
{% if is_incremental() %}
where _loaded_at > (select max(_loaded_at) from {{ this }})
{% endif %}
qualify row_number() over (
    partition by account_id
    order by system_modstamp desc, _loaded_at desc) = 1
