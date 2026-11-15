-- Grain: one row per basket
select basket_id, household_id, store_id,
       min(transaction_date)        as basket_date,
       count(*)                     as lines,
       sum(quantity) filter (where not is_bulk_or_fuel_line) as units,
       sum(sales_value)             as basket_sales,
       sum(total_discount)          as basket_discount
from {{ ref('fct_sales') }}
group by 1, 2, 3
