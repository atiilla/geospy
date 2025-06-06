#!/usr/bin/env python3
"""
Simple example showing how to use GeoSpy as a library
"""

from geospyer import GeoSpy
import os 
import pathlib
import json
import sys

# Initialize GeoSpy with environment variable
try:
    geospy = GeoSpy()  # Uses GEMINI_API_KEY from environment
except Exception as e:
    print(f"Error initializing GeoSpy: {e}")
    print("Please ensure GEMINI_API_KEY environment variable is set")
    sys.exit(1)

# Analyze a local image with path validation
image_path = os.path.join(pathlib.Path(__file__).parent.parent, "kule.jpg")

# Validate image path
image_path = os.path.abspath(image_path)
if not os.path.exists(image_path):
    print(f"Error: Image file not found: {image_path}")
    sys.exit(1)
    
if not image_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
    print(f"Error: Unsupported image format: {image_path}")
    sys.exit(1)

try:
    result = geospy.locate(image_path=image_path)
except Exception as e:
    print(f"Error analyzing image: {e}")
    sys.exit(1)

# For this example, let's show how to access the data
if "error" in result:
    print(f"Error: {result['error']}")
    exit(1)

# Example 1: Save the raw JSON to a file
try:
    with open("geospy_result.json", "w") as f:
        json.dump(result, f, indent=2)
except (IOError, PermissionError) as e:
    print(f"Error saving result file: {e}")
    sys.exit(1)
    
# Example 2: Access specific data from the result
if "locations" in result and result["locations"]:
    # Get the first (most likely) location
    location = result["locations"][0]
    
    # Location details
    city = location.get("city", "Unknown")
    country = location.get("country", "Unknown")
    confidence = location.get("confidence", "Unknown")
    
    # Coordinates for Google Maps
    if "coordinates" in location:
        lat = location["coordinates"].get("latitude", 0)
        lng = location["coordinates"].get("longitude", 0)
        maps_url = f"https://www.google.com/maps?q={lat},{lng}"

# Example 3: Print summary for demonstration
if "locations" in result and result["locations"]:
    location = result["locations"][0]
    city = location.get("city", "Unknown")
    country = location.get("country", "Unknown")
    confidence = location.get("confidence", "Unknown")
    print(f"Location detected: {city}, {country} (confidence: {confidence})")
else:
    print("No location detected")

print("Analysis complete. Results saved to geospy_result.json")