import folium
import requests

def get_osrm_route(coords):

    base_url = "http://router.project-osrm.org/route/v1/driving/"
    coord_str = ";".join([f"{lon},{lat}" for lat, lon in coords])
    url = base_url + coord_str + "?overview=full&geometries=geojson"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            raise Exception("OSRM route API failed")

        data = response.json()

        route = data["routes"][0]["geometry"]["coordinates"]

        # Convert (lon, lat) → (lat, lon)
        return [(lat, lon) for lon, lat in route]

    except Exception as e:
        print("⚠️ OSRM route failed, using straight lines...")
        print("Error: OSRM unavailable (offline mode)")

        # FALLBACK → straight line path
        return coords


def plot_routes(locations, routes, output_file="routes_map.html"):
    
    depot = locations[0]
    
    m = folium.Map(
        location=depot,
        zoom_start=13,
        tiles="OpenStreetMap"   # better for roads
    )
    folium.Marker(
        location=depot,
        popup="Depot",
        icon=folium.Icon(color="black", icon="home")
    ).add_to(m)

    colors = ["red", "blue", "green", "purple", "orange"]

    for i, route in enumerate(routes):
        route_coords = [locations[node] for node in route]

        # 🔥 Get REAL road path
        road_path = get_osrm_route(route_coords)

        # Add markers
        for j, node in enumerate(route):
            folium.Marker(
                location=locations[node],
                popup=f"Stop {node}<br>Vehicle {i+1}",
                icon=folium.Icon(color=colors[i % len(colors)])
            ).add_to(m)

        # 🔥 Draw REAL road route
        folium.PolyLine(
            road_path,
            color=colors[i % len(colors)],
            weight=5,
            opacity=0.8
        ).add_to(m)

    m.save(output_file)