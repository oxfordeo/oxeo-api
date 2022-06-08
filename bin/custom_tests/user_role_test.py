import json
import os

import requests

url_base = "http://0.0.0.0:8081"


# create a user
# payload = {"email": "me@ox.ca", "password": "mypass"}
# r = requests.post(os.path.join(url_base, "users"), json=payload)

# print(r.status_code)
# print(r.text)

# login
U = os.environ.get("email")
P = os.environ.get("password")

authurl = "http://0.0.0.0:8081/auth/token"
r = requests.post(authurl, data={"username": U, "password": P})

print(r.status_code)
print(r.text)

token = json.loads(r.text)["access_token"]

headers = {"Authorization": f"Bearer {token}"}

itemurl = "http://0.0.0.0:8081/users/"
r = requests.get(itemurl, headers=headers)

print(r.status_code)
print(r.text)
