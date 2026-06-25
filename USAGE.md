# Usage Guide - Vehicle Routing Problem Solver

Complete guide to using the VRP solver with examples and common scenarios.

---

## 📖 Table of Contents
1. [Quick Start (5 minutes)](#quick-start)
2. [Running the Solver](#running-the-solver)
3. [Understanding Output](#understanding-output)
4. [Custom Scenarios](#custom-scenarios)
5. [Interpreting Results](#interpreting-results)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

---

## 🚀 Quick Start

### Step 1: Setup (One-time)
```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m pytest -v
```

### Step 2: Run the Solver
```bash
cd src
python main.py
```

### Step 3: View Results
1. **Console Output:** Shows optimized routes, comparisons, metrics
2. **HTML Map:** Open `outputs/routes_map.html` in browser

**Total time:** ~10 seconds for sample data

---

## 🎬 Running the Solver

### Basic Execution
```bash
cd src
python main.py
```

### What Happens
1. ✅ Loads configuration from `config/config.json`
2. ✅ Reads orders from `data/orders.csv`
3. ✅ Validates all input data (15 checks)
4. ✅ Computes distance matrix via OSRM API (or Haversine fallback)
5. ✅ Optimizes routes using OR-Tools
6. ✅ Generates visualization map
7. ✅ Outputs performance metrics

### Expected Console Output

```
✅ Input data validation passed (Advanced)
✅ OSRM API used successfully

========== OPTIMIZED ROUTES ==========

Optimized Vehicle 1:
Depot (ETA: 08:00) -> 6 (ETA: 08:03) -> 1 (ETA: 08:11) -> 2 (ETA: 10:00) -> 7 (ETA: 10:07) -> 5 (ETA: 12:00) -> Depot (ETA: 12:09) -> END
Distance: 28.36 km
Load: 59 / 100

Optimized Vehicle 2:
Depot (ETA: 08:00) -> 3 (ETA: 09:00) -> 4 (ETA: 11:00) -> 8 (ETA: 13:00) -> Depot (ETA: 13:13) -> END
Distance: 18.31 km
Load: 39 / 50

========== NAIVE ROUTES ==========

Naive Vehicle 1:
Depot -> 1 -> 3 -> 5 -> 7 -> Depot
Distance: 27.01 km

Naive Vehicle 2:
Depot -> 2 -> 4 -> 6 -> 8 -> Depot
Distance: 22.41 km

========== COMPARISON ==========
Optimized Total Distance: 46.67 km
Naive Total Distance: 49.41 km
Improvement: 5.56%

⚠️ Note: Naive solution does not consider capacity/time constraints, 
so it may be infeasible. Optimized solution is valid, constraint-aware and realistic

Map saved to outputs/routes_map.html

========== PERFORMANCE METRICS ==========
Total Vehicles Used: 2
Idle Vehicles: 1
Average Distance per Vehicle: 23.33 km
Max Route Distance: 28.36 km
```

---

## 📊 Understanding Output

### 1. Optimized Routes Section

```
Optimized Vehicle 1:
Depot (ETA: 08:00) -> 6 (ETA: 08:03) -> 1 (ETA: 08:11) -> Depot (ETA: 12:09) -> END
Distance: 28.36 km
Load: 59 / 100
```

**What it means:**
- **Route:** Sequence of stops (left-to-right)
- **ETA:** Estimated Time of Arrival in HH:MM format
- **Distance:** Total driving distance for this vehicle
- **Load:** Packages delivered / Vehicle capacity

**Example interpretation:**
- Vehicle 1 starts at 8:00 AM at depot
- Drives 3 minutes to stop #6, arrives 8:03 AM
- Drives 8 minutes to stop #1, arrives 8:11 AM (waits until 8:00 – respects time window)
- Total: 28.36 km, 59 units in a 100-unit vehicle

### 2. Naive Routes Section

```
Naive Vehicle 1:
Depot -> 1 -> 3 -> 5 -> 7 -> Depot
Distance: 27.01 km
```

**What it means:**
- Baseline routing (alternating stop assignment)
- Simple but ignores constraints (may be infeasible)
- Used for comparison only

### 3. Comparison Section

```
Optimized Total Distance: 46.67 km
Naive Total Distance: 49.41 km
Improvement: 5.56%
```

**Metrics breakdown:**
- **Optimized Total Distance:** Sum of all vehicle routes (optimal solution)
- **Naive Total Distance:** Sum of naive baseline routes
- **Improvement %:** Distance saved = `(naive - optimized) / naive * 100`

**Business Interpretation:**
- Save 2.74 km per day (5.56%)
- At $30/km: Save $82.20 daily
- Annually: Save ~$30,000 (365 days)

### 4. Performance Metrics Section

```
Total Vehicles Used: 2
Idle Vehicles: 1
Average Distance per Vehicle: 23.33 km
Max Route Distance: 28.36 km
```

**Metrics explained:**
| Metric | Meaning |
|--------|---------|
| **Used Vehicles** | Number of vehicles with actual deliveries |
| **Idle Vehicles** | Vehicles not used (fleet over-sizing indicator) |
| **Avg Distance/Vehicle** | Mean kilometers per vehicle |
| **Max Route Distance** | Longest single vehicle route |

---

## 🎯 Custom Scenarios

### Scenario 1: Small City Delivery

**Goal:** Optimize 20 orders across Chennai

**Steps:**

1. Create `data/orders_chennai.csv`:
```csv
order_id,lat,lon,demand,start_time,end_time
1,13.05,80.25,25,480,600
2,13.06,80.26,15,540,660
3,13.07,80.27,30,600,720
...20 orders...
```

2. Update `config/config.json`:
```json
{
  "depot": {
    "lat": 13.0827,
    "lon": 80.2707
  },
  "vehicle": {
    "capacities": [50, 50, 100],
    "count": 3
  },
  "solver": {
    "time_limit": 10
  },
  "time": {
    "depot_start": 480,
    "depot_end": 1440
  }
}
```

3. Update `main.py` to read new CSV:
```python
df = pd.read_csv("../data/orders_chennai.csv")  # Change file name
```

4. Run solver:
```bash
python main.py
```

### Scenario 2: Morning Rush Deliveries

**Goal:** Handle peak morning demand (8 AM - 11 AM only)

**Configuration:**
```json
{
  "time": {
    "depot_start": 480,      // 8:00 AM
    "depot_end": 660         // 11:00 AM (3-hour window)
  }
}
```

**Result:** Solver will prioritize quick deliveries within tight time windows. May use more vehicles.

### Scenario 3: Multiple Depots

**Goal:** Route from multiple warehouses

**Approach:**
1. Modify `main.py` to handle depot selection:
```python
# For depot 1:
depot = (config["depot"]["lat"], config["depot"]["lon"])

# For depot 2 (optional extension):
# depot = (13.2, 80.3)  # Different warehouse
```

2. Create separate CSV files per depot
3. Run solver for each depot separately

### Scenario 4: High Demand Day

**Goal:** Handle surge in orders

**Configuration:**
```json
{
  "vehicle": {
    "capacities": [50, 50, 50, 100, 100],  // 5 vehicles instead of 3
    "count": 5
  }
}
```

**Result:** Larger fleet handles more orders efficiently.

---

## 📈 Interpreting Results

### Route Quality Indicators

**Good Solution:**
- ✅ Improvement > 5% (naive vs optimized)
- ✅ Few idle vehicles (close to full fleet utilization)
- ✅ Balanced loads (similar per vehicle)
- ✅ Realistic ETAs (3–8 hour workday)

**Example:**
```
Improvement: 5.56%                ← Good (>5%)
Idle Vehicles: 1 out of 3         ← Acceptable (67% utilization)
Load distribution:
  Vehicle 1: 59/100 = 59%         ← Good utilization
  Vehicle 2: 39/50 = 78%          ← Excellent utilization
  Vehicle 3: Idle                 ← Acceptable (smallest vehicle unused)
```

**Suboptimal Solution (when it happens):**
- ⚠️ Improvement < 1% (poor constraint interactions)
- ⚠️ Many idle vehicles (oversized fleet)
- ⚠️ Unbalanced loads (one vehicle 100%, others 20%)

**Solution:** Increase `solver.time_limit` in config (default 5s)

### Time Window Compliance

**Output shows:**
```
Optimized Vehicle 1:
Depot (ETA: 08:00) -> 6 (ETA: 08:03) -> 1 (ETA: 08:11) -> ...
                                      Order 1: 480-540 (8:00-9:00)
```

**Verify:**
- Order 1 ETA (08:11) is within window (08:00-09:00) ✅
- If ETA > end_time: CONSTRAINT VIOLATION ❌

All ETAs in optimized solution automatically respect time windows.

### Capacity Compliance

**Output shows:**
```
Distance: 28.36 km
Load: 59 / 100
```

**Verify:**
- Load (59) ≤ Capacity (100) ✅
- All optimized routes satisfy capacity constraints

---

## 🆘 Troubleshooting

### Issue 1: FileNotFoundError
```
FileNotFoundError: [Errno 2] No such file or directory: '../data/orders.csv'
```

**Causes & Solutions:**
1. Running from wrong directory
   ```bash
   # Wrong:
   cd VRP_Project
   python src/main.py
   
   # Correct:
   cd VRP_Project/src
   python main.py
   ```

2. Missing data file
   ```bash
   # Verify file exists:
   ls ../data/orders.csv
   ```

### Issue 2: Validation Error
```
ValueError: Total demand (360) exceeds fleet capacity (170)
```

**Solutions:**
1. Increase vehicle capacities:
   ```json
   "capacities": [50, 100, 200]  // Total 350, still need 360+
   ```

2. Reduce order quantities in CSV

3. Use more vehicles:
   ```json
   "count": 4  // Add extra vehicle
   ```

### Issue 3: OSRM API Error
```
⚠️ OSRM failed, switching to Haversine fallback...
Error: OSRM unavailable (offline mode)
```

**Causes & Solutions:**
1. No internet connection → Use Haversine (automatic fallback)
2. OSRM service down → Use Haversine (automatic fallback)
3. Rate limited → Wait 5 minutes, retry

**Result:** Solver uses straight-line distances instead of actual roads. Routes still optimized but less accurate.

### Issue 4: Time Window Infeasibility
```
❌ No solution found! Check constraints.
```

**Causes & Solutions:**
1. Time windows too tight → Relax time windows in CSV
2. Insufficient time for delivery → Increase `solver.time_limit`
3. Vehicle capacity too low → Check `capacities` in config

### Issue 5: Long Optimization Time
```
(Solver running... 30+ seconds)
```

**Causes & Solutions:**
1. Large dataset (100+ orders) → Expected behavior
2. Tight constraints → Solver requires more search
3. Low `time_limit` insufficient → Increase in config:
   ```json
   "solver": {
     "time_limit": 15  // Increase from 5 to 15 seconds
   }
   ```

---

## 🔧 Advanced Usage

### 1. Custom Solver Parameters

Edit `src/optimizer.py`:
```python
# Change search strategy:
search_parameters.first_solution_strategy = \
    routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC  // Try different strategies

# Change time limit (in seconds):
search_parameters.time_limit.seconds = 15  // Increase optimization time

# Change local search:
search_parameters.local_search_metaheuristic = \
    routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING
```

### 2. Batch Processing Multiple Scenarios

Create `batch_process.py`:
```python
import os
import json
import pandas as pd
from main import main

scenarios = [
    {"config": "config/morning.json", "data": "data/morning_orders.csv"},
    {"config": "config/evening.json", "data": "data/evening_orders.csv"},
]

for scenario in scenarios:
    print(f"\nProcessing {scenario['config']}...")
    # Load config and data
    # Run solver
    # Save results
    main()
```

### 3. Real-time Order Insertion

Modify `main.py` to accept new orders:
```python
def add_dynamic_order(order_data):
    # Insert new order into current routes
    # Minimize disruption to already-assigned stops
    # Re-optimize partial routes
    pass
```

### 4. Vehicle Specialization

Extend config:
```json
{
  "vehicles": [
    {
      "id": 1,
      "capacity": 100,
      "type": "delivery",
      "allowed_zones": ["north", "west"]
    },
    {
      "id": 2,
      "capacity": 30,
      "type": "express",
      "allowed_zones": ["all"]
    }
  ]
}
```

---

## 📊 Batch Results Analysis

**Tips for comparing multiple runs:**

1. Save results with timestamps:
   ```bash
   mkdir results
   python main.py > results/run_$(date +%s).log
   ```

2. Compare improvements:
   ```python
   # Extract from multiple runs
   runs = [
       {"date": "2024-04-15", "improvement": 5.56},
       {"date": "2024-04-16", "improvement": 6.12},
   ]
   avg_improvement = sum(r["improvement"] for r in runs) / len(runs)
   ```

3. Track metrics over time:
   - Average distance per route
   - Vehicle utilization %
   - Time window compliance %

---

## 📞 Getting Help

**Issues?**
1. Check this guide for your scenario
2. Review console output for error messages
3. Run tests: `pytest -v`
4. Check config/data files for obvious issues

**Common Fixes:**
- Clear `outputs/` directory before rerun
- Verify PyTest passes: `pytest -v`
- Check CSV format matches specification
- Ensure config.json is valid JSON

---

## 🎓 Next Steps

- Read [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for function details
- Explore code in `src/` directory
- Run tests with coverage: `pytest --cov=src`
- Modify configuration and experiment

---

**Last Updated:** April 15, 2026 | **Version:** 3.0
