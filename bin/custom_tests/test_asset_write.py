import json
import os
import random
import string

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

r = requests.post(itemurl, headers=headers, json=data)

print(r.status_code)
print(r.text)

# ### SINGLE ASSET ####
print("SINGLE ASSET - FAIL LABEL")
shp = geometry.Point(0.0, 5.0)

data = dict(
    geometry=geometry.mapping(shp),
    name="my-asset-" + "".join([random.choice(string.ascii_letters) for _ in range(5)]),
    labels=[],
    properties={},
    company_weights={"mycompany-1": 100},
)

r = requests.post(itemurl, headers=headers, json=data)

print(r.status_code)
print(r.text)


# ### SINGLE ASSET ####
print("MULTIPLE ASSET")
assets = []
for _ in range(10):
    shp = geometry.Point(random.random() * 10, random.random() * 10)

    data = dict(
        geometry=geometry.mapping(shp),
        name="my-asset-"
        + "".join([random.choice(string.ascii_letters) for _ in range(5)]),  # noqa
        labels=["mine"],
        properties={},
        company_weights={"mycompany-1": 100},
    )

    assets.append(data)

# test for checking label
r = requests.post(itemurl, headers=headers, json=assets)

print(r.status_code)
print(r.text)

print("SINGLE ASSET - MultiCO - FAIL")
shp = geometry.Point(0.0, 5.0)

data = dict(
    geometry=geometry.mapping(shp),
    name="my-asset-" + "".join([random.choice(string.ascii_letters) for _ in range(5)]),
    labels=["mine"],
    properties={},
    company_weights={"mycompany-1": 30, "mycompany-2": 60},
)

r = requests.post(itemurl, headers=headers, json=data)

print(r.status_code)
print(r.text)

print("SINGLE ASSET - MultiCO")
shp = geometry.Point(0.0, 5.0)

data = dict(
    geometry=geometry.mapping(shp),
    name="my-asset-" + "".join([random.choice(string.ascii_letters) for _ in range(5)]),
    labels=["mine"],
    properties={},
    company_weights={"mycompany-1": 30, "mycompany-2": 70},
)

r = requests.post(itemurl, headers=headers, json=data)

print(r.status_code)
print(r.text)
