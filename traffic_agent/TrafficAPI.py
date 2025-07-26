import json
from datetime import datetime, timedelta, timezone
from google.protobuf.timestamp_pb2 import Timestamp
from google.maps.routing_v2 import RoutesClient
from google.maps.routing_v2.types import (
    ComputeRouteMatrixRequest,
    RouteMatrixOrigin,
    RouteMatrixDestination,
    Waypoint,
    Location,
    RouteTravelMode,
    RoutingPreference,
)

# Your dictionary of Bangalore hubs and their coordinates
bangalore_hub_coordinates = {
    "Silk Board Junction": {"lat": 12.9165, "lng": 77.6206},
    "Marathahalli Bridge": {"lat": 12.9569, "lng": 77.7011},
    "KR Puram Hanging Bridge": {"lat": 12.9950, "lng": 77.6800},
    "Hebbal Flyover": {"lat": 13.0400, "lng": 77.5900},
    "Tin Factory Junction": {"lat": 12.9915, "lng": 77.6698},
    "Majestic (Kempegowda Bus Station)": {"lat": 12.9800, "lng": 77.5700},
    "Central Silk Board": {"lat": 12.9176, "lng": 77.6253},
    "Electronic City Phase 1": {"lat": 12.8400, "lng": 77.6600},
    "Whitefield (ITPL)": {"lat": 12.9900, "lng": 77.7400},
    "Manyata Tech Park": {"lat": 13.0400, "lng": 77.6200},
    "Outer Ring Road (ORR)": {"lat": 12.9288, "lng": 77.6754},
    "Koramangala (Inner Ring Road)": {"lat": 12.9300, "lng": 77.6200},
    "Indiranagar (100 Feet Road)": {"lat": 12.9699, "lng": 77.6499},
    "MG Road": {"lat": 12.9753, "lng": 77.6049},
    "Jayanagar 4th Block": {"lat": 12.9300, "lng": 77.5800},
    "Malleshwaram 8th Cross": {"lat": 13.0000, "lng": 77.5700},
    "HSR Layout": {"lat": 12.9121, "lng": 77.6446},
    "BTM Layout": {"lat": 12.9200, "lng": 77.6100},
    "Sarjapur Road": {"lat": 12.9245, "lng": 77.6764}
}

def get_traffic_matrix_json(departure_time: datetime):
    """
    Gets traffic data and returns a pre-processed list of hubs with their
    average delay percentage.
    """
    with RoutesClient() as client:
        # ... (API request setup remains the same) ...
        origins, destinations, hub_names = [], [], list(bangalore_hub_coordinates.keys())
        for hub_name in hub_names:
            coords = bangalore_hub_coordinates[hub_name]
            waypoint = Waypoint(location=Location(lat_lng={"latitude": coords["lat"], "longitude": coords["lng"]}))
            origins.append(RouteMatrixOrigin(waypoint=waypoint))
            destinations.append(RouteMatrixDestination(waypoint=waypoint))

        departure_timestamp = Timestamp()
        departure_timestamp.FromDatetime(departure_time)

        request = ComputeRouteMatrixRequest(
            origins=origins,
            destinations=destinations,
            travel_mode=RouteTravelMode.DRIVE,
            routing_preference=RoutingPreference.TRAFFIC_AWARE,
            departure_time=departure_timestamp,
        )
        field_mask = "origin_index,destination_index,duration,static_duration,status"
        
        # --- Step 1: Gather all raw, delayed routes ---
        delayed_routes = []
        for element in client.compute_route_matrix(request=request, metadata=[('x-goog-fieldmask', field_mask)]):
            if element.status.code == 0:
                static_duration_minutes = element.static_duration.seconds / 60
                if static_duration_minutes > 0:
                    delay_percent = ((element.duration.seconds / 60) - static_duration_minutes) / static_duration_minutes * 100
                    if delay_percent > 0:
                        delayed_routes.append({
                            "origin_name": hub_names[element.origin_index],
                            "delay_percent": delay_percent
                        })
        
        # --- Step 2: Aggregate the raw data to calculate averages ---
        hub_delay_data = {}
        for route in delayed_routes:
            name = route["origin_name"]
            if name not in hub_delay_data:
                hub_delay_data[name] = {"total_delay": 0, "route_count": 0}
            hub_delay_data[name]["total_delay"] += route["delay_percent"]
            hub_delay_data[name]["route_count"] += 1
            
        # --- Step 3: Format the final, clean output ---
        final_hub_averages = []
        for name, data in hub_delay_data.items():
            average_delay = data["total_delay"] / data["route_count"]
            final_hub_averages.append({
                "hub_name": name,
                "coords": bangalore_hub_coordinates[name],
                "average_delay_percent": round(average_delay, 2)
            })
            
        return final_hub_averages


# To test directly
if __name__ == "__main__":
    now_utc = datetime.now(timezone.utc)
    future_date = now_utc + timedelta(days=3)
    future_departure_time = future_date.replace(hour=9, minute=0, second=0, microsecond=0)

    # The function now returns the aggregated data directly
    hub_averages_json = get_traffic_matrix_json(future_departure_time)

    # Print the pre-calculated hub averages
    print(json.dumps(hub_averages_json, separators=(',',':')))