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
itemurl = "http://0.0.0.0:8081/assets/"

print("PAGE LIMIT FAIL")
# test limit and paging
query = {
    "page": 0,
    "limit": 5000,
}

r = requests.get(itemurl, headers=headers, json=query)

print(r.status_code)
print(r.text)

print("PAGE LIMIT SUCCESS")
# test limit and paging
query = dict(page=0, limit=5)


r = requests.get(itemurl, headers=headers, json=query)

print("PAGE 0", r.status_code)
print(r.text)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))

query = dict(page=1, limit=5)

r = requests.get(itemurl, headers=headers, json=query)

print("PAGE 1", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))

# single id
query = dict(
    id=69,
)

r = requests.get(itemurl, headers=headers, json=query)

print("SINGLE ID", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))


# multiple id
query = dict(
    page=0,
    limit=3,
    id=[60, 65, 67, 68, 69],
)

r = requests.get(itemurl, headers=headers, json=query)

print("MULTUIPLE ID", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))

# labels
print("LABELS ID")
query = dict(
    labels=["mine"],
)

r = requests.get(itemurl, headers=headers, json=query)
print(r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))

print("GEOMETRY")
# geometry
shp = geometry.shape(
    {
        "type": "Polygon",
        "coordinates": [
            [
                [0, 0],
                [0, 10],
                [10, 10],
                [10, 0],
                [0, 0],
            ]
        ],
    }
)

query = dict(geometry=geometry.mapping(shp))

r = requests.get(itemurl, headers=headers, json=query)

print(r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))
