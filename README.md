# Vehicle Routing Problem (VRP) Solver

**A professional-grade solution to optimize delivery routes using Google OR-Tools, real-world geospatial data, and constraint-based optimization.**

![Version](https://img.shields.io/badge/version-3.0-blue) ![Python](https://img.shields.io/badge/python-3.8+-green) ![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen)

---

## 🎯 Overview

In logistics, the **"Last Mile"** is the most expensive and time-consuming part of the supply chain. This project tackles the **Vehicle Routing Problem (VRP)** — a variation of the famous Traveling Salesman Problem extended to multiple vehicles with real-world constraints.

**Real-world impact:** A savings of just 1 mile per driver per day can translate to millions of dollars in annual savings across enterprise fleets.

### What This Solver Does

Given:
- 📍 A list of delivery locations (latitude, longitude)
- 📦 Package demands for each delivery
- 🚗 A fleet of vehicles with capacity limits
- ⏰ Time windows for customer availability

It produces:
- ✅ Optimal routes for each driver (minimize total distance)
- ✅ ETA for each stop (respecting time windows)
- ✅ Capacity utilization per vehicle
- ✅ Cost-benefit analysis vs naive routing
- ✅ Interactive map visualization

---

## ✨ Features

### Core Capabilities
- **Multi-Vehicle Routing:** Distribute orders across heterogeneous fleet (3+ vehicles)
- **Variable Capacities:** Each vehicle can have different capacity limits
- **Capacity Constraints (CVRP):** Respect max load per vehicle
- **Time Windows (VRPTW):** Deliver within customer-specified hours
- **Real-World Routing:** OSRM API for actual driving distances/durations
- **Graceful Fallback:** Haversine algorithm if OSRM unavailable

### Advanced Features
- **Configuration Management:** JSON-based parameters (no code changes needed)
- **Input Validation:** Advanced data quality checks (15+ validations)
- **Error Handling:** Production-level fault tolerance
- **Unit Tests:** Pytest coverage for core modules
- **Interactive Visualization:** Folium maps with color-coded routes
- **Cost-Benefit Analysis:** Quantified improvement over naive approach

### Technical Highlights
- **Industry-Standard Solver:** Google OR-Tools (combinatorial optimization)
- **Search Strategy:** PATH_CHEAPEST_ARC + GUIDED_LOCAL_SEARCH
- **Optimization Time:** Tunable (default 5 seconds)
- **Fleet Utilization:** Track used vs idle vehicles

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      main.py                            │
│         Orchestrator & Entry Point                      │
└──────────────┬──────────────────────────────────────────┘
               │
       ┌───────┴────────┬──────────────┬──────────────┐
       │                │              │              │
   ┌───▼───┐      ┌────▼────┐   ┌─────▼────┐  ┌─────▼────┐
   │Config │      │Distance │   │Optimizer │  │   Viz    │
   │.json  │      │.py      │   │.py       │  │.py       │
   └───────┘      └────┬────┘   └─────┬────┘  └─────┬────┘
                       │              │              │
                   ┌───▼────────┐  ┌──▼──┐      ┌───▼──────┐
                   │ OSRM API   │  │OR-  │      │ Folium   │
                   │ (Real)     │  │Tools│      │ Maps     │
                   │ Haversine  │  │VRP  │      │ HTML     │
                   │ (Fallback) │  │     │      │ Output   │
                   └────────────┘  └─────┘      └──────────┘

Data Flow:
CSV → Validate → Distance Matrix → VRP Solver → Routes
              ↓                                      ↓
          Config JSON                          Visualization
```

### Module Responsibilities

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| **main.py** | Orchestration & CLI | `main()`, `validate_input()`, helper functions |
| **distance.py** | Distance calculations | `compute_distance_matrix()`, `haversine()` |
| **optimizer.py** | Route optimization | `solve_vrp()` with OR-Tools |
| **visualization.py** | Map generation | `plot_routes()`, `get_osrm_route()` |

---

## 📋 Requirements

- **Python:** 3.8 or higher
- **Dependencies:** See `requirements.txt`

**Key Libraries:**
- `ortools` — Google's combinatorial optimization library
- `pandas` — Data manipulation and CSV handling
- `folium` — Interactive map visualization
- `requests` — HTTP API calls (OSRM)
- `pytest` — Unit testing framework

---

## 🚀 Installation

### 1. Clone/Download Project
```bash
cd VRP_Project
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify Installation
```bash
# Run tests to verify setup
python -m pytest -v
```

Expected output:
```
tests/test_validation.py::test_valid_input PASSED
tests/test_validation.py::test_invalid_latitude PASSED
tests/test_distance.py::test_haversine_distance PASSED
tests/test_optimizer.py::test_vrp_solution_exists PASSED
```

---

## ⚙️ Configuration

All parameters are centralized in `config/config.json`:

```json
{
  "depot": {
    "lat": 13.0827,
    "lon": 80.2707
  },
  "vehicle": {
    "capacities": [20, 50, 100],
    "count": 3
  },
  "solver": {
    "time_limit": 5
  },
  "time": {
    "depot_start": 480,
    "depot_end": 1440
  }
}
```

| Parameter | Meaning | Example |
|-----------|---------|---------|
| `depot.lat/lon` | Starting warehouse location | 13.0827, 80.2707 (Chennai) |
| `vehicle.capacities` | Max units per vehicle | [20, 50, 100] = 3 vehicles |
| `vehicle.count` | Number of vehicles | 3 |
| `solver.time_limit` | Optimization time (seconds) | 5 (balance speed vs quality) |
| `time.depot_start/end` | Operating hours (minutes) | 480–1440 (8 AM – 2 PM) |

### Customize Configuration
Edit `config/config.json` to adjust:
- Warehouse location
- Fleet size and capacities
- Operating hours
- Optimization time

**No code changes needed!**

---

## 📊 Input Data Format

Orders are specified in `data/orders.csv`:

```csv
order_id,lat,lon,demand,start_time,end_time
1,13.05,80.25,30,480,540
2,13.06,80.26,15,600,660
3,13.07,80.27,40,540,600
...
```

| Column | Type | Meaning | Example |
|--------|------|---------|---------|
| `order_id` | Integer | Unique identifier | 1–999 |
| `lat` | Float | Latitude of delivery | 13.05 |
| `lon` | Float | Longitude of delivery | 80.25 |
| `demand` | Integer | Units to deliver | 1–100 |
| `start_time` | Integer | Earliest delivery (min) | 480 = 8 AM |
| `end_time` | Integer | Latest delivery (min) | 540 = 9 AM |

**Time Format:** Minutes from 00:00 (example: 480 = 8 AM, 1440 = midnight)

---

## 🎬 Quick Start (5 minutes)

### Run the Solver
```bash
cd src
python main.py
```

### Expected Output
```
✅ Input data validation passed
✅ OSRM API used successfully

========== OPTIMIZED ROUTES ==========

Optimized Vehicle 1:
Depot (ETA: 08:00) -> 6 (ETA: 08:03) -> 1 (ETA: 08:11) -> Depot (ETA: 12:09) -> END
Distance: 28.36 km
Load: 59 / 100

Optimized Vehicle 2:
Depot (ETA: 08:00) -> 3 (ETA: 09:00) -> 4 (ETA: 11:00) -> Depot (ETA: 13:13) -> END
Distance: 18.31 km
Load: 39 / 50

========== COMPARISON ==========
Optimized Total Distance: 46.67 km
Naive Total Distance: 49.41 km
Improvement: 5.56%

Map saved to outputs/routes_map.html

========== PERFORMANCE METRICS ==========
Total Vehicles Used: 2
Idle Vehicles: 1
Average Distance per Vehicle: 23.33 km
Max Route Distance: 28.36 km
```

### View the Map
Open `outputs/routes_map.html` in your browser to see:
- 🗺️ Interactive map centered on depot
- 📍 Delivery stops color-coded by vehicle
- 🛣️ Real road routes (not straight lines)
- 📌 Markers with stop details

---

## 📖 Detailed Usage

See [USAGE.md](./USAGE.md) for:
- Custom scenarios
- Multi-city deployments
- Parameter tuning
- Troubleshooting

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for:
- Function signatures
- Parameter details
- Return values
- Code examples

---

## 🧪 Testing

### Run All Tests
```bash
python -m pytest -v
```

### Run Specific Test File
```bash
python -m pytest tests/test_validation.py -v
```

### Run with Coverage
```bash
python -m pytest --cov=src tests/
```

**Test Coverage:**
- ✅ Input validation (edge cases)
- ✅ Distance calculations
- ✅ VRP solver
- ✅ Route generation

---

## 📁 Project Structure

```
VRP_Project/
├── README.md                    ← You are here
├── USAGE.md                     ← How to use
├── API_DOCUMENTATION.md         ← API reference
├── requirements.txt             ← Dependencies
├── config/
│   └── config.json             ← Configuration (edit this)
├── data/
│   └── orders.csv              ← Input orders
├── src/
│   ├── main.py                 ← Entry point & orchestrator
│   ├── distance.py             ← Distance matrix calculation
│   ├── optimizer.py            ← VRP solver (OR-Tools)
│   └── visualization.py        ← Map generation
├── tests/
│   ├── conftest.py            ← Pytest configuration
│   ├── test_validation.py     ← Validation tests
│   ├── test_distance.py       ← Distance tests
│   └── test_optimizer.py      ← Solver tests
└── outputs/
    └── routes_map.html        ← Generated map
```

---

## 🔧 Constraints & Capabilities

### Constraints Handled
| Constraint | Status | Example |
|-----------|--------|---------|
| **Capacity** | ✅ Yes | Max 100 units per vehicle |
| **Time Windows** | ✅ Yes | Deliver 9 AM – 5 PM only |
| **Distance** | ✅ Yes | Minimize total distance |
| **Multi-Vehicle** | ✅ Yes | Up to 100+ vehicles |
| **Heterogeneous Fleet** | ✅ Yes | Different vehicle sizes |

### Limitations
- OSRM API required for real routing (local fallback available)
- Optimization time tunable (default 5s for good balance)
- No vehicle speed profiles (uniform speed assumed)
- No vehicle type restrictions (all vehicles deliver all orders)

---

## 💰 Cost-Benefit Analysis

The solver compares **Optimized vs Naive** routing:

```
Naive Approach:     Alternating stop assignment (simple, suboptimal)
Optimized Approach: OR-Tools with constraints (complex, optimal)

Example Results:
  Distance Saved: 2.74 km (5.56% improvement)
  Time Saved: 8–12 minutes per vehicle
  Cost Saved: ~$82/day (assuming $30/km operational cost)
  Annual Impact: ~$30,000 savings (scaled to 365 days)
```

---

## ⚡ Performance

| Metric | Value | Notes |
|--------|-------|-------|
| **Setup Time** | <1s | Loading config + data |
| **Distance Matrix** | 1–3s | OSRM API call |
| **Optimization** | 5s | OR-Tools solver (tunable) |
| **Visualization** | 1–2s | Folium map generation |
| **Total Runtime** | ~10s | For 8 orders, 3 vehicles |

**Scalability:**
- Tested: 8 orders, 3 vehicles
- Expected: Up to 50 orders, 10 vehicles (30–60 seconds)
- With optimization: 100+ orders possible (tune time_limit)

---

## 🛠️ Troubleshooting

### Issue: OSRM API Error
```
⚠️ OSRM failed, switching to Haversine fallback...
```
**Solution:** Check internet connection. Solver automatically uses Haversine (straight-line distances).

### Issue: Validation Error
```
ValueError: Total demand (160) exceeds fleet capacity (120)
```
**Solution:** Increase vehicle capacities in `config.json` or reduce orders.

### Issue: No Solution Found
```
❌ No solution found! Check constraints.
```
**Solution:** 
- Vehicle capacity too low
- Time windows too tight
- Increase `solver.time_limit`

---

## 📚 Technical Stack

- **Python 3.8+** — Programming language
- **Google OR-Tools** — Combinatorial optimization
- **OSRM API** — Real-world routing
- **Pandas** — Data processing
- **Folium** — Map visualization
- **Pytest** — Testing framework

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

---

## 📄 License

This project is provided as-is for educational and commercial use.

---

## 📞 Support

For issues, questions, or suggestions:
1. Check [USAGE.md](./USAGE.md) for examples
2. Review [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for reference
3. Run tests to verify setup: `pytest -v`

---

## 🎓 Learning Resources

- [Vehicle Routing Problem - Wikipedia](https://en.wikipedia.org/wiki/Vehicle_routing_problem)
- [Google OR-Tools Tutorial](https://developers.google.com/optimization/routing)
- [OSRM Routing Engine](http://project-osrm.org/)
- [Combinatorial Optimization - MIT](https://ocw.mit.edu/)

---

**Version:** 3.0 | **Last Updated:** April 15, 2026 | **Status:** Production Ready ✅
