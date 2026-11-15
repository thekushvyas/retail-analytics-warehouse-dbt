-- Basket totals must reconcile exactly to the line-level fact table
select 1
from (select sum(basket_sales) s from {{ ref('fct_baskets') }}) b,
     (select sum(sales_value)  s from {{ ref('fct_sales') }})   l
where abs(b.s - l.s) > 0.01
