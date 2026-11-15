select
    c.household_id::varchar  as household_id,
    c.campaign_id::varchar   as campaign_id,
    d.campaign_type,
    d.start_date::date       as start_date,
    d.end_date::date         as end_date
from {{ source('raw', 'campaigns') }} c
join {{ source('raw', 'campaign_descriptions') }} d using (campaign_id)
