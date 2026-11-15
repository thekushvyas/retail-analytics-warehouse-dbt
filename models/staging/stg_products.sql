select
    product_id::varchar     as product_id,
    manufacturer_id::varchar as manufacturer_id,
    department,
    product_category,
    product_type,
    brand                   as brand_type,          -- National / Private
    package_size
from {{ source('raw', 'products') }}
