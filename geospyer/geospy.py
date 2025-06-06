import json
import requests
import base64
import os
import re
import time
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urlparse

class GeoSpy:
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, max_file_size: int = 10 * 1024 * 1024):
        # Get API key from parameter or environment
        self.gemini_api_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        # Validate API key is present
        if not self.gemini_api_key:
            raise ValueError(
                "Gemini API key is required. Please provide it via the 'api_key' parameter "
                "or set the 'GEMINI_API_KEY' environment variable."
            )
        
        # Validate API key format (basic check)
        if not re.match(r'^[A-Za-z0-9_-]+$', self.gemini_api_key):
            raise ValueError("Invalid API key format")
            
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash-lite-001:generateContent"
        self.timeout = timeout
        self.max_file_size = max_file_size
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
        
    def _validate_image_path(self, image_path: str) -> str:
        """Validate and sanitize image path for security."""
        if not image_path or not isinstance(image_path, str):
            raise ValueError("Image path must be a non-empty string")
        
        # Check if it's a URL
        parsed_url = urlparse(image_path)
        if parsed_url.scheme in ('http', 'https'):
            # URL validation
            if not parsed_url.netloc:
                raise ValueError("Invalid URL: missing domain")
            
            # Block localhost and private IPs
            domain = parsed_url.netloc.split(':')[0].lower()
            if domain in ('localhost', '127.0.0.1', '0.0.0.0'):
                raise ValueError("Localhost URLs are not allowed")
            
            # Block private IP ranges
            if re.match(r'^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)', domain):
                raise ValueError("Private IP addresses are not allowed")
                
            return image_path
        else:
            # Local file validation
            try:
                # Resolve to absolute path
                abs_path = os.path.abspath(image_path)
                
                # Ensure file exists
                if not os.path.exists(abs_path):
                    raise FileNotFoundError(f"Image file not found: {abs_path}")
                
                # Ensure it's a file, not a directory
                if not os.path.isfile(abs_path):
                    raise ValueError(f"Path is not a file: {abs_path}")
                
                # Validate file extension
                allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
                if Path(abs_path).suffix.lower() not in allowed_extensions:
                    raise ValueError(f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}")
                
                # Check file size
                file_size = os.path.getsize(abs_path)
                if file_size > self.max_file_size:
                    raise ValueError(f"File too large: {file_size} bytes (max: {self.max_file_size} bytes)")
                
                return abs_path
            except (OSError, IOError) as e:
                raise ValueError(f"Invalid file path: {e}")
    
    def _detect_mime_type(self, image_path: str) -> str:
        """Detect MIME type of the image."""
        if image_path.startswith(('http://', 'https://')):
            # For URLs, try to guess from extension
            parsed_url = urlparse(image_path)
            path = parsed_url.path
            mime_type, _ = mimetypes.guess_type(path)
            return mime_type or "image/jpeg"
        else:
            # For local files, detect from file
            mime_type, _ = mimetypes.guess_type(image_path)
            return mime_type or "image/jpeg"
    
    def _rate_limit(self):
        """Implement basic rate limiting."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Convert an image file to base64 encoding.
        Supports both local files and URLs.
        
        Args:
            image_path: Path to the image file or URL
            
        Returns:
            Base64 encoded string of the image
            
        Raises:
            ValueError: If the image cannot be loaded or the URL is invalid
            FileNotFoundError: If the local image file doesn't exist
        """
        # Validate input
        validated_path = self._validate_image_path(image_path)
        # Check if the validated_path is a URL
        if validated_path.startswith(('http://', 'https://')):
            try:
                # Use proper headers and SSL verification
                headers = {
                    'User-Agent': 'GeoSpy/0.1.9 (https://github.com/atiilla/geospy)'
                }
                response = requests.get(
                    validated_path, 
                    timeout=self.timeout,
                    headers=headers,
                    verify=True,  # Verify SSL certificates
                    stream=True  # Stream download for large files
                )
                response.raise_for_status()
                
                # Check content length if available
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > self.max_file_size:
                    raise ValueError(f"Image too large: {content_length} bytes (max: {self.max_file_size} bytes)")
                
                # Read content with size limit
                content = b''
                for chunk in response.iter_content(chunk_size=8192):
                    if len(content) + len(chunk) > self.max_file_size:
                        raise ValueError(f"Image too large (max: {self.max_file_size} bytes)")
                    content += chunk
                
                return base64.b64encode(content).decode('utf-8')
                
            except requests.exceptions.SSLError as e:
                raise ValueError(f"SSL verification failed: {e}")
            except requests.exceptions.ConnectionError as e:
                raise ValueError(f"Failed to connect to URL. Please check your internet connection.")
            except requests.exceptions.HTTPError as e:
                raise ValueError(f"HTTP error when downloading image: {e}")
            except requests.exceptions.Timeout as e:
                raise ValueError(f"Request timed out when downloading image from URL")
            except requests.exceptions.RequestException as e:
                raise ValueError(f"Failed to download image from URL: {e}")
        else:
            # Local file
            try:
                with open(validated_path, "rb") as image_file:
                    content = image_file.read()
                    if len(content) > self.max_file_size:
                        raise ValueError(f"File too large: {len(content)} bytes (max: {self.max_file_size} bytes)")
                    return base64.b64encode(content).decode('utf-8')
            except PermissionError:
                raise ValueError(f"Permission denied when accessing image file: {validated_path}")
            except OSError as e:
                raise ValueError(f"Failed to read image file: {e}")
    
    def locate_with_gemini(self, 
                          image_path: str, 
                          context_info: Optional[str] = None, 
                          location_guess: Optional[str] = None) -> Dict[str, Any]:
        """
        Use Gemini API to analyze and geolocate an image with higher accuracy.
        
        Args:
            image_path: Path to the image file or URL
            context_info: Optional additional context about the image
            location_guess: Optional user's guess of the location
            
        Returns:
            Dictionary containing the analysis and location information with structure:
            {
                "interpretation": str,  # Analysis of the image
                "locations": [          # List of possible locations
                    {
                        "country": str,
                        "state": str,
                        "city": str,
                        "confidence": "High"/"Medium"/"Low",
                        "coordinates": {
                            "latitude": float,
                            "longitude": float
                        },
                        "explanation": str
                    }
                ]
            }
            
            On error, returns:
            {
                "error": str,           # Error message
                "details": str,         # Optional details about the error
                "exception": str        # Optional exception information
            }
        """
        # Apply rate limiting
        self._rate_limit()
        
        # Convert image to base64
        try:
            image_base64 = self.encode_image_to_base64(image_path)
            mime_type = self._detect_mime_type(image_path)
        except Exception as e:
            # Sanitize error message to avoid exposing sensitive paths
            error_msg = str(e)
            if "No such file or directory" in error_msg:
                error_msg = "Image file not found"
            elif "Permission denied" in error_msg:
                error_msg = "Permission denied accessing image file"
            return {"error": f"Failed to process image: {error_msg}"}
        
        # Build the prompt
        prompt_text = """You are a professional geolocation expert. You MUST respond with a valid JSON object in the following format:

{
  "interpretation": "A comprehensive analysis of the image, including:
    - Architectural style and period
    - Notable landmarks or distinctive features
    - Natural environment and climate indicators
    - Cultural elements (signage, vehicles, clothing, etc.)
    - Any visible text or language
    - Time period indicators (if any)",
  "locations": [
    {
      "country": "Primary country name",
      "state": "State/region/province name",
      "city": "City name",
      "confidence": "High/Medium/Low",
      "coordinates": {
        "latitude": 12.3456,
        "longitude": 78.9012
      },
      "explanation": "Detailed reasoning for this location identification, including:
        - Specific architectural features that match this location
        - Environmental characteristics that support this location
        - Cultural elements that indicate this region
        - Any distinctive landmarks or features
        - Supporting evidence from visible text or signage"
    }
  ]
}

IMPORTANT: 
1. Your response MUST be a valid JSON object. Do not include any text before or after the JSON object.
2. Do not include any markdown formatting or code blocks.
3. The response should be parseable by JSON.parse().
4. You can provide up to three possible locations if you are not completely confident about a single location.
5. Order the locations by confidence level (highest to lowest).
6. ALWAYS include approximate coordinates (latitude and longitude) for each location when possible.

Consider these key aspects for accurate location identification:
1. Architectural Analysis:
   - Building styles and materials
   - Roof types and construction methods
   - Window and door designs
   - Decorative elements and ornamentation

2. Environmental Indicators:
   - Vegetation types and patterns
   - Climate indicators (snow, desert, tropical, etc.)
   - Terrain and topography
   - Water bodies or coastal features

3. Cultural Context:
   - Language of visible text
   - Vehicle types and styles
   - Clothing and fashion
   - Street furniture and infrastructure
   - Commercial signage and branding

4. Time Period Indicators:
   - Architectural period
   - Vehicle models
   - Fashion styles
   - Technology visible"""

        # Add additional context if provided
        if context_info:
            prompt_text += f"\n\nAdditional context provided by the user:\n{context_info}"
        
        # Add location guess if provided
        if location_guess:
            prompt_text += f"\n\nUser suggests this might be in: {location_guess}"
        
        prompt_text += "\n\nRemember: Your response must be a valid JSON object only. No additional text or formatting."
        
        # Prepare the request body
        request_body = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt_text
                        },
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": image_base64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 2048
            }
        }
        
        # Make the API request with proper headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "GeoSpy/0.1.9 (https://github.com/atiilla/geospy)"
        }
        
        try:
            response = requests.post(
                f"{self.gemini_api_url}?key={self.gemini_api_key}",
                headers=headers,
                json=request_body,
                timeout=self.timeout,
                verify=True  # Verify SSL certificates
            )
            
            if response.status_code != 200:
                # Sanitize error response to avoid exposing sensitive data
                error_details = "API request failed"
                if response.status_code == 401:
                    error_details = "Invalid API key"
                elif response.status_code == 403:
                    error_details = "API access forbidden"
                elif response.status_code == 429:
                    error_details = "Rate limit exceeded"
                elif response.status_code >= 500:
                    error_details = "API server error"
                
                return {
                    "error": f"API request failed with status code {response.status_code}",
                    "details": error_details
                }
            
            data = response.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Strip any markdown formatting and code blocks
            json_string = raw_text.replace("```json", "").replace("```", "").strip()
            
            try:
                parsed_result = json.loads(json_string)
                
                # Handle potential single location format where the location is not in an array
                if "city" in parsed_result and "locations" not in parsed_result:
                    return {
                        "interpretation": parsed_result.get("interpretation", ""),
                        "locations": [{
                            "country": parsed_result.get("country", ""),
                            "state": parsed_result.get("state", ""),
                            "city": parsed_result.get("city", ""),
                            "confidence": parsed_result.get("confidence", "Medium"),
                            "coordinates": parsed_result.get("coordinates", {"latitude": 0, "longitude": 0}),
                            "explanation": parsed_result.get("explanation", "")
                        }]
                    }
                
                return parsed_result
                
            except json.JSONDecodeError as e:
                return {
                    "error": "Failed to parse API response",
                    "details": "Invalid JSON response from API"
                }
        except requests.exceptions.SSLError as e:
            return {
                "error": "SSL verification failed",
                "details": "Could not verify API server certificate"
            }
        except requests.exceptions.Timeout as e:
            return {
                "error": "Request timeout",
                "details": f"Request timed out after {self.timeout} seconds"
            }
        except requests.exceptions.ConnectionError as e:
            return {
                "error": "Connection failed",
                "details": "Could not connect to API server"
            }
        except requests.exceptions.RequestException as e:
            return {
                "error": "API request failed",
                "details": "Network error occurred"
            }
        except Exception as e:
            return {
                "error": "Unexpected error",
                "details": "An unexpected error occurred while processing the request"
            }
            
    def locate(self, image_path: str, context_info: Optional[str] = None, 
              location_guess: Optional[str] = None) -> Dict[str, Any]:
        """
        Locate an image using Gemini API.
        
        Args:
            image_path: Path to the image file or URL
            context_info: Optional additional context about the image
            location_guess: Optional user's guess of the location
            
        Returns:
            Dictionary containing the analysis and location information.
            See locate_with_gemini method for detailed return structure.
            
        Note:
            This is an alias for locate_with_gemini for backward compatibility.
        """
        return self.locate_with_gemini(image_path, context_info, location_guess)