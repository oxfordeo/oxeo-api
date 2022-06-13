import json
import os
import random
from datetime import datetime, timedelta

import requests

url_base = "http://0.0.0.0:8081"

VALID_EVENT_LABELS = ("ndvi", "water_extents", "soil_moisture", "prediction")
# login
U = os.environ.get("email")
P = os.environ.get("password")

authurl = "http://0.0.0.0:8081/auth/token"
r = requests.post(authurl, data={"username": U, "password": P})

print(r.status_code)
print(r.text)

token = json.loads(r.text)["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# write some random events

events = [
    dict(
        aoi_id=7,
        labels=["ndvi"],
        datetime=(
            datetime(2020, 1, 1) + timedelta(days=random.choice(range(180)))
        ).isoformat()[0:10],
        keyed_values={"value": random.random()},
    )
    for ii in range(10)
]

# test for checking label
itemurl = "http://0.0.0.0:8081/events/"
r = requests.post(itemurl, headers=headers, json=events)

print("MAKE NEW EVENTS")
print(r.status_code)
print(r.text)
_ids = json.loads(r.text)["id"]
print(_ids)


print("READ EVENTS")
query = dict(
    id=_ids,
    aoi_id=7,
    start_datetime="2020-03-01",
    end_datetime="2020-07-01",
)

r = requests.get(itemurl, headers=headers, json=query)

print("PAGE 0", r.status_code)
print(json.loads(r.text))


events = [
    dict(
        id=_id,
        aoi_id=7,
        labels=["water_extents"],
        datetime=(
            datetime(2020, 1, 1) + timedelta(days=random.choice(range(180)))
        ).isoformat()[0:10],
        keyed_values={"value": random.random() + 5},
    )
    for _id in _ids
]

print("UPDATE EVENTS")
r = requests.post(itemurl, headers=headers, json=events)
print(r.status_code)
print(r.text)


print("READ EVENTS")
query = dict(
    id=_ids,
    aoi_id=7,
    start_datetime="2020-03-01",
    end_datetime="2020-07-01",
)

r = requests.get(itemurl, headers=headers, json=query)

print("PAGE 0", r.status_code)
print(json.loads(r.text))

print("DELETE EVENTS")
delete_url = "http://0.0.0.0:8081/delete/"
query = dict(id=_ids, table="events")
r = requests.post(delete_url, headers=headers, json=query)
print(r.status_code)
print(r.text)


print("READ EVENTS")
query = dict(
    id=_ids,
    aoi_id=7,
    start_datetime="2020-03-01",
    end_datetime="2020-07-01",
)

r = requests.get(itemurl, headers=headers, json=query)

print("PAGE 0", r.status_code)
print(json.loads(r.text))
