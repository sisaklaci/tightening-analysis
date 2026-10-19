# Tightening Analysis — Databricks + VS Code + GitHub

Spec-kit style project developed locally in VS Code, version-controlled on GitHub,
and executed on Databricks against the Lakehouse Federation view
`snowflake_db_sl_ee_lab.sl_mfg.tightening_zg_view`.

## Workflow

```
VS Code (edit) → GitHub (version) → Databricks Git Folder (run)
```

1. Edit Python/MD files locally in VS Code.
2. `git push` to GitHub.
3. Pull into the Databricks Git Folder (or push directly from VS Code via the
   Databricks extension) and run on a cluster.
4. Edits made inside Databricks can be committed back to GitHub from the Git dialog there.
5. For scheduled/production runs, a Lakeflow Job (`tightening_analysis_job`, defined in
   [databricks.yml](databricks.yml)) sources `tightening_analysis.py` directly from the
   GitHub repo on a daily schedule — no manual sync needed. See "Deploy the scheduled job"
   below.

## One-time setup

### 1. VS Code — Databricks extension
- Extensions (`Ctrl+Shift+X`) → search **Databricks** → install the one published by Databricks.
- Restart VS Code if prompted.

### 2. Workspace connection
- Databricks icon in the sidebar → **Create configuration**.
- Host: `https://adb-5678659344564033.13.azuredatabricks.net`
- Auth method: Azure CLI (if `az login` is already set up), a Personal Access Token
  (User Settings → Developer → Access Tokens in the Databricks UI), or OAuth (U2M, browser login).

### 3. Compute
- Pick an existing **all-purpose cluster** (DBR 13.3 LTS+, Standard/Dedicated access mode).
- Serverless compute does **not** work with "Upload and Run File" — needs a classic cluster.

### 4. Link GitHub to Databricks
- Databricks → User Settings → **Linked Accounts** → add GitHub credentials (PAT or OAuth).
  Required before Databricks can pull/push this repo.

### 5. Create the Databricks Git Folder
- Databricks UI → Workspace → your folder → **Create → Git folder**
- Git repository URL: `<this repo's GitHub URL>`
- Provider: GitHub, folder name e.g. `tightening-analysis`

## Daily use

- Run a file from VS Code: right-click `tightening_analysis.py` → **Run on Databricks →
  Upload and Run File** (output in the Debug Console).
- Or open the file inside the Databricks Git Folder, attach to the cluster, run cells.
- For production/scheduled runs: create a **Lakeflow Job** with Source = Git provider,
  pointing at this repo + branch + file path — Databricks pulls the latest commit each run.

## Deploy the scheduled job

The job itself is defined as code in [databricks.yml](databricks.yml) (`resources.jobs.tightening_analysis_job`) —
runs daily at 06:00 Europe/Budapest on a dedicated job cluster, pulling `tightening_analysis.py`
straight from the `master` branch on GitHub.

The workspace does not allow unrestricted cluster creation — every cluster must reference an
admin-approved cluster policy. Compute is pinned to **"Datalab 03 Job Cluster Single Node"**
(looked up by name via the `gpu_job_policy_id` bundle variable), the only policy that allows a
GPU node for Jobs compute: `Standard_NC4as_T4_v3` (1x NVIDIA T4), `15.4.x-gpu-ml-scala2.12`,
single-node (`num_workers: 0`, driver only). The policy rejects autoscaling and instance-pool
settings, so the job cluster definition in `databricks.yml` intentionally has neither.

To create/update it in the workspace:

- **From VS Code** (no CLI needed): Databricks icon in the sidebar → **Deploy** (or run the
  "Databricks: Deploy Bundle" command). This applies whatever is in `databricks.yml` to the
  `dev` target.
- **From a terminal with the Databricks CLI installed and configured**: `databricks bundle deploy -t dev`.

After deploying, the job appears under **Workflows** in the Databricks UI as
`tightening-analysis-daily`, already active on its schedule. To change the schedule, cluster
size, or runtime version, edit the `resources.jobs` block in `databricks.yml` and redeploy —
don't edit the job directly in the UI, since the next bundle deploy would overwrite UI changes.

## Source table — `tightening_zg_view`

| Column | Type | Description |
|---|---|---|
| ALPHACODE | string | Engine code |
| ENGINEID | string | Engine identifier |
| FINALANGLE | decimal(38,16) | Final angle value |
| FINALTORQUE | decimal(38,17) | Final torque value |
| GRAPHANGLEHEX | string | Graph angle values (hex) |
| GRAPHTORQUEHEX | string | Graph torque values (hex) |
| PLANTID | string | Plant identifier |
| PROGRAMID | decimal(38,0) | Program identifier |
| PROGRAMNAME | string | Program name |
| PROGRAMORIGINALVERSION | decimal(38,0) | Original program version |
| RESULTDATETIME | timestamp | Date/time of the result |
| RESULTID | decimal(38,0) | Unique result identifier |
| RESULTSTATUSID | decimal(38,0) | Result status identifier |
| RESULTSTATUSNAME | string | Result status name (e.g. OK) |
| SAMPLING | decimal(38,2) | Sampling data |
| TIGHTENING | string | Tightening data |
| UNITID | decimal(38,0) | Unit identifier |
| UNITNAME | string | Unit name |
| UNITPROGRAMORIGINALPLANTID | string | Unit program original plant ID |

No Snowflake credentials are needed locally — Lakehouse Federation handles the connection
on the cluster side. Always filter on `RESULTDATETIME` (and other columns) early, since
queries are federated live to Snowflake.
