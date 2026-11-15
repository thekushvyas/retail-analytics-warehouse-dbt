-- Product dimension. 3 product_ids in transactions (32 basket lines) are missing from the raw product master;
-- they are added as 'UNKNOWN' members so facts never drop rows (found by the relationships test).
select product_id, manufacturer_id, department, product_category, product_type, brand_type, package_size,
       false as is_unknown_member
from {{ ref('stg_products') }}
union all
select distinct t.product_id, null, 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', null, null, true
from {{ ref('stg_transactions') }} t
where not exists (select 1 from {{ ref('stg_products') }} p where p.product_id = t.product_id)
