# 🖥️ RVTools Visualiser

<div align="center">
  <img src="djtools.png" alt="RVTools Visualiser" width="700">
</div>

> **Built by a tech veteran with 30+ years of solution design expertise who has never been a professional coder — this app was vibe-crafted using [GitHub Copilot CLI](https://github.com/features/copilot/cli/) and deployed to [Azure Static Web Apps](https://azure.microsoft.com/products/app-service/static). From idea 💡 to production web app, without writing a single line of code manually.**
>
> **Drop in your RVTools `.xlsx` export and instantly turn it into a live VMware estate dashboard — executive summary, infrastructure deep-dives, and a migration-readiness view, all in your browser. No server, no upload, no install.**

[![Deploy](https://github.com/DarrenJohns/djtools-rvtools-viz/actions/workflows/deploy.yml/badge.svg)](https://github.com/DarrenJohns/djtools-rvtools-viz/actions/workflows/deploy.yml)
![Azure](https://img.shields.io/badge/Azure-SWA-0078D4)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Built with](https://img.shields.io/badge/built_with-Copilot_CLI-8957e5)
![Hosted on](https://img.shields.io/badge/hosted_on-Azure_SWA-0078D4)

👉 **Try the live app → [rvtoolsviz.djtools.co.nz](https://rvtoolsviz.djtools.co.nz/)**

📂 **Sample file to test with → [`test-samples/rvtools-sample.xlsx`](test-samples/rvtools-sample.xlsx)** — a multi-tab RVTools export

---

## ⭐ Why You'll Like It

- **🔒 Private by design** — every byte is parsed in your browser. Nothing is uploaded, nothing leaves your machine. Run it offline if you want.
- **⚡ Zero install** — single `index.html`, two CDN libraries (Chart.js + SheetJS). Open it locally, host it anywhere.
- **🎯 Useful in 30 seconds** — drag your `.xlsx` in and you'll have charts, dashboards, and migration recommendations before you can grab a coffee.
- **🧪 Built-in demo mode** — never seen RVTools before? The app boots with a synthetic dataset so you can try every feature without any data of your own.
- **📤 Take it offline** — export a self-contained HTML snapshot that works anywhere, with all charts baked in as images.

---

## ✨ What You Can Do

### 📂 Import your RVTools export

| Feature | What it does |
|---------|-------------|
| **Drag & drop or browse** | Drop a `.xlsx` export onto the upload zone (or click to pick a file) |
| **Multi-tab parsing** | Reads vInfo, vDatastore, vSnapshot, vHost, vDisk, vNetwork, vHealth, vCluster, vCPU, vMemory — every tab unlocks more dashboards |
| **Legacy + modern columns** | Auto-detects column names across RVTools versions (e.g. `Memory MB` vs `Memory`, `Num CPUs` vs `CPUs`) |
| **Helpful errors** | If your file isn't an RVTools export, you'll get a friendly message that tells you what's wrong, not a stack trace |
| **vInfo-only fallback** | Only have a single tab? You still get the core dashboards — extra tabs simply unlock more depth |

### 🧪 Try before you import

| Feature | What it does |
|---------|-------------|
| **Demo Mode on first load** | App boots with a synthetic ~30-VM dataset across multiple datacenters |
| **vInfo Only / Full Export toggle** | Switch demo mode between minimal (vInfo) and rich (full multi-tab) datasets to see the difference your file will make |
| **Sample download** | One-click download of a realistic sample `.xlsx` directly from the drop zone |
| **Back to demo** | Imported a file? Click *Back to demo* to wipe state and explore with sample data again |
| **Import another file** | Already loaded a file? Swap to a different one without first reverting to demo |

### 📊 Executive summary & analytics

| Feature | What it does |
|---------|-------------|
| **Executive cards** | Total VMs, vCPU/RAM/storage, legacy OS count, powered-off VMs |
| **OS distribution** | Doughnut chart of OS families (Windows Server, Windows Desktop, Linux, Other) |
| **Power state** | Pie chart of powered-on vs powered-off |
| **VMs per Datacenter** | Bar chart of VM density |
| **OS versions** | Horizontal bar of specific OS strings |
| **Hardware versions** | Doughnut of VMware virtual hardware versions |
| **Storage by Datacenter** | Provisioned storage per datacenter |

### 🏗️ Infrastructure deep-dives (unlocked with full RVTools export)

| Section | Highlights |
|---------|-----------|
| 🗺️ **Environment Topology** | VMs per Datacenter (rolled-up view), **indicative Azure VM family fit**, capacity rollups by cluster |
| 🏗️ **Host Capacity** | Host CPU/memory **utilisation distribution** and vCPU:core overcommit distribution — instantly see how many hosts are under pressure regardless of estate size |
| 💾 **Storage Dashboard** | Datastore **utilisation distribution** (% used buckets) and **over-provisioning distribution** — surfaces the shape of your storage estate at a glance |
| 💿 **Disk Analysis** | Thin vs thick provisioning split, top 15 VMs by disk capacity, per-disk breakdown with search + DC/cluster filters and CSV export |
| 🌐 **Network Analysis** | VMs per VLAN, adapter type distribution (vmxnet3 / E1000 / etc), per-NIC connectivity |
| ⚡ **Resource Allocation** | Top 15 VMs by vCPU and memory, CPU/memory reservations and limits |
| 📸 **Snapshot Health** | Old / oversized / orphaned snapshots highlighted with age and size |
| 🏥 **Environment Health** | Surfaces messages from the vHealth tab with severity classification |

### 🚀 Migration Readiness

| Feature | What it does |
|---------|-------------|
| **Risk Quadrant** | Scatter plot mapping every VM on Migration Complexity (X) vs Business Impact (Y), coloured by readiness group |
| **Readiness Groups** | Each VM placed into one of four migration cohorts: 🟢 **Ready Now** (lift & shift), 🟡 **Light Prep**, 🟠 **Modernise**, 🔴 **Remediate** |
| **Per-VM notes** | Plain-English migration recommendations based on OS age, power state, and resource profile |
| **Azure Migrate signpost** | The app makes it clear this is an indicative view — links out to Azure Migrate for proper assessment |

### 🔍 Explore, filter, and export

| Feature | What it does |
|---------|-------------|
| **Overview filters** | Datacenter / OS family / power state / readiness — scoped to the Overview cards + six analytics charts only (Wave Plan, Inventory, Risk Quadrant, and infrastructure sections always show the full estate) |
| **Sortable, paginated tables** | All 10 data tables paginate at 25 rows/page, with full-text search and click-to-sort columns |
| **CSV export** | Download readiness recommendations or the full inventory |
| **Offline HTML snapshot** | Self-contained `.html` report with charts baked in as images — works offline, has an amber **OFFLINE SNAPSHOT** banner |

### 🎨 General

| Feature | What it does |
|---------|-------------|
| **Light & dark mode** | Toggle from the nav bar, or auto-detect from your OS preference |
| **Connected-dots background** | Subtle animated SVG with parallax, themed for light and dark |
| **Single-file app** | Pure HTML/CSS/JS — no frameworks, no build step, runs offline once loaded |

---

## 🚀 How to Use

1. **Open** the [live app](https://rvtoolsviz.djtools.co.nz/) — it boots in demo mode so you can explore immediately
2. **Try the toggle** in the demo bar — switch between *vInfo Only* and *Full Export* to see what extra tabs unlock
3. **Drop your file** in the upload zone (or [grab the sample](test-samples/rvtools-sample.xlsx) if you don't have one handy)
4. **Filter** by datacenter, OS, power state, or readiness group — every chart and table updates live
5. **Review** the Migration Readiness section to plan your waves
6. **Export** as CSV or as a self-contained offline HTML snapshot

> **Need to export from RVTools?** In RVTools, go to **File → Export all to Excel** and save the `.xlsx`. Including all tabs unlocks every dashboard. New to RVTools? [Download it from Dell](https://www.dell.com/support/kbdoc/en-nz/000325532/rvtools).

---

## 🏗️ Architecture

| Aspect | Details |
|--------|---------|
| **Type** | Single-file HTML web application |
| **Frameworks** | None — pure HTML / CSS / vanilla JavaScript |
| **CDN dependencies** | [Chart.js](https://www.chartjs.org/) for visualisations, [SheetJS](https://sheetjs.com/) for `.xlsx` parsing |
| **Build step** | None — `index.html` deploys as-is |
| **Hosting** | Azure Static Web Apps (Free SKU) |
| **CI/CD** | GitHub Actions on `ubuntu-latest`, deploys via SWA CLI on every push to `main` |
| **Data privacy** | Zero server-side processing — all parsing happens in the browser |

---

## 📚 Documentation

| Document | What's inside |
|----------|---------------|
| 📋 [Specification](docs/SPEC.md) | Full app spec — data model, column mapping, readiness algorithm, every section enumerated |
| 📖 [How It Works](docs/howitworks.md) | Technical deep-dive — parser, multi-tab fan-out, charting, pagination helper, export pipeline |
| 🎤 [Talk Track](docs/talktrack.md) | End-to-end DevOps walkthrough from idea to production — useful for demos and presentations |

---

## 🗂️ Project Structure

```
djtools-rvtools-viz/
├── index.html                    # The whole app (single file, CDN dependencies only)
├── djtools.png                   # Banner image
├── README.md                     # This file
├── LICENSE                       # MIT license
├── SECURITY.md                   # Security reporting policy
├── test-samples/
│   └── rvtools-sample.xlsx       # Demo / test RVTools export
├── docs/
│   ├── SPEC.md                   # Full specification
│   ├── howitworks.md             # Technical deep-dive
│   └── talktrack.md              # Demo talk track
└── .github/
    ├── workflows/                # CI/CD: deploy.yml + validate.yml
    ├── ISSUE_TEMPLATE/           # Structured bug + feature forms
    ├── pull_request_template.md  # PR checklist
    └── copilot-instructions.md   # Copilot CLI context
```

---

## 🤝 Contributing

Contributions, ideas, and feedback are welcome.

1. Create a branch from `main` (`feature/`, `fix/`, or `docs/` prefix)
2. Make your changes — open `index.html` in any browser to test locally
3. Open a Pull Request — the PR template will guide you
4. After review, merge to `main` → it auto-deploys to Azure

Found a bug or have an idea? [Open an issue](https://github.com/DarrenJohns/djtools-rvtools-viz/issues/new/choose) — there are templates ready.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <strong>DJ Tools</strong> — Built with <a href="https://github.com/features/copilot/cli/">GitHub Copilot CLI</a>
</div>
