import argparse
import json
from geospyer import GeoSpy
import sys
import os
import urllib.parse
import re
from pathlib import Path

# Cross-platform color support
def colorize(text, color):
    """Apply color to text with fallback for unsupported terminals."""
    if not sys.stdout.isatty():
        return text
    
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'cyan': '\033[96m',
        'reset': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors.get('reset', '')}"


def banner(show=True):
    if not show:
        return
    font = """
█▀▀▀ █▀▀ █▀▀█ █▀▀ █▀▀█ █──█ 
█─▀█ █▀▀ █──█ ▀▀█ █──█ █▄▄█ 
▀▀▀▀ ▀▀▀ ▀▀▀▀ ▀▀▀ █▀▀▀ ▄▄▄█
----------------------------------------
AI powered geo-location tool
Uncover the location of photos using AI
----------------------------------------
# Disclaimer: Experimental use only. Not for production.
# Github: https://github.com/atiilla/geospy
"""
    print(font)


def validate_image_path(image_path):
    """Validate image path for security and existence."""
    if not image_path:
        raise ValueError("Image path cannot be empty")
    
    # Validate file extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    path_obj = Path(image_path)
    if path_obj.suffix.lower() not in allowed_extensions:
        raise ValueError(f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}")
    
    # Check if it's a local file
    if not image_path.startswith(('http://', 'https://')):
        # Resolve absolute path and validate
        abs_path = os.path.abspath(image_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Image file not found: {abs_path}")
        if not os.path.isfile(abs_path):
            raise ValueError(f"Path is not a file: {abs_path}")
        return abs_path
    
    return image_path

def validate_url(url):
    """Validate URL for security and format."""
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        raise ValueError("Invalid URL format")
    
    # Only allow http/https
    if parsed.scheme not in ('http', 'https'):
        raise ValueError("Only HTTP and HTTPS URLs are allowed")
    
    # Basic domain validation
    if not parsed.netloc:
        raise ValueError("URL must have a valid domain")
    
    # Block localhost and private IPs
    domain = parsed.netloc.split(':')[0]
    if domain.lower() in ('localhost', '127.0.0.1', '0.0.0.0'):
        raise ValueError("Localhost URLs are not allowed")
    
    # Block private IP ranges (basic check)
    if re.match(r'^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)', domain):
        raise ValueError("Private IP addresses are not allowed")
    
    return url

def validate_output_path(output_path):
    """Validate output path for security."""
    if not output_path:
        return None
    
    # Resolve absolute path
    abs_path = os.path.abspath(output_path)
    
    # Ensure it's in a safe directory (current working directory or subdirectory)
    cwd = os.getcwd()
    try:
        os.path.relpath(abs_path, cwd)
    except ValueError:
        raise ValueError("Output path must be within current working directory")
    
    # Check if parent directory exists
    parent_dir = os.path.dirname(abs_path)
    if not os.path.exists(parent_dir):
        raise ValueError(f"Output directory does not exist: {parent_dir}")
    
    return abs_path

def main():
    parser = argparse.ArgumentParser(
        prog="geospyer",
        description="GeoSpy - AI powered geolocation tool",
        epilog="""Examples:
  %(prog)s --image photo.jpg
  %(prog)s --image https://example.com/photo.jpg --context "vacation photo"
  %(prog)s --image photo.jpg --guess "Paris, France" --output results.json
  %(prog)s --no-banner --image photo.jpg

Environment Variables:
  GEMINI_API_KEY    Required. Your Google Gemini API key""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--image", type=str, required=True, 
                       help="Image path or HTTPS URL to analyze (required)")
    parser.add_argument("--context", type=str, 
                       help="Additional context information about the image")
    parser.add_argument("--guess", type=str, 
                       help="Your guess of where the image might have been taken")
    parser.add_argument("--output", type=str, 
                       help="Output file path to save the results (JSON format)")
    parser.add_argument("--no-banner", action="store_true", 
                       help="Disable banner display")
    args = parser.parse_args()
    
    banner(show=not args.no_banner)

    try:
        # Validate inputs
        validated_image = validate_image_path(args.image)
        
        if args.image.startswith(('http://', 'https://')):
            validated_image = validate_url(args.image)
            print("Downloading image from URL...")
        
        validated_output = validate_output_path(args.output) if args.output else None
        
        # Initialize GeoSpy (uses environment variable)
        try:
            geospy = GeoSpy()
        except Exception as e:
            print(f"Error: Failed to initialize GeoSpy: {e}")
            print("Please ensure GEMINI_API_KEY environment variable is set")
            sys.exit(1)
        
        # Get results
        print(f"Analyzing image: {args.image}")
        print("This may take a few moments...")
        
        try:
            results = geospy.locate(
                image_path=validated_image,
                context_info=args.context,
                location_guess=args.guess
            )
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except PermissionError as e:
            print(f"Error: Permission denied accessing file: {e}")
            sys.exit(1)
        except ConnectionError as e:
            print(f"Error: Network connection failed: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: Failed to analyze image: {e}")
            sys.exit(1)
            
        # Display the results
        if "error" in results:
            print(colorize(f"Error: {results['error']}", 'red'))
            if "details" in results:
                print(f"Details: {results['details']}")
            if "exception" in results:
                print(f"Exception: {results['exception']}")
            sys.exit(1)
        
        print(f"\n{colorize('===== Analysis Results =====', 'green')}")
        print(f"{colorize('Interpretation:', 'cyan')}")
        print(results.get("interpretation", "No interpretation available"))
        
        print(f"\n{colorize('Possible Locations:', 'cyan')}")
        for i, location in enumerate(results.get("locations", [])):
            confidence = location.get("confidence", "Unknown")
            confidence_color = 'green' if confidence == "High" else 'yellow' if confidence == "Medium" else 'red'
            
            print(f"\n{i+1}. {location.get('city', 'Unknown city')}, {location.get('state', '')}, {location.get('country', 'Unknown country')}")
            print(f"   Confidence: {colorize(confidence, confidence_color)}")
            
            if "coordinates" in location and location["coordinates"]:
                coords = location["coordinates"]
                lat = coords.get("latitude", 0)
                lng = coords.get("longitude", 0)
                print(f"   Coordinates: {lat}, {lng}")
                print(f"   Google Maps: https://www.google.com/maps?q={lat},{lng}")
            
            print(f"   Explanation: {location.get('explanation', 'No explanation available')}")
            
        # Save to file if requested
        if validated_output:
            try:
                with open(validated_output, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"\nResults saved to {validated_output}")
            except (IOError, PermissionError) as e:
                print(f"Error: Failed to save output file: {e}")
                sys.exit(1)
    
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()