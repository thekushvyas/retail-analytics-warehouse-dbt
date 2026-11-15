-- Demographics exist for only part of the panel; households seen in transactions are kept in dim_household.
select
    household_id::varchar as household_id,
    age, income, home_ownership, marital_status, household_size, household_comp, kids_count
from {{ source('raw', 'demographics') }}
