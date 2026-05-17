# Data pipeline — Azure SKU/pricing/retirement refresh

## Purpose
Provide the SKU recommender with up-to-date Azure data (regions, VM SKUs, disk SKUs, pricing, retirements) without runtime dependency on any other app.

## Pattern
Same proven pattern as `djtools-azure-vm-sku-locator-PUBLIC` (the VM SKU app), embedded here for independence. **Schema drift between the two apps is the main risk** — see *Drift management* below.

## Inputs
- `config.json` at repo root — defines `targetRegions` to fetch each month.

## Outputs (under `data/`)
| File | Source | Refresh |
|---|---|---|
| `regions.json` | `az account list-locations` (all physical regions) | monthly |
| `metadata.json` | generated | monthly |
| `retirements.json` | scraped from Azure docs (`scripts/update-retirements.py`) | monthly |
| `<region>.json` | `az vm list-skus --resource-type virtualMachines --all` → `scripts/normalize-skus.py` | monthly |
| `<region>-pricing.json` | retail prices API (USD) → `scripts/fetch-pricing.py` | monthly |
| `<region>-pricing-<cur>.json` | retail prices API in each of 16 non-USD currencies (AUD, BRL, CAD, CHF, CNY, DKK, EUR, GBP, INR, JPY, KRW, NOK, NZD, RUB, SEK, TWD) → `scripts/fetch-pricing.py <region> <out> <CUR>` | monthly |
| `<region>-disks.json` | `az vm list-skus --resource-type disks --all` → `scripts/normalize-disks.py` | monthly |
| `history/<region>-YYYY-MM.json` | previous-month archive of `<region>.json` | monthly |

## Workflow
`.github/workflows/refresh-azure-data.yml`
- Schedule: `0 1 1 * *` (1st of month at 01:00 UTC — 1 hour after VM SKU app to reduce overlap)
- Manual: `workflow_dispatch`
- Runner: `ubuntu-latest`
- Auth: OIDC via `AZURE_CLIENT_ID` / `AZURE_TENANT_ID` / `AZURE_SUBSCRIPTION_ID` secrets
- Deploy: only when run on `main` (gated `if: github.ref == 'refs/heads/main'`); SWA token in `SWA_DEPLOYMENT_TOKEN`
- Commit: pushes data updates back to the branch the workflow ran on

## Adding/removing regions
Edit `config.json`'s `targetRegions` array; commit; trigger `workflow_dispatch` to backfill, or wait for the next scheduled run.

## Service principal
A **dedicated** SP for this repo is recommended (least-privilege blast radius, easier to rotate). Required role: `Reader` on the target subscription is sufficient for `az vm list-skus` and `az account list-locations`. Federated credentials should restrict to this repo + branch refs.

## Drift management
The normalizer scripts (`normalize-skus.py`, `normalize-disks.py`, `fetch-pricing.py`, `update-retirements.py`) are forked from the VM SKU app. **If either app evolves the normalised JSON schema, the other should follow within one cycle.** Key fields the recommender depends on:
- `name`, `family`, `vCPUs`, `memoryGB`, `cpuArchitecture`
- `acceleratedNetworking`, `premiumIO`, `ephemeralOSDisk`, `spotEligible`
- pricing: `payg`, `ri1y`, `ri3y` (in the requested currency — USD by default, or whichever of the 17 supported currencies was passed via `currencyCode`)
- disks: `name`, `sizeGB`, `iops`, `throughputMBps`, `tier`
- retirements: `family`, `retirementDate`, `replacement`

If the VM SKU app ships a normaliser change, port it here; bump the data schema version (TBD) so the UI can detect mismatches.

## Smoke test
1. Configure secrets (see *Service principal* above) and `SWA_DEPLOYMENT_TOKEN`.
2. Trigger `Refresh Azure Data` via Actions → Run workflow on the feature branch.
3. Verify `data/` populates with: `regions.json`, `metadata.json`, `retirements.json`, plus `<region>.json` / `<region>-pricing.json` / `<region>-pricing-<cur>.json` (×16 non-USD currencies) / `<region>-disks.json` for each entry in `config.json`.
4. Confirm a commit lands on the branch.
5. (Once on main) Confirm the SWA serves `/data/<region>.json`.

## Cost note
This workflow makes ~3 `az vm list-skus` calls per region per month plus one `az account list-locations` and **17 retail-pricing fetches per region** (one per supported currency: USD plus AUD, BRL, CAD, CHF, CNY, DKK, EUR, GBP, INR, JPY, KRW, NOK, NZD, RUB, SEK, TWD). The retail prices API is unauthenticated and free; total wall-clock for 2 dev regions is roughly 20–30 minutes per scheduled run. Azure read fees: zero.

## Multi-currency fan-out
The pipeline writes one pricing JSON per region per currency: USD lands at `<region>-pricing.json` (backward-compatible filename), all other currencies land at `<region>-pricing-<lowercur>.json`. The client lazily fetches the file matching the user's currency selection and caches the result per region per currency. Adding a region to `config.json` automatically picks up all 17 currencies on the next run; the stale-region cleanup step also sweeps any orphaned `<region>-pricing-*.json` files when a region is removed.
