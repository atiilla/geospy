# geospy

![GitHub](https://img.shields.io/github/license/atiilla/geospy)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/atiilla/geospy)

Python tool using Google's Gemini API to uncover the location where photos were taken through AI-powered geo-location analysis.

[![asciicast](https://asciinema.org/a/722241.svg)](https://asciinema.org/a/722241)

## Installation

### Basic Installation

```bash
pip install geospyer
```

### Development Installation

For development with testing and security tools:

```bash
pip install geospyer[dev]
```

For testing only:

```bash
pip install geospyer[test]
```

## Usage

### Command Line Interface

```bash
geospyer --image path/to/your/image.jpg
```

#### Available Arguments

| Argument | Description |
|----------|-------------|
| `--image` | **Required.** Path to the image file or HTTPS URL to analyze |
| `--context` | Additional context information about the image |
| `--guess` | Your guess of where the image might have been taken |
| `--output` | Output file path to save the results (JSON format) |
| `--no-banner` | Disable banner display |

#### Examples

Basic usage:
```bash
geospyer --image vacation_photo.jpg
```

Using an HTTPS URL:
```bash
geospyer --image https://example.com/photo.jpg
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

Disable banner display:
```bash
geospyer --image vacation_photo.jpg --no-banner
```

### API Key Setup

**⚠️ Security Notice:** For security reasons, always use environment variables for API keys. Never hardcode API keys in your code or pass them as command-line arguments.

GeoSpy uses Google's Gemini API. Set up your API key:

1. **Recommended:** Set the API key as an environment variable:
   ```bash
   export GEMINI_API_KEY="your_key_here"
   ```
   On Windows:
   ```bash
   set GEMINI_API_KEY=your_key_here
   ```

2. The library will automatically use the `GEMINI_API_KEY` environment variable

Get your Gemini API key from [Google AI Studio](https://ai.google.dev/).

**Security Best Practices:**
- Never commit API keys to version control
- Use environment variables or secure credential management systems
- Regularly rotate your API keys
- Monitor API usage for unusual activity

### Python Library

```python
from geospyer import GeoSpy
import os

# Initialize GeoSpy (uses GEMINI_API_KEY environment variable)
try:
    geospy = GeoSpy()
except ValueError as e:
    print(f"Error: {e}")
    print("Please set GEMINI_API_KEY environment variable")
    exit(1)

# Analyze an image and get JSON result
try:
    result = geospy.locate(image_path="image.jpg")
except Exception as e:
    print(f"Error processing image: {e}")
    exit(1)

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
- Secure API key management via environment variables
- Input validation and security controls
- Generate Google Maps links based on image coordinates
- Provide confidence levels for location predictions
- Support for additional context and location guesses
- Export results to JSON
- Handles both local image files and HTTPS URLs with security validation
- Rate limiting and timeout controls
- Cross-platform color support with fallback
- Comprehensive error handling

## Response Format

The API returns a structured JSON response with:
- `interpretation`: Comprehensive analysis of the image
- `locations`: Array of possible locations with:
  - Country, state, and city information
  - Confidence level (High/Medium/Low)
  - Coordinates (latitude/longitude)
  - Detailed explanation of the reasoning

## Security Features

- **Input Validation:** All image paths and URLs are validated to prevent path traversal and SSRF attacks
- **Rate Limiting:** Built-in rate limiting (1 second minimum between requests) to prevent API abuse
- **SSL Verification:** All HTTPS requests verify SSL certificates
- **File Size Limits:** Image files are limited to 10MB to prevent memory exhaustion
- **Secure Headers:** Uses appropriate User-Agent identification instead of browser spoofing
- **Error Sanitization:** Error messages are sanitized to prevent information disclosure
- **Environment-Only API Keys:** API keys must be provided via environment variables
- **URL Restrictions:** Only HTTPS URLs are allowed, localhost and private IPs are blocked
- **File Type Validation:** Only supported image formats (.jpg, .jpeg, .png, .gif, .bmp, .webp) are allowed
- **Timeout Controls:** Configurable timeouts (default 30 seconds) for all network operations

## Disclaimer

**⚠️ Important Notice:**

GeoSpy is intended for **educational and research purposes only**. While it uses AI models to estimate the location of where an image was taken, its predictions are not guaranteed to be accurate. 

**Do NOT use this tool for:**
- Surveillance or stalking
- Law enforcement investigations
- Any activity that may infringe on personal privacy
- Any activity that violates laws or causes harm

**Security and Privacy:**
- Always obtain proper consent before analyzing images
- Be aware that image analysis may reveal sensitive location information
- Follow responsible disclosure practices
- Respect privacy laws and regulations in your jurisdiction

**Legal Responsibility:**
The author(s) and contributors are not responsible for any damages, legal issues, or consequences resulting from the use or misuse of this software. Use at your own risk and discretion.

Always comply with local, national, and international laws and regulations when using AI-based tools.


## Contributing

1. Fork the repository
2. Create a new branch (git checkout -b feature/new-feature).
3. Commit your changes (git commit -am 'Add new feature').
4. Push to the branch (git push origin feature/new-feature).
5. Create a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments