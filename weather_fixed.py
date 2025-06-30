import os
import sys
import asyncio
from typing import Dict, Any, List
import json

# Standard MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import mcp.server.stdio

from dotenv import load_dotenv
import aiohttp
from aiohttp import ClientSession, ClientTimeout

# ─── Config & Init ─────────────────────────────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("OWM_API_KEY")
if not API_KEY:
    print("ERROR: OWM_API_KEY environment variable is not set", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://api.openweathermap.org/data/2.5"

# Create MCP server
server = Server("weather-server")

# ─── HTTP Helper ────────────────────────────────────────────────────────────────
async def fetch_json(url: str, params: Dict[str, Any]) -> Any:
    timeout = ClientTimeout(total=30)  # Kurangi timeout
    try:
        async with ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    print(f"ERROR: {url} → {resp.status}: {error_text}", file=sys.stderr)
                    raise Exception(f"API Error {resp.status}: {error_text}")
                
                data = await resp.json()
                return data
    except Exception as e:
        print(f"ERROR in fetch_json: {e}", file=sys.stderr)
        raise

# ─── Core Weather Functions ────────────────────────────────────────────────────────────
async def get_current_weather_data(city: str) -> Dict[str, Any]:
    """Get current weather for a city"""
    url = f"{BASE_URL}/weather"
    params = {"q": city, "units": "metric", "appid": API_KEY}
    
    try:
        data = await fetch_json(url, params)
        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "weather": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data.get("wind", {}).get("speed", 0),
            "visibility": data.get("visibility", 0) / 1000,  # Convert to km
        }
    except Exception as e:
        print(f"Error getting current weather: {e}", file=sys.stderr)
        raise

async def get_forecast_data(city: str) -> Dict[str, Any]:
    """Get 5-day forecast for a city"""
    url = f"{BASE_URL}/forecast"
    params = {"q": city, "units": "metric", "appid": API_KEY}
    
    try:
        data = await fetch_json(url, params)
        return {
            "city": data["city"]["name"],
            "country": data["city"]["country"],
            "forecast": [
                {
                    "datetime": item["dt_txt"],
                    "temperature": item["main"]["temp"],
                    "weather": item["weather"][0]["description"],
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item.get("wind", {}).get("speed", 0),
                }
                for item in data["list"][:20]  # Limit to first 20 entries
            ]
        }
    except Exception as e:
        print(f"Error getting forecast: {e}", file=sys.stderr)
        raise

# ─── MCP Tool Definitions ────────────────────────────────────────────────────────────
@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_current_weather",
            description="Get current weather information for a specific city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city to get weather for",
                        "default": "Jakarta"
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="get_weather_forecast",
            description="Get 5-day weather forecast for a specific city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city to get forecast for",
                        "default": "Jakarta"
                    }
                },
                "required": ["city"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    
    if name == "get_current_weather":
        city = arguments.get("city", "Jakarta")
        try:
            print(f"Getting current weather for: {city}", file=sys.stderr)
            weather_data = await get_current_weather_data(city)
            
            # Format response
            result = f"""Current Weather in {weather_data['city']}, {weather_data['country']}:
• Temperature: {weather_data['temperature']}°C (feels like {weather_data['feels_like']}°C)
• Condition: {weather_data['weather'].title()}
• Humidity: {weather_data['humidity']}%
• Pressure: {weather_data['pressure']} hPa
• Wind Speed: {weather_data['wind_speed']} m/s
• Visibility: {weather_data['visibility']} km"""
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            error_msg = f"Error getting weather data for {city}: {str(e)}"
            print(error_msg, file=sys.stderr)
            return [TextContent(type="text", text=error_msg)]
    
    elif name == "get_weather_forecast":
        city = arguments.get("city", "Jakarta")
        try:
            print(f"Getting forecast for: {city}", file=sys.stderr)
            forecast_data = await get_forecast_data(city)
            
            # Format response
            result = f"5-Day Weather Forecast for {forecast_data['city']}, {forecast_data['country']}:\n\n"
            
            for item in forecast_data['forecast']:
                result += f"• {item['datetime']}: {item['temperature']}°C, {item['weather'].title()}, Humidity: {item['humidity']}%\n"
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            error_msg = f"Error getting forecast data for {city}: {str(e)}"
            print(error_msg, file=sys.stderr)
            return [TextContent(type="text", text=error_msg)]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

# ─── Main Function ────────────────────────────────────────────────────────────
async def main():
    """Main function to run the MCP server"""
    print("Starting Weather MCP Server...", file=sys.stderr)
    
    # Test API key
    try:
        async with ClientSession() as session:
            test_url = f"{BASE_URL}/weather"
            test_params = {"q": "Jakarta", "appid": API_KEY}
            async with session.get(test_url, params=test_params) as resp:
                if resp.status != 200:
                    print(f"ERROR: API key test failed with status {resp.status}", file=sys.stderr)
                    sys.exit(1)
                print("API key test successful", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: API key test failed: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())