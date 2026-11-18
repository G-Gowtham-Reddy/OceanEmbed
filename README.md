# OceanEmbed – Ocean Temperature Reconstruction

SIH26066 Project: Full-stack application for ocean temperature reconstruction using geospatial machine learning embeddings and neural modeling.

---

## Project Structure

```text
Project395/
├── backend/
│   ├── main.py              # FastAPI application entrypoint with /api/health and CORS
│   └── requirements.txt     # Python dependencies (FastAPI, Uvicorn, NumPy, Pandas, Scikit-learn)
├── frontend/
│   ├── index.html           # HTML template
│   ├── package.json         # Node dependencies & npm scripts (Vite, React, Tailwind, Lucide)
│   ├── postcss.config.js    # PostCSS configuration
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   ├── tsconfig.json        # TypeScript root config
│   ├── tsconfig.app.json    # TypeScript app compiler options
│   ├── tsconfig.node.json   # TypeScript Vite node config
│   ├── vite.config.ts       # Vite build & dev server configuration
│   └── src/
│       ├── types.ts         # Navigation & data interfaces
│       ├── App.tsx          # Main shell with routing & responsive sidebar
│       ├── index.css        # Tailwind directives
│       ├── main.tsx         # React DOM root entrypoint
│       ├── vite-env.d.ts    # Vite TypeScript declarations
│       ├── components/
│       │   ├── Sidebar.tsx            # Navigation sidebar for all 8 pages
│       │   ├── TopNavbar.tsx          # Sticky top bar with API health status
│       │   ├── FilterBar.tsx          # Region, date, variable & depth range filters
│       │   └── OceanCrossSection.tsx  # Central underwater cross-section visualization
│       └── pages/
│           ├── DashboardPage.tsx      # Main research dashboard with metrics & cross-section
│           ├── DataExplorerPage.tsx   # ARGO float stations & vertical sounding curves
│           ├── ThreeDTempPage.tsx     # Isometric 3D multi-depth slicing canvas
│           ├── PredictionPage.tsx     # Subsurface reconstruction workflow & grid preview
│           ├── ModelAnalysisPage.tsx  # Latent embeddings & depth-wise RMSE loss curves
│           ├── ArgoValidationPage.tsx # Ground-truth in-situ CTD comparison (R² & bias)
│           ├── PreprocessingPage.tsx  # Quality control, despiking & density inversion checks
│           └── AboutProjectPage.tsx   # SIH26066 problem statement & institutional sources
├── .gitignore               # Ignored files (venv, node_modules, dist, cache)
└── README.md                # Project documentation and execution instructions
```

---

## Getting Started

### 1. Backend Setup (FastAPI)

1. Open a terminal and navigate to the `backend/` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux:**
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the development server:
   ```bash
   uvicorn main:app --reload --port 8001
   ```
   - API Root: [http://localhost:8001/](http://localhost:8001/)
   - Health Check: [http://localhost:8001/api/health](http://localhost:8001/api/health)
   - Interactive Docs: [http://localhost:8001/docs](http://localhost:8001/docs)

---

### 2. Frontend Setup (React + Vite + Tailwind CSS)

1. In a new terminal, navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   - Web App: [http://localhost:5173/](http://localhost:5173/)

---

## Phase Status

- **Phase 1: Project Scaffolding & Health Check** - Completed
  - Minimal clean structure
  - FastAPI health-check endpoint configured with CORS
  - React + Vite + Tailwind CSS frontend with live status verification
  - Essential ML dependencies pinned in `requirements.txt`

- **Phase 2: Frontend UI Development** - Completed
  - Modern, executive research dashboard redesign
  - Charcoal black (`#09090b`), soft silver (`#e4e4e7`), and subtle cyan (`#06b6d4`) palette
  - Avoids artificial water animations, photos, and distracting visual clutter
  - Real-time dynamic connection to FastAPI backend on port 8001 (`/api/ocean/temperature` and `/api/ocean/regions`)
  - Two-column core workspace:
    - **Interactive Ocean Map**: Vector geospatial map with clickable regional zones, temperature indicators, and coordinates
    - **Depth Temperature Visualizer**: Clean temperature curve from surface to selected depth, hover data probe, and plain-language layer breakdown
  - 4 Key KPI Cards: Surface Temperature, Mixed Layer Depth, Transition Depth, and Deep Ocean Temp
  - Dynamic top controls: Region selector, observation date, and depth range slider with automatic backend synchronization
  - 5 primary navigation views: Dashboard, 3D Ocean Visualization, Prediction, Model Evaluation, and About Project
