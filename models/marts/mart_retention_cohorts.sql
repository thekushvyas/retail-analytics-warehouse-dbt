-- Monthly cohorts (first purchase month) and share still shopping n months later
with hh_month as (
    select distinct household_id, date_trunc('month', basket_date) as activity_month
    from {{ ref('fct_baskets') }}
    where basket_date < date '2018-01-01'      -- drop the partial final month (data ends 1 Jan 2018)
), firsts as (
    select household_id, min(activity_month) as cohort_month from hh_month group by 1
)
select f.cohort_month,
       datediff('month', f.cohort_month, a.activity_month)         as months_since_first,
       count(distinct a.household_id)                              as active_households,
       count(distinct a.household_id) * 1.0
         / max(count(distinct a.household_id)) over (partition by f.cohort_month) as retention
from hh_month a join firsts f using (household_id)
group by 1, 2
