# geospy

![GitHub](https://img.shields.io/github/license/atiilla/geospy)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/atiilla/geospy)

Python tool using Google's Gemini API to uncover the location where photos were taken through AI-powered geo-location analysis.

[![asciicast](https://asciinema.org/a/722241.svg)](https://asciinema.org/a/722241)

## Installation

```bash
pip install geospyer
```

## Usage

### Command Line Interface

```bash
geospyer --image path/to/your/image.jpg
```

#### Available Arguments

| Argument | Description |
|----------|-------------|
| `--image` | **Required.** Path to the image file or URL to analyze |
| `--context` | Additional context information about the image |
| `--guess` | Your guess of where the image might have been taken |
| `--output` | Output file path to save the results (JSON format) |
| `--api-key` | Custom Gemini API key |

#### Examples

Basic usage:
```bash
geospyer --image vacation_photo.jpg
```

With additional context:
```bash
geospyer --image vacation_photo.jpg --context "Taken during summer vacation in 2023"
```

With location guess:
```bash
geospyer --image vacation_photo.jpg --guess "Mediterranean coast"
```

Saving results to a file:
```bash
geospyer --image vacation_photo.jpg --output results.json
```

Using a custom API key:
```bash
geospyer --image vacation_photo.jpg --api-key "your-api-key-here"
```

### API Key Setup

GeoSpy uses Google's Gemini API. You can:
1. Set the API key as an environment variable: `GEMINI_API_KEY=your_key_here`
2. Pass the API key directly when initializing: `GeoSpy(api_key="your_key_here")`
3. Use the `--api-key` parameter in the command line

Get your Gemini API key from [Google AI Studio](https://ai.google.dev/).

### Python Library

```python
from geospyer import GeoSpy

# Initialize GeoSpy
geospy = GeoSpy()

# Analyze an image and get JSON result
result = geospy.locate(image_path="image.jpg")

# Work with the JSON data
if "error" in result:
    print(f"Error: {result['error']}")
else:
    # Access the first location
    if "locations" in result and result["locations"]:
        location = result["locations"][0]
        print(f"Location: {location['city']}, {location['country']}")
        
        # Get Google Maps URL
        if "coordinates" in location:
            lat = location["coordinates"]["latitude"]
            lng = location["coordinates"]["longitude"]
            maps_url = f"https://www.google.com/maps?q={lat},{lng}"
```

See the [examples directory](./examples) for more detailed usage examples.

## Features

- AI-powered geolocation of images using Google's Gemini API
- Generate Google Maps links based on image coordinates
- Provide confidence levels for location predictions
- Support for additional context and location guesses
- Export results to JSON
- Handles both local image files and image URLs

## Response Format

The API returns a structured JSON response with:
- `interpretation`: Comprehensive analysis of the image
- `locations`: Array of possible locations with:
  - Country, state, and city information
  - Confidence level (High/Medium/Low)
  - Coordinates (latitude/longitude)
  - Detailed explanation of the reasoning

## Disclaimer

This tool is for experimental use only. The author is not responsible for the consequences of using this application.

## Contributing

1. Fork the repository
2. Create a new branch (git checkout -b feature/new-feature).
3. Commit your changes (git commit -am 'Add new feature').
4. Push to the branch (git push origin feature/new-feature).
5. Create a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments