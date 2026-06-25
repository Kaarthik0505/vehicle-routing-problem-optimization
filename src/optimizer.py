from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def solve_vrp(distance_matrix, duration_matrix, demands, vehicle_capacities, num_vehicles, time_windows):
    
    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix), num_vehicles, 0
    )
    
    routing = pywrapcp.RoutingModel(manager)

    # Distance callback
    # ---------------- DISTANCE CALLBACK (COST) ---------------- #
    def distance_callback(from_index, to_index):
        return int(distance_matrix[
            manager.IndexToNode(from_index)
        ][
            manager.IndexToNode(to_index)
        ] * 1000)  # km → meters

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Capacity constraint
    def demand_callback(from_index):
        return demands[manager.IndexToNode(from_index)]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

    routing.AddDimensionWithVehicleCapacity(
    demand_callback_index,
    0,
    vehicle_capacities,
    True,
    "Capacity"
)
    # ---------------- TIME CONSTRAINT ---------------- #
    def time_callback(from_index, to_index):
        return int(duration_matrix[
            manager.IndexToNode(from_index)
        ][
            manager.IndexToNode(to_index)
        ])  # already in minutes

    time_callback_index = routing.RegisterTransitCallback(time_callback)

    routing.AddDimension(
        time_callback_index,
        100,    # waiting time
        1440,
        False,
        "Time"
    )

    time_dimension = routing.GetDimensionOrDie("Time")
    for node in range(len(time_windows)):
        index = manager.NodeToIndex(node)
        time_dimension.CumulVar(index).SetRange(
            time_windows[node][0],
            time_windows[node][1]
        )
    for vehicle_id in range(num_vehicles):
        start_index = routing.Start(vehicle_id)
        time_dimension.CumulVar(start_index).SetRange(
            time_windows[0][0],
            time_windows[0][0]
        )

    # Encourage vehicle usage
    for vehicle_id in range(num_vehicles):
        routing.SetFixedCostOfVehicle(5000, vehicle_id)

    # Search strategy
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()

    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )

    search_parameters.time_limit.seconds = 5

    solution = routing.SolveWithParameters(search_parameters)

    # Extract solution
    if solution:
        routes = []
        for vehicle_id in range(num_vehicles):
            index = routing.Start(vehicle_id)
            route = []
            
            while not routing.IsEnd(index):
                route.append(manager.IndexToNode(index))
                index = solution.Value(routing.NextVar(index))
            
            route.append(manager.IndexToNode(index))
            routes.append(route)

        return routes
    else:
        print("❌ No solution found! Check constraints.")
        return []