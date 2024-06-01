import http.client
import mimetypes
from io import BytesIO
import json

class GeoSpy:
    def __init__(self):
        self.connection = http.client.HTTPSConnection("locate-image-7cs5mab6na-uc.a.run.app")

    def send_image_to_server(self, image_path):
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

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

        body = BytesIO()
        boundary = b"--boundary"
        body.write(boundary + b"\r\n")
        body.write(b'Content-Disposition: form-data; name="image"; filename="image.jpg"\r\n')
        body.write(b"Content-Type: " + mimetypes.guess_type("image.jpg")[0].encode() + b"\r\n\r\n")
        body.write(image_data)
        body.write(b"\r\n")
        body.write(boundary + b"--\r\n")

        self.connection.request("POST", "/", body=body.getvalue(), headers=headers)
        response = self.connection.getresponse()
        response_data = response.read().decode()

        if response_data and response.status == 200:
            json_data = json.loads(response_data)
            message = json_data.get("message")
            return message
        else:
            print(f"Status: {response.status} {response.reason}")
            print(f"Service has failed to process the request, please try again.")
            return None

    def country(self, image_path):
        message = self.send_image_to_server(image_path)
        if message:
            return message.split("\n")[0].split(":")[-1].strip()

    def city(self, image_path):
        message = self.send_image_to_server(image_path)
        if message:
            return message.split("\n")[1].split(":")[-1].strip()

    def explanation(self, image_path):
        message = self.send_image_to_server(image_path)
        if message:
            return message.split("\n")[2].split(":")[-1].strip()

    def coordinates(self, image_path):
        message = self.send_image_to_server(image_path)
        if message:
            return message.split("\n")[-1].split(":")[-1].strip().split(",")

    def maps(self, image_path):
        coordinates = self.coordinates(image_path)
        if coordinates:
            latitude, longitude = coordinates
            if "°" in latitude or "°" in longitude:
                latitude_value, latitude_direction = map(str.strip, latitude.split("°"))
                longitude_value, longitude_direction = map(str.strip, longitude.split("°"))
                latitude_sign = 1 if latitude_direction.upper() == "N" else -1
                longitude_sign = 1 if longitude_direction.upper() == "E" else -1
                latitude_float = float(latitude_value) * latitude_sign
                longitude_float = float(longitude_value) * longitude_sign
                return f"https://www.google.com/maps?q={latitude_float},{longitude_float}"
            else:
                return f"https://www.google.com/maps?q={latitude},{longitude}"

    def locate(self, image_path):
        message = self.send_image_to_server(image_path)
        if message:
            result = {
                "country": self.country(image_path),
                "city": self.city(image_path),
                "explanation": self.explanation(image_path),
                "coordinates": self.coordinates(image_path),
                "maps": self.maps(image_path),
            }
            return result