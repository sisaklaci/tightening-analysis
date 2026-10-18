# spark is pre-configured when this runs on a Databricks cluster — no setup needed.

df = spark.table("snowflake_db_sl_ee_lab.sl_mfg.tightening_zg_view")

df_filtered = df.filter(
    (df.PLANTID == "SG") &
    (df.RESULTDATETIME >= "2026-01-01")
)

print(f"Row count: {df_filtered.count()}")
df_filtered.select("ENGINEID", "FINALTORQUE", "FINALANGLE", "RESULTSTATUSNAME").show(10)
