# API Documentation - VRP Solver

Complete reference for all functions, classes, and modules in the VRP solver.

---

## 📖 Table of Contents
1. [main.py](#mainpy)
2. [distance.py](#distancepy)
3. [optimizer.py](#optimizerpy)
4. [visualization.py](#visualizationpy)
5. [Data Structures](#data-structures)
6. [Return Values](#return-values)
7. [Examples](#examples)
8. [Error Handling](#error-handling)

---

## main.py

Main orchestrator module coordinating all solver components.

### validate_input()

Validates order data against 15 quality checks.

```python
def validate_input(df, vehicle_capacities, num_vehicles):
    """
    Validate input order data for VRP solver.
    
    Performs 15 comprehensive checks including:
    - Required columns presence
    - Data type validation
    - Geographic coordinate ranges
    - Time window logic
    - Capacity feasibility
    - Duplicate detection
    
    Args:
        df (pd.DataFrame): Order data with columns:
            - order_id (int): Unique order identifier
            - lat (float): Latitude [-90, 90]
            - lon (float): Longitude [-180, 180]
            - demand (int): Units to deliver [0, max_capacity]
            - start_time (int): Earliest delivery [0, 1440]
            - end_time (int): Latest delivery [0, 1440]
        
        vehicle_capacities (list[int]): Max capacity per vehicle
            Example: [50, 100, 75] for 3 vehicles
        
        num_vehicles (int): Count of available vehicles
    
    Returns:
        None: Prints success message if valid
    
    Raises:
        ValueError: If any validation fails with descriptive message
    
    Examples:
        >>> import pandas as pd
        >>> df = pd.read_csv("orders.csv")
        >>> validate_input(df, [50, 100, 75], 3)
        ✅ Input data validation passed (Advanced)
        
        >>> df_bad = df.copy()
        >>> df_bad.loc[0, 'lat'] = 200  # Invalid latitude
        >>> validate_input(df_bad, [50], 1)
        ValueError: Invalid latitude values
    
    Validation Checks:
        1. Required columns: ✅ order_id, lat, lon, demand, start_time, end_time
        2. Missing values: ✅ No NaN/null values
        3. Latitude range: ✅ [-90, 90]
        4. Longitude range: ✅ [-180, 180]
        5. Negative demand: ✅ All >= 0
        6. Time window logic: ✅ start_time <= end_time
        7. Duplicate order IDs: ✅ All unique
        8. Total capacity: ✅ sum(demand) <= sum(capacities)
        9. Individual demand: ✅ demand <= max(capacities)
        10. Time window sanity: ✅ [0, 1440] minutes
        11-15. Additional internal checks
    """
```

### calculate_route_distance()

Calculates total distance for a route.

```python
def calculate_route_distance(route, distance_matrix):
    """
    Calculate total distance traveled in a route.
    
    Sums distances between consecutive stops including
    returns to depot (final node = 0).
    
    Args:
        route (list[int]): Sequence of node indices
            Example: [0, 5, 3, 1, 0]
            - Starts at depot (0)
            - Visits nodes 5, 3, 1
            - Returns to depot (0)
        
        distance_matrix (list[list[float]]): Distance between all pairs
            Example: [[0, 10, 20], [10, 0, 15], [20, 15, 0]]
            - distance_matrix[i][j] = distance from node i to j
    
    Returns:
        float: Total distance in kilometers
    
    Example:
        >>> distance_matrix = [
        ...     [0, 5, 10],
        ...     [5, 0, 6],
        ...     [10, 6, 0]
        ... ]
        >>> route = [0, 1, 2, 0]
        >>> calculate_route_distance(route, distance_matrix)
        21  # 5 + 6 + 10
    """
```

### calculate_eta()

Calculates estimated time of arrival for each stop.

```python
def calculate_eta(route, duration_matrix, time_windows):
    """
    Calculate ETA for each stop respecting time windows.
    
    Simulates driving and waiting times. If arrival is before
    customer's start_time, driver waits. Ensures all ETAs
    fall within customer's [start_time, end_time] window.
    
    Args:
        route (list[int]): Sequence of node indices
            Example: [0, 2, 1, 3, 0]
        
        duration_matrix (list[list[float]]): Travel time between nodes (minutes)
            Example: [[0, 5, 10], [5, 0, 6], [10, 6, 0]]
        
        time_windows (list[tuple]): (start, end) for each node (minutes from 00:00)
            Example: [(480, 1440), (480, 600), (600, 720)]
            - Depot: 8 AM - Midnight
            - Order 1: 8 AM - 10 AM
            - Order 2: 10 AM - 12 PM
    
    Returns:
        list[int]: ETA for each stop (minutes from 00:00)
        Example: [480, 485, 525, 540]
    
    Algorithm:
        current_time = depot_start
        for each node in route:
            if first node:
                current_time = max(current_time, node_start_time)
            else:
                current_time += travel_time(prev, node)
                if current_time < node_start_time:
                    current_time = node_start_time  # Wait for window
        return current_time
    
    Example:
        >>> duration_matrix = [[0, 5, 10], [5, 0, 6], [10, 6, 0]]
        >>> time_windows = [(480, 1440), (480, 600), (600, 720)]
        >>> route = [0, 1, 0]
        >>> calculate_eta(route, duration_matrix, time_windows)
        [480, 485, 490]
    """
```

### format_time()

Converts minutes to HH:MM format.

```python
def format_time(minutes):
    """
    Convert minutes from 00:00 to HH:MM format.
    
    Args:
        minutes (int): Minutes from midnight (0-1440)
            Example: 480 = 8 AM, 900 = 3 PM
    
    Returns:
        str: Formatted time HH:MM
        Example: "08:00", "15:30"
    
    Example:
        >>> format_time(480)
        "08:00"
        >>> format_time(900)
        "15:00"
        >>> format_time(1125)
        "18:45"
    """
```

### calculate_load()

Calculates total demand for a route.

```python
def calculate_load(route, demands):
    """
    Calculate total package load for a route.
    
    Args:
        route (list[int]): Node indices in route
            Example: [0, 1, 3, 5, 0]
        
        demands (list[int]): Demand at each node
            Example: [0, 20, 15, 30, 0]
            - Depot: 0 (no pickup/delivery)
            - Orders: actual demands
    
    Returns:
        int: Total units in route (excludes depot)
    
    Example:
        >>> route = [0, 1, 3, 5, 0]
        >>> demands = [0, 20, 15, 30, 0]
        >>> calculate_load(route, demands)
        65  # 20 + 15 + 30
    """
```

### main()

Main entry point orchestrating entire solver.

```python
def main():
    """
    Orchestrate entire VRP optimization pipeline.
    
    Workflow:
        1. Load configuration from config/config.json
        2. Load order data from data/orders.csv
        3. Validate input (15 checks)
        4. Compute distance matrix (OSRM + fallback)
        5. Optimize routes using OR-Tools
        6. Calculate ETAs, distances, loads
        7. Compare vs naive baseline
        8. Generate visualization
        9. Output performance metrics
    
    Configuration Requirements:
        - config/config.json must contain:
            {
                "depot": {"lat": 13.0827, "lon": 80.2707},
                "vehicle": {"capacities": [50, 100, 75], "count": 3},
                "solver": {"time_limit": 5},
                "time": {"depot_start": 480, "depot_end": 1440}
            }
    
    Input Data Requirements:
        - data/orders.csv with columns:
            order_id, lat, lon, demand, start_time, end_time
    
    Output Files:
        - Console: Route assignments, metrics, comparison
        - outputs/routes_map.html: Interactive map visualization
    
    Raises:
        ValueError: If configuration invalid or data validation fails
        FileNotFoundError: If config.json or orders.csv missing
        requests.exceptions.RequestException: If OSRM API fails
            (falls back to Haversine)
    
    Example:
        >>> if __name__ == "__main__":
        ...     main()
        
        Output:
        ✅ Input data validation passed (Advanced)
        ✅ OSRM API used successfully
        
        ========== OPTIMIZED ROUTES ==========
        Optimized Vehicle 1: ...
        ...
        Map saved to outputs/routes_map.html
    """
```

---

## distance.py

Distance matrix computation with API and fallback support.

### haversine()

Great-circle distance calculation.

```python
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate great-circle distance between two geographic points.
    
    Uses Haversine formula for accurate distance calculation on Earth's
    surface. Useful as fallback when OSRM API unavailable.
    
    Args:
        lat1 (float): Starting latitude [-90, 90]
        lon1 (float): Starting longitude [-180, 180]
        lat2 (float): Ending latitude [-90, 90]
        lon2 (float): Ending longitude [-180, 180]
    
    Returns:
        float: Distance in kilometers
    
    Formula:
        a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
        c = 2 × arcsin(√a)
        d = R × c  (R = Earth radius ≈ 6371 km)
    
    Accuracy:
        ± 0.5% error (excellent for routing)
    
    Example:
        >>> # Chennai to nearby point (4 km away)
        >>> haversine(13.0827, 80.2707, 13.05, 80.25)
        4.17
    
    Note:
        - Does NOT account for road networks
        - Calculates "as the crow flies" distance
        - Used as fallback when OSRM unavailable
        - Faster than API calls (instant, no network)
    """
```

### compute_distance_matrix()

Computes distance and duration matrix between all location pairs.

```python
def compute_distance_matrix(locations):
    """
    Compute distance and duration between all location pairs.
    
    Primary: Uses OSRM Open Routing Service API for real road distances
    Fallback: Uses Haversine if OSRM unavailable
    
    Args:
        locations (list[tuple[float, float]]): List of (lat, lon) coordinates
            Example: [(13.0827, 80.2707), (13.05, 80.25), (13.06, 80.26)]
            - First location should be depot
            - Rest are delivery locations
    
    Returns:
        tuple[list[list[float]], list[list[float]]]:
        - distance_matrix: Distance between all pairs (km)
        - duration_matrix: Travel time between all pairs (minutes)
        
        Both are n×n matrices where n = len(locations)
        Example:
            distance_matrix = [
                [0, 4.17, 5.23],
                [4.17, 0, 1.02],
                [5.23, 1.02, 0]
            ]
            duration_matrix = [
                [0, 8.3, 10.5],
                [8.3, 0, 2.0],
                [10.5, 2.0, 0]
            ]
    
    OSRM API Details:
        - Endpoint: http://router.project-osrm.org/table/v1/driving/
        - Timeout: 5 seconds
        - Fallback: Haversine (straight-line) distances
        - No rate limiting (public service)
    
    Conversion:
        - Distance: meters → kilometers (÷1000)
        - Duration: seconds → minutes (÷60)
    
    Error Handling:
        - HTTP error → Fallback to Haversine
        - Invalid response → Fallback to Haversine
        - Timeout → Fallback to Haversine
        - No exception (always returns valid matrix)
    
    Example:
        >>> locations = [(13.0827, 80.2707), (13.05, 80.25), (13.06, 80.26)]
        >>> dist_matrix, dur_matrix = compute_distance_matrix(locations)
        >>> print(dist_matrix[0][1])
        4.17  # km from depot to location 1
        >>> print(dur_matrix[0][1])
        8.3   # minutes travel time
    
    Print Output:
        ✅ OSRM API used successfully  (if API available)
        ⚠️ OSRM failed, switching to Haversine fallback...  (if API down)
    """
```

---

## optimizer.py

Vehicle Routing Problem optimization using Google OR-Tools.

### solve_vrp()

Solves the Vehicle Routing Problem using constraint optimization.

```python
def solve_vrp(distance_matrix, duration_matrix, demands, 
              vehicle_capacities, num_vehicles, time_windows):
    """
    Solve Vehicle Routing Problem with capacity and time constraints.
    
    Uses Google OR-Tools routing library to find optimal or near-optimal
    routes minimizing total distance while respecting:
    - Vehicle capacity constraints
    - Time window constraints
    - Distance minimization objective
    
    Args:
        distance_matrix (list[list[float]]): Distance between all pairs (km)
            Shape: n × n where n = len(locations)
            distance_matrix[i][j] = distance from node i to j
        
        duration_matrix (list[list[float]]): Travel time between all pairs (minutes)
            Shape: n × n
            duration_matrix[i][j] = time to travel from i to j
        
        demands (list[int]): Package demand at each node
            demands[0] = 0 (depot doesn't have demand)
            demands[i] = units for order i
            Example: [0, 20, 15, 30, 25]
        
        vehicle_capacities (list[int]): Max capacity per vehicle
            Length = num_vehicles
            Example: [50, 75, 100] for 3 vehicles with different sizes
        
        num_vehicles (int): Number of vehicles available
            Example: 3
        
        time_windows (list[tuple[int, int]]): (start, end) time for each node (minutes)
            time_windows[0] = depot hours, e.g., (480, 1440)
            time_windows[i] = customer i hours, e.g., (600, 720)
            Example: [(480, 1440), (480, 600), (600, 720), ...]
    
    Returns:
        list[list[int]]: Routes for each vehicle
            - Returns list of len(num_vehicles)
            - Each route starts and ends at depot (node 0)
            - Example: [[0, 1, 3, 0], [0, 2, 4, 5, 0], [0, 6, 0]]
              - Vehicle 1: depot → order 1 → order 3 → depot
              - Vehicle 2: depot → order 2 → order 4 → order 5 → depot
              - Vehicle 3: depot → order 6 → depot
        - If no solution found, returns []
    
    Constraints Enforced:
        1. Capacity: sum(demands in route) <= vehicle_capacity
        2. Time Window: arrival_time ∈ [start_time, end_time]
        3. Distance: Minimized as primary objective
    
    Optimization Strategy:
        - First Solution: PATH_CHEAPEST_ARC (greedy initial solution)
        - Local Search: GUIDED_LOCAL_SEARCH (metaheuristic refinement)
        - Time Limit: 5 seconds (tunable in config)
    
    Special Handling:
        - Depot start time fixed to config["time"]["depot_start"]
        - Vehicle fixed cost: 5000 (penalizes unused vehicles)
        - Waiting time allowed: 100 minutes (for time window compliance)
    
    Raises:
        Exception: If no feasible solution found (returns empty list)
    
    Example:
        >>> distance_matrix = [
        ...     [0, 10, 20, 30],
        ...     [10, 0, 15, 25],
        ...     [20, 15, 0, 10],
        ...     [30, 25, 10, 0]
        ... ]
        >>> duration_matrix = distance_matrix  # Assume duration = distance
        >>> demands = [0, 20, 15, 30]  # Depot has no demand
        >>> vehicle_capacities = [50, 50]  # 2 vehicles
        >>> num_vehicles = 2
        >>> time_windows = [
        ...     (480, 1440),  # Depot: 8 AM - midnight
        ...     (480, 600),   # Order 1: 8-10 AM
        ...     (600, 720),   # Order 2: 10 AM - 12 PM
        ...     (720, 840)    # Order 3: 12-2 PM
        ... ]
        >>> routes = solve_vrp(
        ...     distance_matrix, duration_matrix, demands,
        ...     vehicle_capacities, num_vehicles, time_windows
        ... )
        >>> print(routes)
        [[0, 1, 2, 0], [0, 3, 0]]
        # Vehicle 1: Depot → Order 1 → Order 2 → Depot
        # Vehicle 2: Depot → Order 3 → Depot
    
    Performance:
        - Small problem (8 orders, 3 vehicles): ~10 seconds
        - Medium problem (20 orders, 5 vehicles): ~30 seconds
        - Large problem (100+ orders): May need increased time_limit
    """
```

---

## visualization.py

Interactive map generation using Folium.

### get_osrm_route()

Fetches real road route from OSRM API.

```python
def get_osrm_route(coords):
    """
    Fetch actual road route between coordinates using OSRM API.
    
    Returns the geographic coordinates along real roads (not straight line).
    Used to draw realistic routes on map.
    
    Args:
        coords (list[tuple[float, float]]): Ordered waypoints (lat, lon)
            Example: [(13.0827, 80.2707), (13.05, 80.25), (13.06, 80.26)]
            - Must be minimum 2 points
            - Order matters (defines route direction)
    
    Returns:
        list[tuple[float, float]]: Geographic coordinates along actual roads (lat, lon)
            Example: [(13.0827, 80.2707), (13.08, 80.26), (13.07, 80.25), ...]
            - Includes all intermediate points along roads
            - Ready for Folium PolyLine
    
    Fallback Behavior:
        If OSRM API fails: Returns input coords (straight lines)
        Result: Map shows simplified routes but still functional
    
    OSRM API Details:
        - Endpoint: http://router.project-osrm.org/route/v1/driving/
        - Timeout: 5 seconds
        - Returns GeoJSON format
        - Free, no authentication required
    
    Error Handling:
        - HTTP errors → Fallback to input coordinates
        - Timeout → Fallback to input coordinates
        - Invalid response → Fallback to input coordinates
        - No exception (always returns valid coordinates)
    
    Example:
        >>> coords = [(13.0827, 80.2707), (13.05, 80.25)]
        >>> route = get_osrm_route(coords)
        >>> len(route) > len(coords)  # More points due to roads
        True
        >>> route[0]
        (13.0827, 80.2707)  # Starts at first coordinate
    
    Print Output:
        ✅ Returns road routes (if OSRM available)
        ⚠️ OSRM route failed, using straight lines...  (if OSRM down)
    """
```

### plot_routes()

Generates interactive map with routes visualization.

```python
def plot_routes(locations, routes, output_file="routes_map.html"):
    """
    Generate interactive Folium map with optimized routes.
    
    Creates beautiful map showing:
    - Depot location (black home marker)
    - Delivery stops (color-coded by vehicle)
    - Route paths (real roads from OSRM or straight lines)
    - Interactive markers with stop details
    
    Args:
        locations (list[tuple[float, float]]): All location coordinates (lat, lon)
            locations[0] = depot (starting point)
            locations[1:] = delivery locations
            Example: [(13.0827, 80.2707), (13.05, 80.25), (13.06, 80.26)]
        
        routes (list[list[int]]): Routes from VRP solver
            Example: [[0, 1, 3, 0], [0, 2, 4, 0]]
            - Each route starts and ends at 0 (depot)
            - Node indices refer to locations
        
        output_file (str): Path for output HTML file
            Default: "routes_map.html"
            Full path recommended: "../outputs/routes_map.html"
    
    Returns:
        None: Writes HTML file to disk
    
    Map Features:
        - Centered on depot location
        - Zoom level: 13 (city street level)
        - Base tiles: OpenStreetMap (detailed for roads)
        - Interactive: Pan, zoom, click markers
    
    Markers:
        Depot: Black house icon with label "Depot"
        Stops:
        - Red = Vehicle 1
        - Blue = Vehicle 2
        - Green = Vehicle 3
        - Purple, Orange for vehicles 4+
        - Popup shows: "Stop {node_id}\nVehicle {vehicle_num}"
    
    Routes:
        - PolyLine for each vehicle (color-coded)
        - Line weight: 5 pixels
        - Opacity: 0.8 (slightly transparent)
        - Uses OSRM for real roads (or fallback to straight lines)
    
    Example:
        >>> locations = [(13.0827, 80.2707), (13.05, 80.25), (13.06, 80.26)]
        >>> routes = [[0, 1, 0], [0, 2, 0]]
        >>> plot_routes(locations, routes, "output.html")
        
        Generated file can be opened in browser:
        - Click markers to see stop details
        - Hover over routes to see exact paths
        - Zoom in/out to explore
    
    Output File:
        - Format: HTML + JavaScript
        - Size: Typically 50-500 KB
        - Browser compatibility: All modern browsers
        - No internet required after generation (fully self-contained)
    
    Example Usage:
        >>> from visualization import plot_routes
        >>> locations = [...solver output...]
        >>> routes = [...solver output...]
        >>> plot_routes(locations, routes, "../outputs/routes_map.html")
        >>> # Now open outputs/routes_map.html in browser
    """
```

---

## Data Structures

### Location
```python
Location = Tuple[float, float]
# Example: (13.0827, 80.2707)
# Represents: (latitude, longitude)
```

### Route
```python
Route = List[int]
# Example: [0, 1, 3, 5, 0]
# Represents: Sequence of node indices (starts and ends at depot)
```

### TimeWindow
```python
TimeWindow = Tuple[int, int]
# Example: (480, 600)
# Represents: (start_time_minutes, end_time_minutes)
# 0 = 00:00 (midnight), 480 = 08:00 (8 AM), 1440 = 24:00 (midnight next day)
```

### Order
```python
class Order:
    order_id: int          # Unique identifier
    lat: float             # Latitude [-90, 90]
    lon: float             # Longitude [-180, 180]
    demand: int            # Units to deliver [0, vehicle_capacity]
    start_time: int        # Earliest delivery (minutes)
    end_time: int          # Latest delivery (minutes)
```

---

## Return Values

### Routes Return Format
```python
[
    [0, 1, 3, 4, 0],      # Vehicle 1 route
    [0, 2, 5, 0],         # Vehicle 2 route
    [0, 6, 0]             # Vehicle 3 route (single order)
]
```

**Interpretation:**
- Each inner list is one vehicle's route
- Starts at 0 (depot), ends at 0 (depot)
- Node numbers correspond to locations: 0=depot, 1-N=orders
- Order of nodes determines delivery sequence

### Distance Matrix Format
```python
[
    [0, 10, 20, 30],       # From depot to all nodes
    [10, 0, 15, 25],       # From node 1 to all nodes
    [20, 15, 0, 10],       # From node 2 to all nodes
    [30, 25, 10, 0]        # From node 3 to all nodes
]
```

**Interpretation:**
- matrix[i][j] = distance from node i to node j (km)
- Always symmetric: matrix[i][j] == matrix[j][i]
- Diagonal always 0: matrix[i][i] == 0

---

## Examples

### Example 1: Full End-to-End Usage

```python
import pandas as pd
import json
from distance import compute_distance_matrix
from optimizer import solve_vrp
from visualization import plot_routes

# Load config
with open("../config/config.json") as f:
    config = json.load(f)

# Load and validate data
df = pd.read_csv("../data/orders.csv")
validate_input(df, config["vehicle"]["capacities"], config["vehicle"]["count"])

# Prepare inputs
depot = (config["depot"]["lat"], config["depot"]["lon"])
locations = [depot] + list(zip(df["lat"], df["lon"]))
demands = [0] + df["demand"].tolist()
time_windows = [(config["time"]["depot_start"], config["time"]["depot_end"])] + \
               list(zip(df["start_time"], df["end_time"]))

# Compute distances
distance_matrix, duration_matrix = compute_distance_matrix(locations)

# Solve VRP
routes = solve_vrp(
    distance_matrix,
    duration_matrix,
    demands,
    vehicle_capacities=config["vehicle"]["capacities"],
    num_vehicles=config["vehicle"]["count"],
    time_windows=time_windows
)

# Visualize
plot_routes(locations, routes, "../outputs/routes_map.html")

# Print results
for i, route in enumerate(routes):
    dist = calculate_route_distance(route, distance_matrix)
    load = calculate_load(route, demands)
    print(f"Vehicle {i+1}: {route}, Distance: {dist:.2f} km, Load: {load}")
```

### Example 2: Custom Configuration

```python
# Modify configuration on-the-fly
config = {
    "depot": {"lat": 12.9716, "lon": 77.5946},  # Bangalore instead of Chennai
    "vehicle": {"capacities": [100, 100, 100, 100], "count": 4},  # 4 large trucks
    "solver": {"time_limit": 10},  # More optimization time
    "time": {"depot_start": 360, "depot_end": 1200}  # 6 AM - 8 PM
}

# Use in main pipeline
locations = [(config["depot"]["lat"], config["depot"]["lon"])] + ...
```

### Example 3: Batch Processing Multiple Scenarios

```python
scenarios = [
    {"name": "morning", "config_file": "config/morning.json"},
    {"name": "evening", "config_file": "config/evening.json"},
]

for scenario in scenarios:
    print(f"Processing {scenario['name']} scenario...")
    
    with open(scenario['config_file']) as f:
        config = json.load(f)
    
    # Run full pipeline
    df = pd.read_csv(f"../data/orders_{scenario['name']}.csv")
    # ... rest of pipeline ...
    
    plot_routes(locations, routes, f"../outputs/{scenario['name']}_map.html")
```

---

## Error Handling

### Graceful Degradation Pattern

The VRP solver implements graceful degradation:

```
Primary → Fallback → Result
OSRM API ──→ Haversine ──→ Always works (worse quality)
API calls ──→ Cached ──→ Always produces output
Real roads ──→ Straight → Map still useful
```

### Exception Handling Examples

```python
# Input validation errors (raised to caller)
try:
    validate_input(df, [50], 1)
except ValueError as e:
    print(f"Validation failed: {e}")

# API failures (gracefully degraded)
distance_matrix, duration_matrix = compute_distance_matrix(locations)
# If OSRM fails:
#   ✅ Falls back to Haversine automatically
#   ✅ No exception raised
#   ✅ Results still usable (less accurate)

# VRP solver failures (returns empty)
routes = solve_vrp(...)
if not routes:
    print("Warning: No solution found")
    # Handle empty routes
```

---

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| validate_input() | <100ms | Fast validation |
| compute_distance_matrix() | 1–3s | OSRM API call |
| solve_vrp() | 5s | Tunable optimization |
| plot_routes() | 1–2s | Folium generation |
| **Total** | ~10s | For 8 orders, 3 vehicles |

---

**Last Updated:** April 15, 2026 | **Version:** 3.0 API Reference
