import numpy as np
import requests

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c

def compute_distance_matrix(locations):

    base_url = "http://router.project-osrm.org/table/v1/driving/"
    coords = ";".join([f"{lon},{lat}" for lat, lon in locations])
    url = base_url + coords + "?annotations=distance,duration"

    try:
        response = requests.get(url, timeout=5)

        # Check HTTP status
        if response.status_code != 200:
            raise Exception("OSRM API error")

        data = response.json()

        # Validate response
        if "distances" not in data or "durations" not in data:
            raise Exception("Invalid OSRM response")

        distance_matrix = data["distances"]
        duration_matrix = data["durations"]

        # Convert units
        distance_matrix = [
            [d / 1000 if d is not None else 0 for d in row]
            for row in distance_matrix
        ]

        duration_matrix = [
            [t / 60 if t is not None else 0 for t in row]
            for row in duration_matrix
        ]

        print("✅ OSRM API used successfully")

        return distance_matrix, duration_matrix

    except Exception as e:
        print("⚠️ OSRM failed, switching to Haversine fallback...")
        print("Error: OSRM unavailable (offline mode)")

        # FALLBACK (VERY IMPORTANT)
        from distance import haversine

        n = len(locations)
        distance_matrix = [[0]*n for _ in range(n)]
        duration_matrix = [[0]*n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                dist = haversine(
                    locations[i][0], locations[i][1],
                    locations[j][0], locations[j][1]
                )
                distance_matrix[i][j] = dist
                duration_matrix[i][j] = dist * 2  # approx time

        return distance_matrix, duration_matrix