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
        aoi_id=5,
        labels=[random.choice(VALID_EVENT_LABELS)],
        datetime=(
            datetime(2020, 1, 1) + timedelta(days=random.choice(range(500)))
        ).isoformat()[0:10],
        keyed_values={"value": random.random()},
    )
    for ii in range(50)
]

# test for checking label
itemurl = "http://0.0.0.0:8081/events/"
r = requests.post(itemurl, headers=headers, json=events)

print(r.status_code)
print(r.text)
