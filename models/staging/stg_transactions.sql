-- One row per basket line. Cleans types, flags fuel/kiosk lines and derives prices.
select
    basket_id::varchar                        as basket_id,
    household_id::varchar                     as household_id,
    store_id::varchar                         as store_id,
    product_id::varchar                       as product_id,
    cast(transaction_timestamp as timestamp)  as transaction_ts,
    cast(transaction_timestamp as date)       as transaction_date,
    week                                      as week_no,
    quantity,
    sales_value,
    retail_disc,
    coupon_disc,
    coupon_match_disc,
    sales_value + retail_disc                 as shelf_value,
    quantity > 100                            as is_bulk_or_fuel_line
from {{ source('raw', 'transactions') }}
where quantity > 0
