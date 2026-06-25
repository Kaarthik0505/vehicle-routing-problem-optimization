import pandas as pd
import json
from distance import compute_distance_matrix
from optimizer import solve_vrp
from visualization import plot_routes

# ---------------- INPUT VALIDATION ---------------- #
def validate_input(df, vehicle_capacities, num_vehicles):
    required_columns = ["order_id", "lat", "lon", "demand", "start_time", "end_time"]

    # ---------------- BASIC CHECKS ---------------- #

    # Missing columns
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    # Null values
    if df.isnull().values.any():
        raise ValueError("Dataset contains missing (NaN) values")

    # Latitude/Longitude range
    if not df["lat"].between(-90, 90).all():
        raise ValueError("Invalid latitude values")

    if not df["lon"].between(-180, 180).all():
        raise ValueError("Invalid longitude values")

    # Demand check
    if (df["demand"] < 0).any():
        raise ValueError("Demand cannot be negative")

    # Time window logic
    if (df["start_time"] > df["end_time"]).any():
        raise ValueError("Start time cannot be greater than end time")

    # ---------------- ADVANCED CHECKS ---------------- #

    # Duplicate order IDs
    if df["order_id"].duplicated().any():
        raise ValueError("Duplicate order_id found")

    # Capacity feasibility check
    total_demand = df["demand"].sum()
    total_capacity = sum(vehicle_capacities)

    if total_demand > total_capacity:
        raise ValueError(
            f"Total demand ({total_demand}) exceeds fleet capacity ({total_capacity})"
        )

    # Individual demand vs vehicle capacity
    if (df["demand"] > max(vehicle_capacities)).any():
        raise ValueError("Single order demand exceeds vehicle capacity")

    # Time window sanity (optional stricter rule)
    if (df["start_time"] < 0).any() or (df["end_time"] > 1440).any():
        raise ValueError("Time windows must be within 0–1440 minutes")

    print("✅ Input data validation passed (Advanced)")

def main():
    # Load configuration
    with open("../config/config.json", "r") as f:
        config = json.load(f)
    vehicle_capacities = config["vehicle"]["capacities"]
    num_vehicles = config["vehicle"]["count"]

    # Load data
    df = pd.read_csv("../data/orders.csv")
    # Validate input
    validate_input(df, vehicle_capacities, num_vehicles)

    # Depot (Chennai example)
    depot = (config["depot"]["lat"], config["depot"]["lon"])

    # Locations (depot + deliveries)
    locations = [depot] + list(zip(df["lat"], df["lon"]))

    # Demands (0 for depot)
    demands = [0] + df["demand"].tolist()

    # NEW: Time windows
    time_windows = [
        (config["time"]["depot_start"], config["time"]["depot_end"])
    ] + list(zip(df["start_time"], df["end_time"]))

    # Compute distance matrix
    distance_matrix, duration_matrix = compute_distance_matrix(locations)

    # Solve VRP
    routes = solve_vrp(
        distance_matrix,
        duration_matrix,
        demands,
        vehicle_capacities=vehicle_capacities,
        num_vehicles=num_vehicles,
        time_windows=time_windows
    )

    # ---------------- HELPER FUNCTIONS ---------------- #

    def calculate_route_distance(route, distance_matrix):
        distance = 0
        for i in range(len(route) - 1):
            distance += distance_matrix[route[i]][route[i+1]]
        return distance

    def calculate_eta(route, duration_matrix, time_windows):
        current_time = time_windows[0][0]
        eta_list = []

        for i in range(len(route)):
            node = route[i]

            if i == 0:
                current_time = max(current_time, time_windows[node][0])
            else:
                prev = route[i-1]
                travel_time = duration_matrix[prev][node]
                current_time += travel_time

                # Respect time window (wait if early)
                start, end = time_windows[node]
                if current_time < start:
                    current_time = start

            eta_list.append(int(current_time))

        return eta_list

    def format_time(minutes):
        hours = minutes // 60
        mins = minutes % 60
        return f"{int(hours):02d}:{int(mins):02d}"

    def calculate_load(route, demands):
        return sum([demands[node] for node in route])

    def naive_multi_vehicle(locations, num_vehicles):
        routes = []
        nodes = list(range(1, len(locations)))

        # Bad assignment: alternate nodes
        for i in range(num_vehicles):
            route_nodes = nodes[i::num_vehicles]
            route = [0] + route_nodes + [0]
            routes.append(route)

        return routes
    # ---------------- PROCESSING ---------------- #

    order_ids = ["Depot"] + df["order_id"].astype(str).tolist()

    # Optimized results
    optimized_results = []
    total_distance = 0

    for i, route in enumerate(routes):
        eta = calculate_eta(route, duration_matrix, time_windows)
        readable_route = [order_ids[node] for node in route]
        route_distance = calculate_route_distance(route, distance_matrix)
        total_distance += route_distance

        load = calculate_load(route, demands)
        optimized_results.append((i+1, readable_route, route_distance, eta, load))

    # Naive results
    naive_routes = naive_multi_vehicle(locations, num_vehicles)

    naive_results = []
    naive_total_distance = 0

    for i, route in enumerate(naive_routes):
        readable_route = [order_ids[node] for node in route]
        route_distance = calculate_route_distance(route, distance_matrix)
        naive_total_distance += route_distance

        naive_results.append((i+1, readable_route, route_distance))

    # ---------------- OUTPUT ---------------- #

    print("\n========== OPTIMIZED ROUTES ==========")

    for vehicle, route, dist, eta, load in optimized_results:
        print(f"\nOptimized Vehicle {vehicle}:")

        for i in range(len(route)):
            node = route[i]
            time = eta[i]
            print(f"{node} (ETA: {format_time(time)})", end="")

            if i != len(route) - 1:
                print(" -> ", end="")

        print(" -> END")
        print(f"Distance: {dist:.2f} km")
        capacity = vehicle_capacities[vehicle-1]
        print(f"Load: {load} / {capacity}")

    print("\n========== NAIVE ROUTES ==========")

    for vehicle, route, dist in naive_results:
        print(f"\nNaive Vehicle {vehicle}:")
        print(" -> ".join(route))
        print(f"Distance: {dist:.2f} km")

    # Comparison
    improvement = ((naive_total_distance - total_distance) / naive_total_distance) * 100

    print("\n========== COMPARISON ==========")
    print(f"Optimized Total Distance: {total_distance:.2f} km")
    print(f"Naive Total Distance: {naive_total_distance:.2f} km")
    print(f"Improvement: {improvement:.2f}%")
    if improvement < 0:
        print("\n⚠️ Note: Naive solution does not consider capacity/time constraints, so it may be infeasible. Optimized solution is valid,constraint-aware and realistic")

    # ---------------- VISUALIZATION ---------------- #

    plot_routes(locations, routes, "../outputs/routes_map.html")
    print("\nMap saved to outputs/routes_map.html")

    print("\n========== PERFORMANCE METRICS ==========")

    used_vehicles = sum(1 for r in optimized_results if r[2] > 0)
    print(f"Total Vehicles Used: {used_vehicles}")
    print(f"Idle Vehicles: {len(routes) - used_vehicles}")
    print(f"Average Distance per Vehicle: {total_distance/len(routes):.2f} km")

    max_route = max([r[2] for r in optimized_results])
    print(f"Max Route Distance: {max_route:.2f} km")

if __name__ == "__main__":
    main()