import json
import os

import geopandas as gpd
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

# write a new AOI
itemurl = "http://0.0.0.0:8081/aoi/"

feature = Feature(geometry=shp, properties={"labels": "waterbody"})
r = requests.post(itemurl, headers=headers, json=feature)

print("WRITE NEW AOI")
print(r.status_code)
print(r.text)

_id = json.loads(r.text)["id"]

# change some properties and update
feature = Feature(
    geometry=shp,
    properties={"labels": "waterbody", "my_property": "unique_val"},
    id=_id,
)
r = requests.post(itemurl, headers=headers, json=feature)

print("UPDATE A PROPERTY")
print(r.status_code)
print(r.text)

# check it out
query = dict(page=0, limit=5, id=_id)
r = requests.get(itemurl, headers=headers, json=query)

print("READ THE NEW FT")
print("PAGE 0", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)["features"]))  # single feature

new_shp = geometry.shape(
    {
        "type": "Polygon",
        "coordinates": [
            [
                [76.7779541015625, 22.45],
                [76.56097412109375, 22.3],
                [76.53213500976562, 22.0],
                [76.61453247070312, 21.9],
                [76.93588256835938, 22.2],
                [76.7779541015625, 22.45],
            ]
        ],
    }
)
feature = Feature(
    geometry=new_shp,
    properties={"labels": "waterbody", "my_property": "unique_val"},
    id=_id,
)
r = requests.post(itemurl, headers=headers, json=feature)
print("UPDATE A GEOM")
print(r.status_code)
print(r.text)

# check it out
query = dict(page=0, limit=5, id=_id)
r = requests.get(itemurl, headers=headers, json=query)

print("CHECK GEOM")
print("PAGE 0", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)["features"]))  # single feature

delete_url = "http://0.0.0.0:8081/delete/"
query = dict(id=_id, table="aoi")
r = requests.post(delete_url, headers=headers, json=query)

print("DELETE AOI")
print(r.status_code)
print(r.text)

# check it out
query = dict(page=0, limit=5, id=_id)
r = requests.get(itemurl, headers=headers, json=query)

print("CHECK GEOM")
print("PAGE 0", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)["features"]))  # single feature
