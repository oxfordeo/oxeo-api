import json
import os
import random

import geopandas as gpd
import requests

gdf = gpd.read_file("./data/ag_areas_gaza.geojson")

print(gdf)

# login
authurl = "http://0.0.0.0:8081/auth/token"
U = os.environ.get("email")
P = os.environ.get("password")
r = requests.post(authurl, data={"username": U, "password": P})

print(r.status_code)
print(r.text)

token = json.loads(r.text)["access_token"]

headers = {"Authorization": f"Bearer {token}"}

for feature in gdf.iterfeatures():
    feature["properties"]["labels"] = "agricultural_area"

    if random.random() > 0.5:
        feature["properties"]["livestock"] = random.choice(["cows", "chickens"])
    if random.random() > 0.5:
        feature["properties"]["crop"] = random.choice(["maize", "soy"])

    itemurl = "http://0.0.0.0:8081/aoi/"
    r = requests.post(itemurl, headers=headers, json=feature)

    print(r.status_code)
    print(r.text)
