import json
import os

import requests

url_base = "http://0.0.0.0:8081"
U = os.environ.get("email")
P = os.environ.get("password")


# login

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

itemurl = "http://0.0.0.0:8081/events/"
r = requests.get(itemurl, headers=headers, json=query)

print(r.status_code)
print(r.text)

# test limit and paging
query = dict(
    page=0,
    limit=5,
    aoi_id=5,
    start_datetime="2020-03-01",
    end_datetime="2020-07-01",
)

itemurl = "http://0.0.0.0:8081/events/"
r = requests.get(itemurl, headers=headers, json=query)

print("PAGE 0", r.status_code)
print(json.loads(r.text))

query = dict(
    page=1,
    limit=5,
    aoi_id=5,
    start_datetime="2020-03-01",
    end_datetime="2020-07-01",
)

itemurl = "http://0.0.0.0:8081/events/"
r = requests.get(itemurl, headers=headers, json=query)

print("PAGE 1", r.status_code)
print(json.loads(r.text))

# single id
query = dict(
    aoi_id=5,
    start_datetime="2020-03-01",
    end_datetime="2020-07-01",
)

itemurl = "http://0.0.0.0:8081/events/"
r = requests.get(itemurl, headers=headers, json=query)

print("SINGLE ID", r.status_code)
print(json.loads(r.text))


# multiple id
query = dict(
    page=0,
    limit=3,
    aoi_id=5,
    start_datetime="2020-03-01",
    end_datetime="2020-07-01",
)

r = requests.get(itemurl, headers=headers, json=query)

print("MULTUIPLE ID", r.status_code)
print(json.loads(r.text))

# labels
query = dict(
    labels=["ndvi"],
    aoi_id=5,
    start_datetime="2020-03-01",
    end_datetime="2020-07-01",
)

r = requests.get(itemurl, headers=headers, json=query)

print("LABELS ID", r.status_code)
print(json.loads(r.text))

# labels
query = dict(
    aoi_id=5,
    start_datetime="2020-03-01",
    end_datetime="2020-07-01",
)

r = requests.get(itemurl, headers=headers, json=query)

print("MULTILABEL", r.status_code)
print(json.loads(r.text))
