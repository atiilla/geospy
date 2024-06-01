# geospy

![GitHub](https://img.shields.io/github/license/atiilla/geospy)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/atiilla/geospy)

Python tool using Graylark's AI-powered geo-location service to uncover the location where photos were taken.

![screenshot](screenshot.PNG)

## Installation

```bash
pip install geospyer
```

## Usage

```bash
geospyer --image path/to/your/image.jpg
```

```python
from geospy import GeoSpy

geospy = GeoSpy()
country = geospy.country("image.png")
city = geospy.city("image.png")
explanation = geospy.explanation("image.png")
coordinates = geospy.coordinates("image.png")
maps_link = geospy.maps("image.png")
location_data = geospy.locate("image.png")
print(str(location_data))
```

Replace path/to/your/image.jpg with the actual path to the image you want to analyze.

## Features

- Generate Google Maps links based on image coordinates.

## Disclaimer

This application uses Graylark's AI-powered geolocation. It is not affiliated with Graylark, and the author is not responsible for the consequences of using this application.

## Contributing

1. Fork the repository
2. Create a new branch (git checkout -b feature/new-feature).
3. Commit your changes (git commit -am 'Add new feature').
4. Push to the branch (git push origin feature/new-feature).
5. Create a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Thanks to Graylark](https://graylark.io/) for providing the AI-powered geolocation service.
- [Thanks to @metaltiger775] for transforming the project into a versatile library that can be seamlessly integrated into other codebases!