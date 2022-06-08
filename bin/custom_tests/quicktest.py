import json
import os

import requests

url_base = "http://0.0.0.0:8081"
U = os.environ.get("email")
P = os.environ.get("password")


# create a user
payload = {"email": U, "password": P}
r = requests.post(os.path.join(url_base, "users"), json=payload)

print(r.status_code)
print(r.text)

# login

authurl = "http://0.0.0.0:8081/auth/token"
r = requests.post(authurl, data={"username": U, "password": P})

print(r.status_code)
print(r.text)

token = json.loads(r.text)["access_token"]

headers = {"Authorization": f"Bearer {token}"}

item = {
    "title": "The Doors",
    "description": "Hello I love you wont you tell me your name",
}

itemurl = "http://0.0.0.0:8081/users/items"
r = requests.post(itemurl, headers=headers, json=item)

print(r.status_code)
print(r.text)
