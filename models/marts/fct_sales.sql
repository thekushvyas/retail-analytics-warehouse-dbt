-- Grain: one row per basket line (household x basket x product)
select
    t.basket_id, t.household_id, t.store_id, t.product_id, t.transaction_date, t.transaction_ts,
    t.quantity, t.sales_value, t.shelf_value,
    t.retail_disc + t.coupon_disc + t.coupon_match_disc as total_discount,
    t.is_bulk_or_fuel_line
from {{ ref('stg_transactions') }} t
