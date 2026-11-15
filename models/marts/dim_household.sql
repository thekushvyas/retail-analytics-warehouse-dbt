-- Every household that ever shopped, enriched with demographics where available
with seen as (
    select household_id, min(transaction_date) first_purchase_date, max(transaction_date) last_purchase_date
    from {{ ref('stg_transactions') }} group by 1
), camp as (
    select household_id, count(distinct campaign_id) campaigns_received
    from {{ ref('stg_campaign_exposure') }} group by 1
)
select s.household_id, s.first_purchase_date, s.last_purchase_date,
       coalesce(c.campaigns_received, 0) as campaigns_received,
       h.age, h.income, h.household_size, h.kids_count,
       h.household_id is not null as has_demographics
from seen s
left join {{ ref('stg_households') }} h using (household_id)
left join camp c using (household_id)
