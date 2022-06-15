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
create_url = "http://0.0.0.0:8081/companies/"
update_url = "http://0.0.0.0:8081/companies/update/"
delete_url = "http://0.0.0.0:8081/delete/"

# ### SINGLE ASSET ####
print("SINGLE ASSET")
shp = geometry.Point(0.0, 5.0)

data = dict(
    name="big-corp" + "".join([random.choice(string.ascii_letters) for _ in range(5)]),
    properties={"HQ": "Coruscant"},
)

r = requests.post(create_url, headers=headers, json=data)

print(r.status_code)
print(r.text)

_id = json.loads(r.text)["id"]

print("QEURY SINGLE ID")
# single id
query = dict(
    id=_id,
)

r = requests.get(create_url, headers=headers, json=query)

print(json.loads(r.text))

print("QUERY on PROPS")
query = dict(
    name="big-corp",
)

r = requests.get(create_url, headers=headers, json=query)
print(r.status_code)
print(json.loads(r.text))

print("QUERY on PROPS")
query = dict(keyed_values={"HQ": None})

r = requests.get(create_url, headers=headers, json=query)
print(r.status_code)
print(json.loads(r.text))

print("UPDATE")


data = dict(
    id=_id,
    name="big-corp-3",
    properties={"HQ": "Tatooine"},
)


r = requests.post(update_url, headers=headers, json=data)

print(r.status_code)
print(r.text)

# single id
query = dict(
    id=_id,
)

r = requests.get(create_url, headers=headers, json=query)

print("SINGLE ID", r.status_code)
print(json.loads(r.text))

print("DELETE")

query = dict(id=_id, table="company")
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
print(json.loads(r.text))
