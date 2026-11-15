# %% [markdown]
# # Retail Analytics Warehouse — Metrics Report
#
# Reads the dbt marts built in `warehouse.duckdb` (run `python scripts/load_raw.py && dbt build --profiles-dir .` first)
# and reports weekly active households, basket economics, retention cohorts and data-quality results.

# %%
import duckdb, pandas as pd, numpy as np, matplotlib.pyplot as plt, pathlib, json
CH = pathlib.Path("charts"); CH.mkdir(exist_ok=True)
plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": .25, "font.size": 10})
BLUE, GREY, RED = "#2563eb", "#9ca3af", "#dc2626"
con = duckdb.connect("warehouse.duckdb", read_only=True)
con.sql("select schema_name, table_name, estimated_size as rows from duckdb_tables() where schema_name = 'main_marts' order by 2").df()

# %% [markdown]
# ## 1. Data-quality results (from `dbt build`)

# %%
rr = json.load(open("target/run_results.json"))
tests = pd.DataFrame([{"test": r["unique_id"].split(".")[2], "status": r["status"]} for r in rr["results"] if r["unique_id"].startswith("test.")])
print(f"{len(tests)} data tests: {tests.status.value_counts().to_dict()}")
unknown = int(con.sql("select count(*) n from main_marts.dim_product where is_unknown_member").df().n[0])
print(f"Orphan product_ids in transactions added as UNKNOWN dimension members: {unknown}")
tests

# %% [markdown]
# ## 2. Weekly KPIs

# %%
wk = con.sql("select * from main_marts.mart_weekly_kpis where week_start >= '2017-01-02' and week_start < '2017-12-25' order by 1").df()
fig, ax = plt.subplots(1, 3, figsize=(12, 3.3))
ax[0].plot(wk.week_start, wk.weekly_active_households, color=BLUE); ax[0].set_title("Weekly active households")
ax[1].plot(wk.week_start, wk.avg_basket_value, color=BLUE); ax[1].set_title("Average basket value ($)")
ax[2].plot(wk.week_start, wk.discount_rate * 100, color=BLUE); ax[2].set_title("Discount rate (% of shelf value)")
fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(CH / "01_weekly_kpis.png", bbox_inches="tight")
n_hh = int(con.sql("select count(*) n from main_marts.dim_household").df().n[0])
print(f"Avg weekly active households {wk.weekly_active_households.mean():.0f} of {n_hh:,} "
      f"({wk.weekly_active_households.mean()/n_hh:.0%}); avg basket ${wk.avg_basket_value.mean():.2f}; "
      f"discount rate {wk.discount_rate.mean():.1%}")
wk.describe().round(2)

# %% [markdown]
# ## 3. Household engagement: stickiness and shopping frequency

# %%
eng = con.sql("""
with w as (select household_id, count(distinct date_trunc('week', basket_date)) wks, count(*) baskets, sum(basket_sales) sales
           from main_marts.fct_baskets group by 1)
select count(*) households, avg(wks) avg_active_weeks, median(baskets) median_baskets,
       avg((wks >= 26)::int) share_active_26plus_weeks,
       sum(sales) filter (where sales >= (select quantile_cont(sales, .8) from w)) / sum(sales) top20_sales_share
from w""").df()
eng.round(3)

# %% [markdown]
# ## 4. Retention cohorts

# %%
coh = con.sql("select * from main_marts.mart_retention_cohorts where cohort_month < '2017-12-01' order by 1, 2").df()
piv = coh.pivot(index="cohort_month", columns="months_since_first", values="retention")
fig, ax = plt.subplots(figsize=(8, 3.6))
im = ax.imshow(piv.values * 100, cmap="Blues", vmin=0, vmax=100, aspect="auto")
ax.set_yticks(range(len(piv))); ax.set_yticklabels([f"{d:%b %Y} (n={int(n)})" for d, n in zip(piv.index, coh[coh.months_since_first == 0].active_households)], fontsize=8)
ax.set_xlabel("Months since first purchase"); ax.set_title("Household retention by first-purchase month (%)"); ax.grid(False)
for i in range(piv.shape[0]):
    for j in range(piv.shape[1]):
        v = piv.values[i, j]
        if not np.isnan(v): ax.text(j, i, f"{v*100:.0f}", ha="center", va="center", fontsize=7, color="white" if v > .6 else "black")
fig.colorbar(im, fraction=.03); fig.tight_layout(); fig.savefig(CH / "02_retention_cohorts.png", bbox_inches="tight")
jan = piv.iloc[0]
print(f"January cohort ({int(coh.iloc[0].active_households)} households): month-1 {jan[1]:.0%}, month-6 {jan[6]:.0%}, month-11 {jan[11]:.0%}")

# %% [markdown]
# ## 5. Campaign reach vs. spend (descriptive)

# %%
camp = con.sql("""
select h.campaigns_received >= 1 as got_campaign, count(*) households,
       avg(b.sales) avg_annual_sales, avg(b.baskets) avg_baskets
from main_marts.dim_household h
join (select household_id, sum(basket_sales) sales, count(*) baskets from main_marts.fct_baskets group by 1) b using (household_id)
group by 1 order by 1""").df()
camp.round(1)

# %% [markdown]
# Campaign recipients spend more, but campaigns were targeted at engaged households, so this is **not** a causal effect —
# a holdout design (see the email-lift project) is needed to measure incrementality.
