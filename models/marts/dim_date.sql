-- Calendar dimension covering the transaction period
with bounds as (select min(transaction_date) d0, max(transaction_date) d1 from {{ ref('stg_transactions') }})
select
    cast(d as date)                         as date_day,
    cast(date_trunc('week', d) as date)     as week_start,
    cast(date_trunc('month', d) as date)    as month_start,
    dayname(d)                              as day_name,
    isodow(d) in (6, 7)                     as is_weekend
from bounds, range(d0, d1 + interval 1 day, interval 1 day) t(d)
