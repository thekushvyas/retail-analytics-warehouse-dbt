"""Load dunnhumby 'The Complete Journey' tables into a local DuckDB file (schema: raw)."""
import duckdb, completejourney_py as cj

TABLES = ["transactions", "products", "demographics", "campaigns", "campaign_descriptions", "coupon_redemptions"]

def main(path="warehouse.duckdb"):
    con = duckdb.connect(path)
    con.execute("create schema if not exists raw")
    for name, df in cj.get_data(TABLES).items():
        con.register("df", df)
        con.execute(f"create or replace table raw.{name} as select * from df")
        print(f"raw.{name}: {len(df):,} rows")
    con.close()

if __name__ == "__main__":
    main()
