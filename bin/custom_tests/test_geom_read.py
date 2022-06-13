import json
import os

import geopandas as gpd
import requests
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

# test limit and paging
query = {
    "page": 0,
    "limit": 5000,
}

itemurl = "http://0.0.0.0:8081/aoi/"
r = requests.get(itemurl, headers=headers, json=query)

print(r.status_code)
print(r.text)

# test limit and paging
query = dict(page=0, limit=5)

itemurl = "http://0.0.0.0:8081/aoi/"
r = requests.get(itemurl, headers=headers, json=query)

print("PAGE 0", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))

query = dict(page=1, limit=5)

itemurl = "http://0.0.0.0:8081/aoi/"
r = requests.get(itemurl, headers=headers, json=query)

print("PAGE 1", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))

# single id
query = dict(
    id=11,
)

itemurl = "http://0.0.0.0:8081/aoi/"
r = requests.get(itemurl, headers=headers, json=query)

print("SINGLE ID", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))


# multiple id
query = dict(
    page=0,
    limit=3,
    id=[5, 7, 8, 9, 11],
)

itemurl = "http://0.0.0.0:8081/aoi/"
r = requests.get(itemurl, headers=headers, json=query)

print("MULTUIPLE ID", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))

# labels
query = dict(
    labels=["waterbody"],
)

itemurl = "http://0.0.0.0:8081/aoi/"
r = requests.get(itemurl, headers=headers, json=query)

print("LABELS ID", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))

# labels
query = dict(
    labels=["waterbody", "agricultural_area"],
)

itemurl = "http://0.0.0.0:8081/aoi/"
r = requests.get(itemurl, headers=headers, json=query)

print("MULTILABEL", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))


# geometry
shp = geometry.shape(
    {
        "type": "Polygon",
        "coordinates": [
            [
                [31.88232421875, -23.634459770994653],
                [31.9537353515625, -24.089096670083006],
                [32.2119140625, -24.099125826874857],
                [32.22564697265625, -23.647040184548587],
                [31.88232421875, -23.634459770994653],
            ]
        ],
    }
)

query = dict(geometry=geometry.mapping(shp))

r = requests.get(itemurl, headers=headers, json=query)

print("GEOMETRY", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))

# key-value pairs
query = dict(keyed_values={"livestock": "cows"})

r = requests.get(itemurl, headers=headers, json=query)
print("key-value", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))


query = dict(keyed_values={"livestock": "cows", "crop": "maize"})
r = requests.get(itemurl, headers=headers, json=query)
print("MULTI key-value", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))

query = dict(keyed_values={"livestock": None, "crop": "maize"})
r = requests.get(itemurl, headers=headers, json=query)
print("MIXED key-value", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))
