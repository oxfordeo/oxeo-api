import json
import os

import requests
from geojson import Feature
from shapely import geometry

url_base = "http://0.0.0.0:8081"


# login
U = os.environ.get("email")
P = os.environ.get("password")

authurl = "http://0.0.0.0:8081/auth/token"
r = requests.post(authurl, data={"username": U, "password": P})

print(r.status_code)
print(r.text)

token = json.loads(r.text)["access_token"]

headers = {"Authorization": f"Bearer {token}"}

shp = geometry.shape(
    {
        "type": "Polygon",
        "coordinates": [
            [
                [76.7779541015625, 22.42499308964722],
                [76.56097412109375, 22.311966810977616],
                [76.53213500976562, 22.055096050575845],
                [76.61453247070312, 21.88061545090571],
                [76.93588256835938, 22.165786064257418],
                [76.7779541015625, 22.42499308964722],
            ]
        ],
    }
)

feature = Feature(geometry=shp, properties={"labels": "meow"})

# test for checking label
itemurl = "http://0.0.0.0:8081/aoi/"
r = requests.post(itemurl, headers=headers, json=feature)

print(r.status_code)
print(r.text)

feature = Feature(geometry=shp, properties={"labels": "waterbody"})

# test for checking label
itemurl = "http://0.0.0.0:8081/aoi/"
r = requests.post(itemurl, headers=headers, json=feature)

print(r.status_code)
print(r.text)
