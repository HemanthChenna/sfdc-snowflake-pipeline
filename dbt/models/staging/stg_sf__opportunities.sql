{{ config(unique_key='opportunity_id') }}
select
    payload:Id::string                     as opportunity_id,
    payload:AccountId::string              as account_id,
    payload:Name::string                   as opportunity_name,
    payload:StageName::string              as stage_name,
    payload:Amount::number(18,2)           as amount,
    payload:CloseDate::date                as close_date,
    payload:IsClosed::boolean              as is_closed,
    payload:IsWon::boolean                 as is_won,
    payload:IsDeleted::boolean             as is_deleted,
    to_timestamp_tz(payload:SystemModstamp::string,
        'YYYY-MM-DD"T"HH24:MI:SS.FF3TZHTZM') as system_modstamp,
    _loaded_at
from {{ source('salesforce_raw', 'sf_opportunity') }}
{% if is_incremental() %}
where _loaded_at > (select max(_loaded_at) from {{ this }})
{% endif %}
qualify row_number() over (
    partition by opportunity_id
    order by system_modstamp desc, _loaded_at desc) = 1
