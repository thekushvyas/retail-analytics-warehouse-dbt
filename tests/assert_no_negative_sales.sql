select * from {{ ref('fct_sales') }} where sales_value < 0 or shelf_value < sales_value - 0.001
