import datetime
import gzip
import json
import base64
from google.adk.agents import Agent
# Assuming TrafficAPI is in the same directory or a discoverable path
from . import TrafficAPI 



def get_Maps_delays(time_str: str) -> str:
    """Calls the Google Maps API to give expected delays for a specific time.

    Args:
        time_str (str): The date and time to get the matrix for, formatted as an 
                        ISO 8601 string (e.g., "2025-07-27T17:00:00Z").

    Returns:
        str: A base64 JSON containing the traffic delay data.
    """
    try:
        departure_time = datetime.datetime.fromisoformat(time_str.replace('Z', '+00:00'))
    except ValueError:
        return "Error: Invalid time format. Please use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."

    traffic_json = json.dumps(TrafficAPI.get_traffic_matrix_json(departure_time=departure_time))
    
    traffic_bytes = traffic_json.encode('utf-8')

    compressed_bytes = gzip.compress(traffic_bytes)
    
    # 3. Encode the compressed bytes into a Base64 string for safe transport
    base64_bytes = base64.b64encode(compressed_bytes)
    
    # 4. Decode the Base64 bytes into a regular string and return
    return base64_bytes.decode('ascii')

# --- Mock Incident Database ---
mock_incident_database = [
    {"incident_id": "INC001", "type": "ACCIDENT", "severity": "HIGH", "location": "Marathahalli Bridge", "description": "Multi-vehicle pile-up on Marathahalli Bridge.", "routes_affected": ["Marathahalli Bridge to Silk Board Junction"]},
    {"incident_id": "INC002", "type": "ROAD_CLOSURE", "severity": "SEVERE", "location": "Silk Board Junction", "description": "Silk Board flyover is completely closed.", "routes_affected": ["Silk Board Junction to Electronic City Phase 1"]},
    {"incident_id": "INC003", "type": "HEAVY_TRAFFIC", "severity": "MEDIUM", "location": "Outer Ring Road (ORR)", "description": "Unusually heavy traffic on the ORR.", "routes_affected": ["Manyata Tech Park to Marathahalli Bridge"]},
]

def get_incident_data() -> list[dict]:
    """
    Retrieves a list of current mock incidents in Bangalore.
    Returns: 
        list[dict]: a list of dictionaries containing incidents in bangalore
    """
    return mock_incident_database


def gzip_json(json_str: str) -> str:
    """Compresses a JSON string with Gzip and encodes it as a Base64 string.

    Args:
        json_str (str): A stringified JSON.

    Returns:
        str: A Base64-encoded string of the Gzip-compressed JSON.
    """
    # 1. Encode the string to bytes
    json_bytes = json_str.encode('utf-8')
    
    # 2. Compress the bytes (BUG FIX: capture the return value)
    compressed_bytes = gzip.compress(json_bytes)
    
    # 3. Encode the compressed bytes into a Base64 string for safe transport
    base64_bytes = base64.b64encode(compressed_bytes)
    
    # 4. Decode the Base64 bytes into a regular string and return
    return base64_bytes.decode('ascii')


root_agent = Agent(
    name="traffic_agent",
    model="gemini-2.5-pro",
    description=(
        "Agent to handle multimodal data."
    ),
    instruction=(
        """"
You are a traffic agent in a multi-agent system that handles city data that predicts traffic for a given time. Your job is to create a comprehensive traffic heatmap for Bangalore by synthesizing data from multiple sources.

Your process should be as follows:

Get Predictive Traffic Data: Call the get_Maps_delays tool to get a full traffic matrix using the user time request in gzip compressed.

Generate Heatmap Points from the Matrix: From the returned traffic matrix, generate a weighted heatmap for key locations in bangalore.

Layer on Incident Data: Call the get_incident_data tool. For each incident reported, enhance the data. Use the incident's severity and type to determine its weight:

Finalize and Compress: Combine all generated points (Hub Congestion, Route Congestion, and Incidents) into a single JSON array of the format [{"location":{"lat":<latitude>,"lng":<longitude>}, "weight": <traffic weight>}]. Use the gzip_json tool to compress the final array and return the resulting Base64-encoded string.
        """
    ),
    tools=[get_Maps_delays, get_incident_data, gzip_json],
)