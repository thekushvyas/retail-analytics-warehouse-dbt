-- Weekly business KPIs: active households, baskets, sales, basket size, discount rate
select d.week_start,
       count(distinct b.household_id)                 as weekly_active_households,
       count(*)                                       as baskets,
       sum(b.basket_sales)                            as sales,
       sum(b.basket_sales) / count(*)                 as avg_basket_value,
       sum(b.basket_discount) / nullif(sum(b.basket_sales + b.basket_discount), 0) as discount_rate
from {{ ref('fct_baskets') }} b
join {{ ref('dim_date') }} d on d.date_day = b.basket_date
group by 1
