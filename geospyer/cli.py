import argparse
import http.client
import mimetypes
from io import BytesIO
import json


def display_map(cordinates):
    # Extract latitude and longitude from the coordinates
    latitude, longitude = cordinates
    google_maps_link = ""

    # if latitude or longitude contains '°' or 'N' or 'S' or 'E' or 'W'
    if "°" in latitude or "°" in longitude:
        # Extract numerical values and direction
        latitude_value, latitude_direction = map(str.strip, latitude.split("°"))
        longitude_value, longitude_direction = map(str.strip, longitude.split("°"))

        # Determine the sign for latitude and longitude
        latitude_sign = 1 if latitude_direction.upper() == "N" else -1
        longitude_sign = 1 if longitude_direction.upper() == "E" else -1

        # Convert string values to float
        latitude_float = float(latitude_value) * latitude_sign
        longitude_float = float(longitude_value) * longitude_sign

        # Generate Google Maps link
        google_maps_link = (
            f"https://www.google.com/maps?q={latitude_float},{longitude_float}"
        )

    else:
        # Extract numerical values and direction
        google_maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"

    # Display the Google Maps link
    return f"Google Maps Link: {google_maps_link}"

def send_image_to_server(image_path):
    # Open the image file
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    # Set up connection to the server using HTTPS
    connection = http.client.HTTPSConnection("locate-image-7cs5mab6na-uc.a.run.app")

    # Set the headers, including the custom header
    headers = {
        "Content-Type": "multipart/form-data; boundary=boundary",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,tr;q=0.8,ar;q=0.7",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "Referer": "https://geospy.web.app/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    # Create a multipart/form-data request
    body = BytesIO()
    boundary = b"--boundary"

    # Add image data
    body.write(boundary + b"\r\n")
    body.write(
        b'Content-Disposition: form-data; name="image"; filename="image.jpg"\r\n'
    )
    body.write(
        b"Content-Type: " + mimetypes.guess_type("image.jpg")[0].encode() + b"\r\n\r\n"
    )
    body.write(image_data)
    body.write(b"\r\n")

    # Finalize the request
    body.write(boundary + b"--\r\n")

    # Send the request
    connection.request("POST", "/", body=body.getvalue(), headers=headers)

    # Get the response
    response = connection.getresponse()

    # Print the response status and data
    response_data = response.read().decode()
    # Extract the message from the JSON data
    if response_data and response.status == 200:
        print(f"\033[92mAI found where the picture was taken\033[92m\n")
        json_data = json.loads(response_data)
        message = json_data.get("message")
        coordinates = message.split("\n")[-1].split(":")[-1].strip().split(",")
        print(message.strip())
        print(display_map(coordinates))
    else:
        print(f"Status: {response.status} {response.reason}")
        print(f"Service has failed to process the request, please try again.")

    # Close the connection
    connection.close()


def banner():
    font = """
\033[94m▒█▀▀█ █▀▀ █▀▀█ ▒█▀▀▀█ █▀▀█ █░░█ 
▒█░▄▄ █▀▀ █░░█ ░▀▀▀▄▄ █░░█ █▄▄█ 
▒█▄▄█ ▀▀▀ ▀▀▀▀ ▒█▄▄▄█ █▀▀▀ ▄▄▄█
AI powered geo-location. Uncover the location photos were taken from by harnessing the power of AI
Disclaimer: This application uses Graylark's AI powered geolocation. This application is not affiliated with Graylark and I'm not responsible for the consequences of using this application.
Github: https://github.com/atiilla/geospy
"""
    print(font + "\033[0m")


def main():
    banner()
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, help="image path")
    args = parser.parse_args()

    if args.image:
        send_image_to_server(args.image)

    else:
        print("Please provide an image path using the --image argument.")