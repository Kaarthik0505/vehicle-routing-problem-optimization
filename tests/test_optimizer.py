from optimizer import solve_vrp

def test_vrp_solution_exists():
    distance_matrix = [
        [0, 5, 10],
        [5, 0, 6],
        [10, 6, 0]
    ]

    duration_matrix = distance_matrix

    demands = [0, 10, 15]

    vehicle_capacities = [30]
    num_vehicles = 1

    time_windows = [
        (0, 1000),
        (0, 1000),
        (0, 1000)
    ]

    routes = solve_vrp(
        distance_matrix,
        duration_matrix,
        demands,
        vehicle_capacities,
        num_vehicles,
        time_windows
    )

    assert len(routes) > 0
    assert routes[0][0] == 0  # starts at depot