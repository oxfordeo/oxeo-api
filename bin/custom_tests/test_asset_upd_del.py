import json
import os
import random
import string

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
create_url = "http://0.0.0.0:8081/assets/"
update_url = "http://0.0.0.0:8081/assets/update/"

# ### SINGLE ASSET ####
print("SINGLE ASSET")
shp = geometry.Point(0.0, 5.0)

data = dict(
    geometry=geometry.mapping(shp),
    name="my-asset-" + "".join([random.choice(string.ascii_letters) for _ in range(5)]),
    labels=["mine"],
    properties={},
    company_weights={"mycompany-1": 100},
)

r = requests.post(create_url, headers=headers, json=data)

print(r.status_code)
print(r.text)

_id = json.loads(r.text)["id"][0]

# single id
query = dict(
    id=_id,
)

r = requests.get(create_url, headers=headers, json=query)

print("SINGLE ID", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))

ft = json.loads(r.text)["features"][0]
print(ft)

data = dict(
    id=_id,
    geometry=ft["geometry"],
    name=ft["properties"]["name"],
    labels=ft["properties"]["labels"],
    company_weights=ft["properties"]["company_weights"],
    properties={
        kk: vv
        for kk, vv in ft["properties"].items()
        if kk not in ["name", "labels", "company_weights"]
    },
)

data["company_weights"] = {"mycompany-1": 45, "mycompany-3": 55}
data["properties"]["my-key"] = "my-val"
print(data)

r = requests.post(update_url, headers=headers, json=[data])

print(r.status_code)
print(r.text)

# single id
query = dict(
    id=_id,
)

r = requests.get(create_url, headers=headers, json=query)

print("SINGLE ID", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))

ft = json.loads(r.text)["features"][0]
print(ft)

print("DELETE")
delete_url = "http://0.0.0.0:8081/delete/"
query = dict(id=_id, table="asset")
r = requests.post(delete_url, headers=headers, json=query)
print(r.status_code)
print(r.text)

print("READ AGAIN")
# single id
query = dict(
    id=_id,
)

r = requests.get(create_url, headers=headers, json=query)

print("SINGLE ID", r.status_code)
print(gpd.GeoDataFrame.from_features(json.loads(r.text)))

ft = json.loads(r.text)["features"][0]
print(ft)
