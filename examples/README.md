# GeoSpy Library Examples

This directory contains simple examples showing how to use GeoSpy as a library.

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your Gemini API key:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
   On Windows:
   ```bash
   set GEMINI_API_KEY=your-api-key-here
   ```

## Library Usage

GeoSpy returns a JSON object that you can use in your application. Here's how to use it:

```python
from geospyer import GeoSpy

# Initialize
geospy = GeoSpy()  # Uses GEMINI_API_KEY from environment

# Analyze an image and get the result JSON
result = geospy.locate(image_path="your_image.jpg")

# The result is a JSON object you can work with
if "error" in result:
    # Handle errors
    print(f"Error: {result['error']}")
else:
    # Work with the data
    locations = result.get("locations", [])
    if locations:
        top_location = locations[0]
        print(f"Location: {top_location.get('city')}, {top_location.get('country')}")
```

### Accessing the JSON Data

The result object contains these main sections:

1. `interpretation`: Analysis of the image
2. `locations`: Array of possible locations, ordered by confidence

Example of accessing location data:

```python
# Get coordinates for Google Maps
if "locations" in result and result["locations"]:
    location = result["locations"][0]
    
    if "coordinates" in location:
        lat = location["coordinates"].get("latitude")
        lng = location["coordinates"].get("longitude")
        maps_url = f"https://www.google.com/maps?q={lat},{lng}"
```

### Saving to a File

You can easily save the results to a JSON file:

```python
import json

with open("result.json", "w") as f:
    json.dump(result, f, indent=2)
```

### Run the Example

```bash
python library_usage.py
```

This will analyze an image, save the results to `geospy_result.json`, and print a summary to the console.

## Examples

### Basic Library Usage

The `library_usage.py` file shows how to safely use GeoSpy with proper error handling:

```python
from geospyer import GeoSpy
import os
import sys

# Initialize with error handling
try:
    geospy = GeoSpy()  # Uses GEMINI_API_KEY from environment
except Exception as e:
    print(f"Error initializing GeoSpy: {e}")
    sys.exit(1)

# Validate and analyze an image
image_path = os.path.abspath("your_image.jpg")
if not os.path.exists(image_path):
    print("Error: Image file not found")
    sys.exit(1)

try:
    result = geospy.locate(image_path=image_path)
except Exception as e:
    print(f"Error analyzing image: {e}")
    sys.exit(1)
```

Run the example with:
```bash
python library_usage.py
```


## Using in Your Projects

To use GeoSpy in your own projects:

1. Install the package:
   ```bash
   pip install geospyer
   ```

2. Import and initialize:
   ```python
   from geospyer import GeoSpy
   
   # Always use environment variable for security
   geospy = GeoSpy()  # Uses GEMINI_API_KEY from environment
   ```

3. Analyze images:
   ```python
   results = geospy.locate(
       image_path="path/to/image.jpg",
       context_info="Optional context",
       location_guess="Optional guess"
   )
   ``` 