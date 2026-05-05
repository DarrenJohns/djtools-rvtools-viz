# 🔬 How It Works — RVTools Visualiser Under the Hood

> **A technical deep-dive into how every feature is built — one HTML file, two CDN libraries, pure vanilla JavaScript.**

---

## 📐 Architecture Overview

The entire app lives in a single `index.html` file with three embedded sections:

| Section | Purpose |
|---------|---------|
| `<style>` | CSS using custom properties for light/dark theming, responsive grid, connected-dots SVG background |
| `<body>` | Semantic HTML — hero, demo bar, drop zone, filters, sections, tables |
| `<script>` | Vanilla JavaScript — multi-tab parsing, charting, filtering, pagination, export |

**CDN dependencies:**
- **[Chart.js](https://www.chartjs.org/)** — every chart, including the Risk Quadrant scatter
- **[SheetJS](https://sheetjs.com/)** — `.xlsx` parsing

**Why single-file?** It deploys to any static host (Azure SWA, S3, GitHub Pages) with zero build step, and you can open `index.html` locally and it just works.

---

## 🎨 Theme System — Light & Dark

CSS custom properties + a `dark` class on `<body>`:

```css
:root {
  --primary: #0078D4;
  --bg: #F5F9FF;
  --card-bg: #FFFFFF;
  --text: #1A1A2E;
}

body.dark {
  --bg: #0D1117;
  --card-bg: #161B22;
  --text: #E6EDF3;
}
```

`toggleTheme()` flips the class and saves the choice to `localStorage`. On page load, the saved preference wins; otherwise we fall back to `prefers-color-scheme`.

**💡 Technique:** every colour in the app is `var(--token)`, so flipping one class re-themes the entire UI in one repaint.

### Connected-dots background

An inline SVG pattern of circles + lines, tinted with the brand palette and overlaid with a `radial-gradient`. `background-attachment: fixed` produces the parallax feel. Light and dark themes use different colour variants and opacity.

---

## 📂 File Import — Excel Parsing

### The drop zone

```js
dropZone.addEventListener('dragover',  e => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop',      e => { e.preventDefault(); dropZone.classList.remove('dragover'); if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]); });
```

We also `preventDefault()` `dragover`/`drop` on `document` so the browser doesn't try to render the file outside the zone if the user drops slightly off-target.

### SheetJS read

```js
function handleFile(file) {
  const reader = new FileReader();
  reader.onload = e => {
    const wb = XLSX.read(e.target.result, { type: 'array' });
    // ... locate vInfo, parse, fan out to optional tabs
  };
  reader.readAsArrayBuffer(file);
}
```

### Friendly errors

Instead of letting parser failures bubble up, we surface them via `showFileError(title, hint)`:
- File extension isn't `.xlsx` / `.xls`
- `XLSX.read` throws
- No `vInfo` sheet (we list the sheets we *did* find)
- vInfo sheet empty
- vInfo parses but no VM rows survive

---

## 🪜 Multi-tab Fan-out

After locating `vInfo`, the importer iterates a parser map for the optional tabs:

```js
const tabParsers = {
  vDatastore: parseDatastoreTab,
  vSnapshot:  parseSnapshotTab,
  vHost:      parseHostTab,
  vDisk:      parseDiskTab,
  vNetwork:   parseNetworkTab,
  vHealth:    parseHealthTab,
  vCluster:   parseClusterTab,
  vCPU:       parseCPUTab,
  vMemory:    parseMemoryTab,
};

for (const [tabName, parser] of Object.entries(tabParsers)) {
  const sn = wb.SheetNames.find(s => s.toLowerCase() === tabName.toLowerCase());
  if (sn) {
    allData[tabName] = parser(XLSX.utils.sheet_to_json(wb.Sheets[sn], { defval: '' }));
  }
}
```

Each parser returns a normalised array of objects. The render functions for each dashboard read from `allData[tabName]` and **silently skip themselves** if the tab is missing — that's why a vInfo-only file still works, just with fewer sections.

### Column mapping — legacy & modern

RVTools has changed column names across versions, so each parser tries modern names first and falls back:

```js
function parseRVToolsData(rows) {
  return rows.map(r => ({
    name:          r['VM']        || r['Name'],
    powerState:    r['Powerstate']|| r['Power state'],
    cpus:          parseInt(r['CPUs'] || r['Num CPUs']) || 0,
    memoryMB:      parseInt(r['Memory'] || r['Memory MB']) || 0,
    provisionedMB: parseFloat(r['Provisioned MB'] || r['Provisioned MiB']) || 0,
    os:            r['OS according to the VMware Tools'] || r['OS according to the configuration file'] || '',
    datacenter:    r['Datacenter'] || r['DC'] || '',
    // ...
  }));
}
```

---

## 🧮 Readiness Algorithm & Risk Scoring

### OS classification

Three helpers categorise each VM's OS:
- `isLegacyOS(os)` — Server 2008/2003/2000, XP, Vista, Win7, RHEL/CentOS 5–6
- `isOlderOS(os)` — Server 2012/R2, Ubuntu 14/16, RHEL/CentOS 7
- `isModernOS(os)` — Server 2016+, Ubuntu 18+, RHEL/CentOS 8+

### Wave assignment

```js
function getWave(vm) {
  if (!vm.powerState.match(/on/i)) return isLegacyOS(vm.os) ? 4 : 3;
  if (isLegacyOS(vm.os)) return 4;
  if (isOlderOS(vm.os))  return 2;
  if (isModernOS(vm.os)) return 1;
  return 3; // unknown OS treated cautiously
}
```

The wave number maps to one of four readiness labels:

| Wave | Label | Colour token |
|------|-------|--------------|
| 1 | 🟢 Ready Now | `--wave1` |
| 2 | 🟡 Light Prep | `--wave2` |
| 3 | 🟠 Modernise | `--wave3` |
| 4 | 🔴 Remediate | `--wave4` |

### Complexity & Impact

- **Complexity** — vCPU count, memory, provisioned storage, plus signals from OS, firmware (BIOS vs EFI), and hardware version
- **Impact** — disk + memory + CPU as a coarse business-impact proxy

These two scores place each VM on the Risk Quadrant scatter.

---

## 🎯 SKU Recommender

The SKU recommender is a self-contained module sitting alongside the readiness layer. It consumes the same `allVMs` array but renders into its own collapsible section.

**State.** Three top-level pieces — `skurPlan` (region/currency/term/headroom), `skurGroups` (sizing groups with mode + members + pinned flag), and `skurOutOfScope` (key → reason+note map). Tag rules and selection sit in their own collections. Every meaningful state change dispatches a `skurPlanChanged` event with `{detail:{field}}` — the data pill, group rail, recommendation grid, and live-data lazy-loader all subscribe and re-render.

**Live data loader.** `skurInitLiveData()` runs on `DOMContentLoaded` (and lazily on region change). It fetches `data/metadata.json` to discover available regions, then `data/<region>.json` (capability) + `data/<region>-pricing.json` (retail prices, keyed by *size* — `A1_v2`, not `Standard_A1_v2`). `_skurNormaliseLiveSkus()` filters to B/D/E/F families, drops region-restricted SKUs, infers processor family from the name suffix (`a` → AMD, `p` → ARM, else Intel), and joins capability + price into the `{name, family, vcpu, ramGb, hourlyUsd, …}` shape the ranker expects. On `file://` the loader silently no-ops (browsers block `fetch()` from local files); the recommender falls back to the 40-SKU seed catalog.

**Ranking.** `skurRankCandidates(vm, eligible, mode, plan)` maps every eligible SKU through `skurFitFor(vm, sku)` (returns `null` if the SKU can't fit the VM) and `skurScore<Mode>(fit, sku, plan)`:

- **Balanced** — distance from headroom target on both CPU and RAM, with a small cost tiebreaker.
- **Cost** — cheapest hourly rate that satisfies the minimum headroom floor.
- **Rightsized** — waste-normalised (waste / vm-size) on both axes with cost tiebreaker.

The top score wins; ranks 2–3 become alternates. Confidence is computed from min headroom + burstable family flag.

**Duplicate handling.** `parseRVToolsData()` deduplicates after mapping using a stable key — UUID first, then `name|cluster|dc` composite. First occurrence wins; the dropped count is exposed on `window.rvtoolsDupInfo` and surfaced in the file-load banner and the Excel Summary sheet.

**Exports.** CSV uses `_downloadCSV(prefix, headers, rows)` to emit a 21-column row per VM. Excel builds an `XLSX.utils.book_new()` workbook with Summary / All-recommendations / per-group / OOS / Plan sheets — sheet names sanitised to strip `: \ / ? * [ ]` and capped at 28 chars (Excel's 31-char limit minus a dedupe-suffix budget). All numeric cells stay numeric so Excel can chart them.

---

## 📊 Charts — Chart.js Integration

`renderCharts()` (and each per-section render function) creates Chart.js instances. Before re-creating a chart we destroy any existing instance on that canvas to avoid memory leaks during filter changes:

```js
if (charts['osDist']) charts['osDist'].destroy();
charts['osDist'] = new Chart(canvas, { type: 'doughnut', data, options });
```

The Risk Quadrant uses a `scatter` chart with one dataset per readiness group, coloured from the `--wave1..4` tokens.

The **Indicative Azure Family Fit** chart in Environment Topology buckets VMs into D-/E-/F-/M-series-style families based on their vCPU and memory profile, giving a coarse first-look at SKU shape.

---

## 🔍 Filtering — scoped to the Overview section

Four dropdowns inside the **Overview** section drive `applyFilters()`. A filter change rebuilds Overview's six metric cards, exec-summary text, and six analytics charts only. Wave Plan, Full Inventory, the Risk Quadrant, and every infrastructure dashboard always render against the full estate, so the filter bar can't accidentally hide infrastructure context:

```js
function applyFilters() {
  const dc    = document.getElementById('fDC').value;
  const os    = document.getElementById('fOS').value;
  const power = document.getElementById('fPower').value;
  const wave  = document.getElementById('fWave').value;

  filteredVMs = allVMs.filter(vm =>
    (!dc    || vm.dc === dc) &&
    (!os    || vm.osFamily === os) &&
    (!power || vm.power.includes(power === 'poweredOn' ? 'on' : 'off')) &&
    (!wave  || getWave(vm) === parseInt(wave))
  );

  renderSummary();   // Overview cards + exec text
  renderCharts();    // 6 analytics charts
  // Risk Quadrant, Wave table, Inventory table read from allVMs and are unaffected
}
```

---

## 📄 Pagination — One Helper, Ten Tables

All ten data tables share a single helper. State lives in a per-table object so each table paginates independently:

```js
const _tablePagState = {}; // { key: { page, rows, tbodyId } }
const PAGE_SIZE = 25;

function paginateTable(key, tbodyId, rowsHtml) {
  if (rowsHtml !== undefined) _tablePagState[key] = { page: 1, rows: rowsHtml, tbodyId };
  const st = _tablePagState[key];
  const tbody = document.getElementById(tbodyId);
  const totalPages = Math.max(1, Math.ceil(st.rows.length / PAGE_SIZE));
  st.page = Math.min(st.page, totalPages);
  const start = (st.page - 1) * PAGE_SIZE;
  tbody.innerHTML = st.rows.slice(start, start + PAGE_SIZE).join('');
  renderPagination(key, tbody, totalPages, st.page, st.rows.length);
}

function _gotoTablePage(key, p) {
  if (!_tablePagState[key]) return;
  _tablePagState[key].page = p;
  paginateTable(key, _tablePagState[key].tbodyId);
}
```

Each render function builds its rows array as HTML strings, then hands them to `paginateTable('host', 'hostTBody', rows)`. Re-rendering the whole table (e.g. after a filter change) resets to page 1.

**💡 Closure trap we hit and fixed:** `renderPagination` builds its prev/next buttons via `Function.prototype.toString()` — closures don't survive that, only globals resolve in the resulting `onclick` scope. We bake the table key in as a string literal:

```js
onclick="(${eval(`(p => _gotoTablePage(${JSON.stringify(key)}, p))`).toString()})(${i})"
```

That's why `_gotoTablePage` lives at the top level rather than inside the helper.

---

## 🧪 Demo Mode

State on first load:

```js
let allVMs   = [...SAMPLE_VMS];
let allData  = { vInfo: allVMs, ...SAMPLE_TABS };
```

A small `showDemoIndicators()` / `hideSampleIndicators()` pair toggles the demo bar, the drop-zone's `demo-active` class, and the reset button label.

`loadSampleData(mode)` swaps the dataset between `vinfo` (just `SAMPLE_VMS`) and `full` (`SAMPLE_VMS` + `SAMPLE_TABS`) so users can preview the difference between minimal and rich exports without leaving the demo.

When a real file lands successfully, `hideSampleIndicators()` runs: the demo bar disappears, and the drop-zone plus the *How to export from RVTools* helper panel are hidden so the imported state is unambiguous. A green confirmation card under the (now hidden) drop-zone surfaces the filename, VM count, and detected tabs. Two buttons appear below: **📥 Import another file** (re-opens the file picker) and **× Back to demo** (calls `clearLoadedData()`, restores demo state, and scrolls back to the upload section).

---

## 📤 Export System

### CSV

`exportCSV()` builds a CSV string with proper quoting (fields containing commas or quotes are wrapped + escaped) and triggers a download via a temporary `<a>` and `Blob` URL.

### "Save Locally" — offline HTML snapshot

`exportHTML()` produces a self-contained `.html` file:

1. Every Chart.js canvas is captured as a base64 PNG via `canvas.toDataURL()`
2. Summary cards and table rows are cloned (no pagination — every row is rendered)
3. The result is wrapped in a standalone HTML template with inline CSS and the amber **OFFLINE SNAPSHOT** banner
4. Footer carries the export timestamp

The snapshot has zero external dependencies — drop it on a USB stick, open it on a plane, it works.

---

## 🚀 Deployment

```
Push to main → GitHub Actions → SWA CLI deploy → Live at rvtoolsviz.djtools.co.nz
```

The deploy workflow:
1. Checks out the repo
2. Copies `index.html` to a `deploy-staging/` folder (required by the SWA CLI)
3. Runs `npx @azure/static-web-apps-cli deploy` with the deployment token
4. Verifies with an HTTP request to the custom domain

**💡 Why the staging folder?** The SWA CLI's underlying `StaticSitesClient.exe` fails when the artifact folder is the repo root. Copying to a subfolder first is the workaround.

### HTML validation workflow

A separate `validate.yml` runs on PRs:
- DOCTYPE presence + essential HTML tags
- Tag balance (with a threshold for JS template strings inside the HTML-export builder)
- Common smells (TODO comments, `console.log`)

`PYTHONUTF8: 1` is set for cross-platform runner compatibility.
