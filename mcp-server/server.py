# server.py
from typing import Dict, Optional, List
from os import getenv
import httpx
import logging
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Create an MCP server
mcp = FastMCP("Trip Planning Tools - MCP Server")


# Add a tool
# @mcp.tool()
# def greet(user_name: str = "there") -> str:
#     """Greet the User. Always use me to start the conversation."""
#     return f"Hello {user_name}! How can I help you today?"


# Mock Database for User Preferences
class UserPreferencesDB:
    def __init__(self):
        self.data = {
            "renjith": {
                "interests": ["beaches", "natural", "museums"]
            },
            "bigblue": {
                "interests": ["cultural", "sculptures"]
            }
        }

    def get_preferences(self, user_name: str) -> Optional[Dict]:
        return self.data.get(user_name)

    def set_preferences(self, user_name: str, preferences: Dict):
        self.data[user_name] = preferences


@mcp.tool()
def get_travel_preferences(user_name: str) -> dict:
    """Get travel preferences of a User. Use me always to personlize a trip plan."""
    return UserPreferencesDB().get_preferences(user_name=user_name.lower())


@mcp.tool()
async def get_attractions(location_name: str, user_interests: str = None) -> List[Dict]:
    """Get travel attractions for a given travel location and provided user interests.
    location_name: city name, area name etc
    user_interests: comma separated list of interests (eg: cultural,beaches etc)"""

    # Obtain free API key from https://dev.opentripmap.org/login
    OPEN_TRIPMAP_API_KEY = getenv("OPEN_TRIPMAP_API_KEY")
    
    if not OPEN_TRIPMAP_API_KEY:
        return [{"error": "API key not configured"}]

    geocoding_url = "https://api.opentripmap.com/0.1/en/places/geoname"
    geocoding_params = {
        'name': location_name,
        'apikey': OPEN_TRIPMAP_API_KEY
    }

    try:
        async with httpx.AsyncClient() as client:
            geo_response = await client.get(geocoding_url, params=geocoding_params)
            geo_data = geo_response.json()

            logging.debug(f"Geocoding response for {location_name}: {geo_data}")

            if not geo_data or 'lat' not in geo_data or 'lon' not in geo_data:
                return [{"error": "Location not found"}]

            lat, lon = geo_data['lat'], geo_data['lon']

            # if interests is none use default
            if user_interests is None:
                user_interests = 'tourist_attractions,museums,theatres,architecture'

            attractions_url = "https://api.opentripmap.com/0.1/en/places/radius"
            attractions_params = {
                'radius': 10000, # radius in meters
                'lat': lat,
                'lon': lon,
                'kinds': user_interests,
                'limit': 30,
                'apikey': OPEN_TRIPMAP_API_KEY
            }

            attractions_response = await client.get(attractions_url, params=attractions_params)
            attractions_data = attractions_response.json()

            formatted_attractions = []
            for attraction in attractions_data.get('features', []):
                properties = attraction.get('properties', {})
                formatted_attractions.append({
                    'name': properties.get('name', 'Unknown'),
                    'type': properties.get('kinds', '').replace('_', ' ').title(),
                    'coordinates': attraction.get('geometry', {}).get('coordinates', [])
                })

            return formatted_attractions

    except Exception as e:
        return [{"error": f"Failed to fetch attractions: {str(e)}"}]
